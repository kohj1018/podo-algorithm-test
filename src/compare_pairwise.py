"""Stage 8: pairwise comparison for the top-K jobs, with A/B and B/A order swap."""
from __future__ import annotations

import json
from typing import Dict, List

from . import config, llm
from .models import CONF_RANK, MatchingTable, PairwiseResult, clamp, CONFIDENCES
from .rerank_listwise import compress_table

_RANK_TO_CONF = {0: "low", 1: "medium", 2: "high"}


def _compare_once(comp_a: dict, comp_b: dict, label: str) -> dict:
    prompt = config.render(
        config.load_prompt("pairwise_compare"),
        JOB_A=json.dumps(comp_a, ensure_ascii=False, indent=2),
        JOB_B=json.dumps(comp_b, ensure_ascii=False, indent=2),
    )

    def validate(obj) -> dict:
        if not isinstance(obj, dict):
            raise ValueError("expected a JSON object")
        return {
            "winner": clamp(obj.get("winner"), {"a", "b", "tie"}, "tie"),
            "confidence": clamp(obj.get("confidence"), CONFIDENCES, "low"),
            "reason": (obj.get("reason") or "").strip()[:400],
        }

    return llm.call_structured(llm.JSON_SYSTEM, prompt, validate, max_tokens=800, cache_label=label)


def run_pairwise(tables: List[MatchingTable], candidate_ids: List[str],
                 domain_ctx: Dict[str, dict] = None) -> List[PairwiseResult]:
    """Compare all pairs among the given candidate_ids (A/B and B/A)."""
    domain_ctx = domain_ctx or {}
    comp: Dict[str, dict] = {t.job_id: compress_table(t, domain_ctx.get(t.job_id)) for t in tables}
    ids = [jid for jid in candidate_ids if jid in comp]
    results: List[PairwiseResult] = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            r_ab = _compare_once(comp[a], comp[b], f"pair_{a}_vs_{b}")  # winner: a->A(=a), b->B(=b)
            r_ba = _compare_once(comp[b], comp[a], f"pair_{b}_vs_{a}")  # winner: a->A(=b), b->B(=a)

            ab_winner = a if r_ab["winner"] == "a" else (b if r_ab["winner"] == "b" else "tie")
            ba_winner = b if r_ba["winner"] == "a" else (a if r_ba["winner"] == "b" else "tie")

            agreed = ab_winner != "tie" and ab_winner == ba_winner
            if agreed:
                outcome = ab_winner
                conf_rank = min(CONF_RANK[r_ab["confidence"]], CONF_RANK[r_ba["confidence"]])
                confidence = _RANK_TO_CONF[conf_rank]
            else:
                # disagreement under order swap -> treat as tie / low confidence
                outcome = "tie"
                confidence = "low"

            results.append(PairwiseResult(
                job_a=a, job_b=b,
                ab_winner=ab_winner, ba_winner=ba_winner,
                agreed=agreed, outcome=outcome, confidence=confidence,
                reason_ab=r_ab["reason"], reason_ba=r_ba["reason"],
            ))
    return results
