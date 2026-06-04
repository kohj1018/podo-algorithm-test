"""Stage 7: LLM listwise reranker over COMPRESSED matching tables (fit only)."""
from __future__ import annotations

import json
from typing import Dict, List

from . import config, llm
from .models import CORE_NATURES, MatchingTable


def compress_table(table: MatchingTable, ctx: dict = None) -> dict:
    """Compact, fit-only summary of a matching table (no raw JD/resume text).

    Gaps are split by nature: CORE (technical/domain/experience_level/language) gaps matter for
    ranking; behavioral gaps are listed separately and should mostly affect explanation.
    """
    ctx = ctx or {}
    counts: Dict[str, Dict[str, int]] = {}
    strong: List[str] = []
    core_gaps: List[str] = []
    behavioral_gaps: List[str] = []
    pref_tech_gaps: List[str] = []
    invalid: List[str] = []
    risks: List[str] = []
    product_duties: List[str] = []
    for row in table.rows:
        counts.setdefault(row.requirement_type, {"direct": 0, "adjacent": 0, "weak": 0, "missing": 0})
        counts[row.requirement_type][row.match_level] += 1
        is_core = row.requirement_nature in CORE_NATURES
        is_prereq = row.prerequisite_status == "prerequisite"
        unmet = row.match_level in ("missing", "weak")
        if row.match_level == "direct" and row.confidence in ("high", "medium") and not row.invalid_match:
            strong.append(row.requirement_text)
        if row.requirement_type in ("critical", "required") and unmet:
            tag = f"[{row.requirement_type}/{row.requirement_nature}/{row.match_level}] {row.requirement_text}"
            if is_prereq:
                core_gaps.append(tag)               # real prerequisite gaps (these matter)
            elif row.prerequisite_status == "behavioral_preference":
                behavioral_gaps.append(tag)
            else:                                    # product_duty / context — NOT a prerequisite gap
                product_duties.append(tag)
        if row.requirement_type in ("preferred", "optional") and is_core and is_prereq and unmet:
            pref_tech_gaps.append(f"[{row.requirement_type}/{row.requirement_nature}/{row.match_level}] {row.requirement_text}")
        if row.invalid_match:
            invalid.append(row.requirement_text)
        note = (row.risk_note or row.verifier_note or "").strip()
        if note:
            risks.append(note)
    return {
        "job_id": table.job_id,
        "company": table.company,
        "title": table.title,
        "role_family": ctx.get("role_family"),
        "domain_alignment": ctx.get("domain_alignment"),
        "domain_alignment_reason": ctx.get("domain_alignment_reason"),
        "match_counts_by_type": counts,
        "strong_direct_matches": strong[:6],
        "core_prerequisite_gaps": core_gaps[:8],
        "preferred_technical_gaps": pref_tech_gaps[:6],
        "behavioral_gaps": behavioral_gaps[:4],
        "product_duty_gaps_not_blocking": product_duties[:6],
        "invalid_matches": invalid[:6],
        "risks": risks[:6],
    }


_DOM_RANK = {"strong": 3, "adjacent": 2, "weak": 1, "mismatch": 0}


def _ask_listwise(prompt: str, all_ids: List[str], cache_label: str) -> dict:
    """One listwise call. Returns deduped valid ordering + the duplicate ids it dropped."""
    def validate(obj) -> dict:
        ranking = obj.get("ranking") if isinstance(obj, dict) else None
        if not isinstance(ranking, list) or not ranking:
            raise ValueError("expected a non-empty 'ranking' list")
        ordered, seen, dups = [], set(), []
        for r in ranking:
            jid = r.get("job_id") if isinstance(r, dict) else None
            if jid not in all_ids:
                continue
            if jid in seen:
                dups.append(jid)
                continue
            seen.add(jid)
            ordered.append({"job_id": jid, "reason": (r.get("reason") or "").strip()})
        return {"ordered": ordered, "dups": dups,
                "uncertainty": (obj.get("uncertainty_notes") or "").strip()}

    return llm.call_structured(llm.JSON_SYSTEM, prompt, validate, max_tokens=3000, cache_label=cache_label)


def listwise_rank(tables: List[MatchingTable], domain_ctx: Dict[str, dict] = None,
                  fits: Dict[str, dict] = None) -> dict:
    domain_ctx = domain_ctx or {}
    fits = fits or {}
    compressed = [compress_table(t, domain_ctx.get(t.job_id)) for t in tables]
    all_ids = [t.job_id for t in tables]
    base = config.render(config.load_prompt("listwise_rerank"),
                         JOBS=json.dumps(compressed, ensure_ascii=False, indent=2))
    warnings: dict = {}

    res = _ask_listwise(base, all_ids, "listwise")
    ordered, uncertainty = res["ordered"], res["uncertainty"]
    if res["dups"]:
        warnings["duplicates_first_pass"] = res["dups"]
    present = {x["job_id"] for x in ordered}
    missing = [j for j in all_ids if j not in present]

    if missing:
        warnings["omitted_first_pass"] = missing
        retry_prompt = base + (
            f"\n\n중요: 직전 응답에서 다음 job_id가 누락되었습니다: {missing}. "
            "모든 입력 job_id를 정확히 한 번씩 포함하는 완전한 순위를 반환하세요.")
        try:
            res2 = _ask_listwise(retry_prompt, all_ids, "listwise_retry")
            if len({x["job_id"] for x in res2["ordered"]}) >= len(present):
                ordered = res2["ordered"]
                if res2["dups"]:
                    warnings["duplicates_retry"] = res2["dups"]
        except llm.LLMError:
            pass
        present = {x["job_id"] for x in ordered}
        still = [j for j in all_ids if j not in present]
        if still:
            warnings["omitted_after_retry_placed_by_fit"] = still

            def key(jid):
                f = fits.get(jid, {}).get("level", 1)
                return (f, _DOM_RANK.get(domain_ctx.get(jid, {}).get("domain_alignment", "weak"), 1))

            for jid in still:  # fit-aware placement (NOT appended blindly at the end)
                k = key(jid)
                pos = len(ordered)
                for idx, item in enumerate(ordered):
                    if key(item["job_id"]) < k:
                        pos = idx
                        break
                ordered.insert(pos, {"job_id": jid,
                                     "reason": "(listwise 누락 → fit/domain 기준 안전 배치)"})

    return {"ranking": ordered, "uncertainty_notes": uncertainty,
            "compressed": compressed, "warnings": warnings}
