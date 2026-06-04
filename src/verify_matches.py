"""Stage 6: verify matches.

Two layers:
  1) Deterministic extractive check — every evidence quote must actually appear in the
     resume text (or in a parsed evidence item). Non-extractive quotes are dropped and the
     row is downgraded. This guarantees the "every quote is extractive" hard rule.
  2) Conservative LLM verifier — re-judges each row and may only LOWER match_level.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List

from . import config, llm
from .models import (
    CONF_RANK,
    MATCH_SEVERITY,
    SEVERITY_TO_LEVEL,
    EvidenceItem,
    MatchingTable,
    MatchRow,
    clamp,
    CONFIDENCES,
    MATCH_LEVELS,
)

MAX_RESUME_CHARS = 9000


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def _build_haystack(resume_text: str, evidence: List[EvidenceItem]) -> List[str]:
    hay = [_norm(resume_text)]
    for e in evidence:
        if e.exact_quote:
            hay.append(_norm(e.exact_quote))
        if e.normalized_summary:
            hay.append(_norm(e.normalized_summary))
    return [h for h in hay if h]


def _is_extractive(quote: str, haystack: List[str]) -> bool:
    qn = _norm(quote)
    if not qn:
        return False
    return any(qn in h for h in haystack)


def _extractive_pass(table: MatchingTable, resume_text: str, evidence: List[EvidenceItem]) -> None:
    haystack = _build_haystack(resume_text, evidence)
    for row in table.rows:
        original_count = len(row.evidence_quotes)
        claimed_support = original_count > 0 or bool(row.matched_evidence_ids)
        valid = [q for q in row.evidence_quotes if _is_extractive(q, haystack)]
        removed = original_count - len(valid)
        row.evidence_quotes = valid
        row.extractive_ok = removed == 0
        if removed > 0:
            row.risk_note = (row.risk_note + f" [{removed}개 비추출(non-extractive) 인용 제거됨]").strip()

        # A row that ASSERTED support but has zero extractive quotes is an invalid match.
        if claimed_support and not valid:
            row.invalid_match = True
            row.matched_evidence_ids = []  # #8: clear unsupported evidence ids
            row.downgraded = True
            if row.match_level in ("direct", "adjacent"):
                row.match_level = "weak"
            elif row.match_level == "weak":
                row.match_level = "missing"
            row.confidence = "low"
            row.risk_note = (row.risk_note + " [invalid_match: 이력서에서 추출 가능한 근거 인용을 찾지 못해 강등]").strip()


def _apply_verifier(row: MatchRow, v: dict) -> None:
    cur_sev = MATCH_SEVERITY.get(row.match_level, 0)
    v_level = clamp(v.get("match_level"), MATCH_LEVELS, row.match_level)
    v_sev = MATCH_SEVERITY.get(v_level, cur_sev)
    new_sev = min(cur_sev, v_sev)  # verifier may only lower
    if (v.get("downgrade") or v.get("exaggerated")) and new_sev > 0:
        new_sev -= 1
    if new_sev != cur_sev:
        row.downgraded = True
    row.match_level = SEVERITY_TO_LEVEL[new_sev]

    # confidence: take the lower of current and verifier's, and cap when downgraded
    v_conf = clamp(v.get("confidence"), CONFIDENCES, row.confidence)
    if CONF_RANK[v_conf] < CONF_RANK[row.confidence]:
        row.confidence = v_conf
    if row.downgraded and CONF_RANK[row.confidence] > CONF_RANK["medium"]:
        row.confidence = "medium"
    if row.match_level == "missing":
        row.confidence = "low"

    note = (v.get("verifier_note") or "").strip()
    if note:
        row.verifier_note = note


def _evidence_payload(evidence: List[EvidenceItem]) -> str:
    return json.dumps([{
        "evidence_id": e.evidence_id,
        "title": e.title,
        "source_section": e.source_section,
        "evidence_type": e.evidence_type,
        "strength": e.strength,
        "recency": e.recency,
        "exact_quote": e.exact_quote,
    } for e in evidence], ensure_ascii=False, indent=2)


def _llm_verify(table: MatchingTable, resume_text: str, evidence: List[EvidenceItem]) -> None:
    matches_payload = json.dumps([{
        "requirement_id": r.requirement_id,
        "requirement_text": r.requirement_text,
        "requirement_type": r.requirement_type,
        "requirement_nature": r.requirement_nature,
        "prerequisite_status": r.prerequisite_status,
        "alternatives": r.alternatives,
        "requirement_category": r.requirement_category,
        "alternative_match_policy": r.alternative_match_policy,
        "match_level": r.match_level,
        "confidence": r.confidence,
        "matched_evidence_ids": r.matched_evidence_ids,
        "evidence_quotes": r.evidence_quotes,
        "explanation": r.explanation,
    } for r in table.rows], ensure_ascii=False, indent=2)

    prompt = config.render(
        config.load_prompt("match_verifier"),
        RESUME_TEXT=resume_text[:MAX_RESUME_CHARS],
        EVIDENCE=_evidence_payload(evidence),
        MATCHES=matches_payload,
    )

    def validate(obj) -> Dict[str, dict]:
        items = obj.get("verified") if isinstance(obj, dict) else obj
        if not isinstance(items, list):
            raise ValueError("expected a 'verified' list")
        return {it["requirement_id"]: it for it in items if isinstance(it, dict) and it.get("requirement_id")}

    verdicts = llm.call_structured(llm.JSON_SYSTEM, prompt, validate, max_tokens=10000,
                                   cache_label=f"verify_{table.job_id}")
    for row in table.rows:
        v = verdicts.get(row.requirement_id)
        if v:
            _apply_verifier(row, v)


def verify_table(table: MatchingTable, resume_text: str, evidence: List[EvidenceItem]) -> MatchingTable:
    _extractive_pass(table, resume_text, evidence)
    _llm_verify(table, resume_text, evidence)
    return table
