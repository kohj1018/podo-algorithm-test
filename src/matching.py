"""Stage 5: build a requirement -> evidence matching table for one JD.

The matcher selects evidence by `evidence_id` only; the CODE fills `evidence_quotes`
verbatim from the selected evidence items' `exact_quote`. This guarantees quotes are
extractive by construction (no LLM-paraphrased quotes to be stripped later). Rows that
claim a match but resolve to no usable evidence get one targeted re-match retry.
"""
from __future__ import annotations

import json
from typing import Dict, List

from . import config, llm
from .models import (
    CONFIDENCES,
    MATCH_LEVELS,
    EvidenceItem,
    JobPosting,
    MatchingTable,
    MatchRow,
    as_list,
    clamp,
)


def _evidence_payload(evidence: List[EvidenceItem]) -> str:
    items = [{
        "evidence_id": e.evidence_id,
        "title": e.title,
        "exact_quote": e.exact_quote,
        "normalized_summary": e.normalized_summary,
        "skills": e.skills,
        "evidence_type": e.evidence_type,
        "strength": e.strength,
        "recency": e.recency,
    } for e in evidence]
    return json.dumps(items, ensure_ascii=False, indent=2)


def _requirements_payload(job: JobPosting) -> str:
    reqs = [{
        "requirement_id": r.requirement_id,
        "requirement_text": r.requirement_text,
        "requirement_type": r.requirement_type,
        "requirement_nature": r.requirement_nature,
        "prerequisite_status": r.prerequisite_status,
        "alternatives": r.alternatives,
        "requirement_category": r.requirement_category,
        "alternative_match_policy": r.alternative_match_policy,
    } for r in job.all_requirements()]
    return json.dumps(reqs, ensure_ascii=False, indent=2)


GROUP_CATEGORIES = {"state_management", "styling", "data_fetching", "build_tooling", "testing",
                    "framework", "language"}


def _resolve_evidence(row: MatchRow, evidence_by_id: Dict[str, EvidenceItem]) -> bool:
    """Validate matched_evidence_ids and fill quotes/sources from the evidence items.
    Discards non-existent ids. Returns True if the row now has at least one valid evidence id."""
    valid, bad = [], []
    for eid in row.matched_evidence_ids:
        (valid if eid in evidence_by_id else bad).append(eid)
    row.matched_evidence_ids = valid
    # Quotes are copied verbatim from the parsed evidence — always extractive by construction.
    row.evidence_quotes = [evidence_by_id[eid].exact_quote for eid in valid if evidence_by_id[eid].exact_quote]
    row.evidence_source_sections = [evidence_by_id[eid].source_section for eid in valid
                                    if evidence_by_id[eid].source_section]
    if bad:
        row.risk_note = (row.risk_note + f" [존재하지 않는 evidence_id 무시: {bad}]").strip()
    return bool(valid)


def _needs_rematch(row: MatchRow, has_valid: bool) -> bool:
    """Decide whether to run a targeted re-match retry for this row."""
    if has_valid:
        return False
    # (a) the matcher CLAIMED a match but resolved to no usable evidence (over-claim / paraphrase)
    if row.match_level in ("direct", "adjacent", "weak"):
        return True
    # (b) a critical/required SAME-CATEGORY group came back missing — likely a false negative
    grouped = bool(row.alternatives) or row.requirement_category in GROUP_CATEGORIES
    return (row.requirement_type in ("critical", "required")
            and row.match_level in ("missing", "weak") and grouped)


def _rematch(job_id: str, row: MatchRow, evidence: List[EvidenceItem]) -> dict:
    """Targeted second-pass match for ONE requirement: choose evidence_id(s) only."""
    prompt = config.render(
        config.load_prompt("rematch_evidence"),
        REQUIREMENT_TEXT=row.requirement_text,
        REQUIREMENT_TYPE=row.requirement_type,
        REQUIREMENT_NATURE=row.requirement_nature,
        ALTERNATIVES=json.dumps(row.alternatives, ensure_ascii=False),
        EVIDENCE=_evidence_payload(evidence),
    )

    def validate(obj) -> dict:
        if not isinstance(obj, dict):
            raise ValueError("expected a JSON object")
        return {
            "ids": as_list(obj.get("matched_evidence_ids")),
            "match_level": clamp(obj.get("match_level"), MATCH_LEVELS, row.match_level),
            "confidence": clamp(obj.get("confidence"), CONFIDENCES, "low"),
            "explanation": (obj.get("explanation") or "").strip(),
        }

    return llm.call_structured(llm.JSON_SYSTEM, prompt, validate, max_tokens=2000,
                               cache_label=f"rematch_{job_id}_{row.requirement_id}")


def build_matching_table(job: JobPosting, evidence: List[EvidenceItem]) -> MatchingTable:
    all_reqs = job.all_requirements()
    evidence_by_id = {e.evidence_id: e for e in evidence}
    prompt = config.render(
        config.load_prompt("requirement_evidence_match"),
        COMPANY=job.company,
        TITLE=job.title,
        REQUIREMENTS=_requirements_payload(job),
        EVIDENCE=_evidence_payload(evidence),
    )

    def validate(obj) -> List[MatchRow]:
        rows_raw = obj.get("matches") if isinstance(obj, dict) else obj
        if not isinstance(rows_raw, list):
            raise ValueError("expected a 'matches' list")
        rows = [MatchRow(**r) for r in rows_raw if isinstance(r, dict)]
        if not rows:
            raise ValueError("no match rows parsed")
        return rows

    # AI/ML-style roles have many requirements; gpt-5 reasoning tokens eat the budget, so keep headroom.
    rows = llm.call_structured(llm.JSON_SYSTEM, prompt, validate, max_tokens=16000,
                               cache_label=f"match_{job.job_id}")

    # Ensure exactly one row per requirement; backfill any the model dropped + authoritative metadata.
    by_id = {r.requirement_id: r for r in rows}
    final_rows: List[MatchRow] = []
    for req in all_reqs:
        row = by_id.get(req.requirement_id) or MatchRow(
            requirement_id=req.requirement_id, match_level="missing", confidence="low",
            explanation="모델이 이 요구사항에 대한 매칭을 반환하지 않아 missing 처리함.")
        row.requirement_text = req.requirement_text
        row.requirement_type = req.requirement_type
        row.requirement_nature = req.requirement_nature
        row.requirement_origin = req.requirement_origin
        row.prerequisite_status = req.prerequisite_status
        row.alternatives = req.alternatives
        row.requirement_category = req.requirement_category
        row.alternative_match_policy = req.alternative_match_policy
        final_rows.append(row)

    # Resolve evidence ids -> verbatim quotes. One targeted re-match retry per row that either
    # (a) claimed a match but resolved to nothing, or (b) is a missing/weak critical/required group.
    for row in final_rows:
        has_valid = _resolve_evidence(row, evidence_by_id)
        if not _needs_rematch(row, has_valid):
            continue
        over_claim = row.match_level in ("direct", "adjacent", "weak")  # vs. a missing-group false-negative check
        res = None
        try:
            res = _rematch(job.job_id, row, evidence)
        except llm.LLMError:
            res = None
        if res and res["ids"]:
            row.matched_evidence_ids = res["ids"]
            row.match_level = res["match_level"]
            row.confidence = res["confidence"]
            row.rematched = True
            if res["explanation"]:
                row.explanation = (row.explanation + " | 재매칭: " + res["explanation"]).strip(" |")
        if not _resolve_evidence(row, evidence_by_id):
            # retry found no usable evidence
            row.match_level = "missing"
            row.confidence = "low"
            if over_claim:
                # the matcher had asserted a match it could not support -> flag it
                row.invalid_match = True
                row.risk_note = (row.risk_note + " [재매칭 후에도 유효 근거 없음 → missing 처리]").strip()
            else:
                # a genuine miss confirmed by the false-negative recheck (not an over-claim)
                row.risk_note = (row.risk_note + " [그룹 재확인: 근거 없음(genuine miss)]").strip()

    return MatchingTable(job_id=job.job_id, company=job.company, title=job.title, rows=final_rows)
