"""Stage 9 + 10: aggregate pairwise results (Bradley-Terry) and assign 1-5 fit levels.

The Bradley-Terry score is a RELATIVE fit-strength score among the compared jobs.
It is NOT a pass/acceptance probability. The 1-5 fit level is derived separately and
conservatively from verified requirement coverage.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .models import (
    CORE_NATURES,
    FIT_LABELS,
    ROLE_FAMILY_TO_DOMAINS,
    FitResult,
    JobPosting,
    MatchingTable,
    PairwiseResult,
)

# requirement-type weights and match-level credit (used only for the 1-5 level, never shown as %)
TYPE_WEIGHT = {"critical": 3.0, "required": 2.0, "preferred": 1.0, "optional": 0.5}
LEVEL_CREDIT = {"direct": 1.0, "adjacent": 0.6, "weak": 0.3, "missing": 0.0}
# Weight by prerequisite status: only true prerequisites carry full weight. Product duties /
# context barely count, behavioral preferences count a little — so they cannot dominate fit.
STATUS_WEIGHT = {
    "prerequisite": 1.0, "behavioral_preference": 0.4, "product_duty": 0.15, "context": 0.1,
}
# Visible domain-distance ceiling on the 1-5 fit level (not a hidden penalty; shown in report).
# "mismatch" is handled dynamically in compute_fit (1 if no core evidence, else 2).
DOMAIN_CAP = {"strong": 5, "adjacent": 4, "weak": 3, "mismatch": 2}
# Interchangeable tooling categories — a gap here is "minor/tooling", NOT a role-defining gap.
MINOR_CATEGORIES = {"state_management", "styling", "data_fetching", "build_tooling", "testing"}


def domain_alignment(role_family: str, primary, secondary):
    """Return (alignment, reason) comparing a JD role_family to the user's domain profile."""
    primary = {d.lower() for d in primary}
    secondary = {d.lower() for d in secondary}
    tokens = ROLE_FAMILY_TO_DOMAINS.get(role_family, {role_family})
    if tokens & primary:
        return "strong", f"role_family '{role_family}'가 사용자 주력 도메인({sorted(primary)})과 직접 일치"
    if tokens & secondary:
        return "adjacent", f"role_family '{role_family}'가 사용자 보조 도메인({sorted(secondary)})과 인접 (주력 아님)"
    if role_family in {"marketing", "design", "product"}:
        return "mismatch", f"role_family '{role_family}'는 사용자 엔지니어링 도메인과 불일치"
    return "weak", f"role_family '{role_family}'가 사용자 도메인과 약하게만 관련됨"


# --------------------------------------------------------------------------- Bradley-Terry
def bradley_terry(ids: List[str], results: List[PairwiseResult],
                  iters: int = 300, prior: float = 0.5) -> Dict[str, float]:
    """Iterative MM estimate of Bradley-Terry strengths. Pure python, no scipy.

    A small symmetric `prior` of split games keeps the comparison graph connected so the
    iteration always converges, even with few/disagreeing pairs.
    """
    n = len(ids)
    if n == 0:
        return {}
    if n == 1:
        return {ids[0]: 1.0}
    idx = {jid: i for i, jid in enumerate(ids)}
    wins = [[0.0] * n for _ in range(n)]  # wins[i][j] = (fractional) wins of i over j
    for r in results:
        if r.job_a not in idx or r.job_b not in idx:
            continue
        i, j = idx[r.job_a], idx[r.job_b]
        if r.outcome == r.job_a:
            wins[i][j] += 1.0
        elif r.outcome == r.job_b:
            wins[j][i] += 1.0
        else:  # tie
            wins[i][j] += 0.5
            wins[j][i] += 0.5
    for i in range(n):
        for j in range(n):
            if i != j:
                wins[i][j] += prior

    total_wins = [sum(wins[i]) for i in range(n)]
    p = [1.0] * n
    for _ in range(iters):
        new_p = [0.0] * n
        for i in range(n):
            denom = 0.0
            for j in range(n):
                if i == j:
                    continue
                games = wins[i][j] + wins[j][i]
                denom += games / (p[i] + p[j])
            new_p[i] = (total_wins[i] / denom) if denom > 0 else p[i]
        s = sum(new_p)
        if s > 0:
            new_p = [x * n / s for x in new_p]  # normalize mean strength to 1
        if max(abs(new_p[i] - p[i]) for i in range(n)) < 1e-9:
            p = new_p
            break
        p = new_p
    return {ids[i]: p[i] for i in range(n)}


def elo(ids: List[str], results: List[PairwiseResult], k: float = 32.0) -> Dict[str, float]:
    """Optional Elo-style fallback aggregation."""
    rating = {jid: 1500.0 for jid in ids}
    for r in results:
        if r.job_a not in rating or r.job_b not in rating:
            continue
        a, b = r.job_a, r.job_b
        ea = 1.0 / (1.0 + 10 ** ((rating[b] - rating[a]) / 400.0))
        if r.outcome == a:
            sa = 1.0
        elif r.outcome == b:
            sa = 0.0
        else:
            sa = 0.5
        rating[a] += k * (sa - ea)
        rating[b] += k * ((1 - sa) - (1 - ea))
    return rating


# --------------------------------------------------------------------------- 1-5 fit level
def compute_fit(table: MatchingTable, alignment: str = "weak") -> dict:
    """Derive a 1-5 fit level. CORE (technical/domain/experience_level/language) gaps drive
    caps; behavioral gaps are de-weighted and do not cap. A visible domain-distance cap is
    applied last. The returned numbers are fit metrics, never pass probability / percentages.
    """
    earned = total = 0.0
    prereq_crit_unmet = prereq_req_unmet = 0
    prereq_crit_total = prereq_req_total = 0
    role_defining_crit_unmet = role_defining_req_unmet = 0  # unmet gaps that are NOT minor/tooling
    role_evidence = 0  # direct/adjacent on a CORE-nature PREREQUISITE critical/required req
    crit_total = crit_met = req_total = req_met = 0
    strong: List[str] = []
    weak: List[str] = []            # unmet PREREQUISITE critical/required gaps (drive caps + ranking)
    pref_gaps: List[str] = []       # unmet preferred/optional core prerequisite gaps (e.g. AOSP/C++)
    product_duties: List[str] = []  # critical/required items that are product duties, NOT prerequisites
    invalid: List[str] = []
    risks: List[str] = []
    for row in table.rows:
        # Weight by type AND by prerequisite status, so product duties / context / behavioral
        # preferences cannot dominate the score.
        w = TYPE_WEIGHT.get(row.requirement_type, 1.0) * STATUS_WEIGHT.get(row.prerequisite_status, 0.7)
        credit = LEVEL_CREDIT.get(row.match_level, 0.0)
        if row.confidence == "low":
            credit *= 0.7
        total += w
        earned += w * credit

        is_core = row.requirement_nature in CORE_NATURES
        is_prereq = row.prerequisite_status == "prerequisite"
        unmet = row.match_level in ("missing", "weak")

        # Real role evidence = direct/adjacent on a CORE-nature PREREQUISITE critical/required req.
        if (row.requirement_type in ("critical", "required") and is_prereq and is_core
                and row.match_level in ("direct", "adjacent") and not row.invalid_match):
            role_evidence += 1
        is_minor = row.requirement_category in MINOR_CATEGORIES  # tooling group gap = minor
        if row.requirement_type == "critical":
            crit_total += 1
            if not unmet:
                crit_met += 1
            if is_prereq:
                prereq_crit_total += 1
                if unmet:
                    prereq_crit_unmet += 1
                    if not is_minor:
                        role_defining_crit_unmet += 1
        if row.requirement_type == "required":
            req_total += 1
            if not unmet:
                req_met += 1
            if is_prereq:
                prereq_req_total += 1
                if unmet:
                    prereq_req_unmet += 1
                    if not is_minor:
                        role_defining_req_unmet += 1

        if row.match_level == "direct" and row.confidence in ("high", "medium") and not row.invalid_match:
            strong.append(row.requirement_text)
        if row.requirement_type in ("critical", "required") and unmet:
            tag = f"[{row.requirement_type}/{row.requirement_nature}/{row.match_level}] {row.requirement_text}"
            if is_prereq:
                weak.append(tag)                       # only PREREQUISITE gaps are real gaps
            elif row.prerequisite_status in ("product_duty", "context"):
                product_duties.append(tag)             # on-the-job duty, not a candidate gap
        if row.requirement_type in ("preferred", "optional") and is_core and is_prereq and unmet:
            pref_gaps.append(f"[{row.requirement_type}/{row.requirement_nature}/{row.match_level}] {row.requirement_text}")
        if row.invalid_match:
            invalid.append(row.requirement_text)
        note = (row.risk_note or row.verifier_note or "").strip()
        if note:
            risks.append(note)

    ratio = earned / total if total > 0 else 0.0
    if ratio >= 0.80:
        level = 5
    elif ratio >= 0.62:
        level = 4
    elif ratio >= 0.42:
        level = 3
    elif ratio >= 0.22:
        level = 2
    else:
        level = 1

    # Coverage-aware caps from unmet PREREQUISITES (product duties / context / behavioral never cap).
    # Role-defining gaps (e.g. React/Kotlin/security) cap harshly; minor/tooling gaps
    # (state/styling/data_fetching/build/testing) do NOT cap a well-covered role below 4.
    crit_ratio = (prereq_crit_total - prereq_crit_unmet) / prereq_crit_total if prereq_crit_total else 1.0
    cap_reasons = []
    role_defining_gap = (role_defining_crit_unmet > 0) or (role_defining_req_unmet > 0)

    if role_defining_crit_unmet >= 2:
        level = min(level, 2); cap_reasons.append(f"role-defining critical gaps x{role_defining_crit_unmet}")
    elif role_defining_crit_unmet == 1:
        level = min(level, 3); cap_reasons.append("role-defining critical gap")
    elif prereq_crit_unmet > 0:
        # only minor/tooling critical gaps remain
        if crit_ratio >= 0.8:
            level = min(level, 4); cap_reasons.append("minor critical (tooling) gap, criticals ≥80% met → max 4")
        else:
            level = min(level, 3); cap_reasons.append("critical gaps <80% met → max 3")

    if role_defining_req_unmet >= 2:
        level = min(level, 2); cap_reasons.append(f"role-defining required gaps x{role_defining_req_unmet}")
    elif role_defining_req_unmet == 1:
        level = min(level, 3); cap_reasons.append("role-defining required gap")
    # minor/tooling required gaps don't add a hard cap — they already lower the coverage ratio.

    # visible domain-distance cap. mismatch is dynamic: cap 1 if there is NO real role evidence
    # (no direct/adjacent on a core prerequisite critical/required req), else cap 2.
    if alignment == "mismatch":
        domain_cap = 2 if role_evidence > 0 else 1
    else:
        domain_cap = DOMAIN_CAP.get(alignment, 5)
    if domain_cap < level:
        cap_reasons.append(f"domain {alignment} → max {domain_cap}")
    level = min(level, domain_cap)

    return {
        "level": level,
        "label": FIT_LABELS[level],
        "coverage": {
            "critical_met": crit_met,
            "critical_total": crit_total,
            "critical_met_count": prereq_crit_total - prereq_crit_unmet,
            "critical_total_count": prereq_crit_total,
            "required_met": req_met,
            "required_total": req_total,
            "role_defining_gap": role_defining_gap,
            "cap_reason": "; ".join(cap_reasons) or "no cap",
            "prereq_critical_unmet": prereq_crit_unmet,
            "prereq_required_unmet": prereq_req_unmet,
            "role_evidence_matches": role_evidence,
            "domain_alignment": alignment,
            "domain_cap": domain_cap,
            "weighted_earned": round(earned, 2),
            "weighted_total": round(total, 2),
        },
        "strong": strong[:8],
        "weak": weak[:10],
        "preferred_gaps": pref_gaps[:10],
        "product_duties": product_duties[:10],
        "invalid": invalid[:10],
        "risks": risks[:8],
    }


# --------------------------------------------------------------------------- final assembly
def aggregate(
    jobs_by_id: Dict[str, JobPosting],
    tables_by_id: Dict[str, MatchingTable],
    listwise: dict,
    pairwise: List[PairwiseResult],
    candidate_ids: List[str],
    fits: Dict[str, dict],
    domain_ctx: Dict[str, dict],
) -> Tuple[List[FitResult], Dict[str, float], list]:
    """candidate_ids = the jobs that received pairwise comparison (Bradley-Terry set).
    fits = precomputed compute_fit() per job_id (shared with selection/listwise)."""
    ordered_ids = [r["job_id"] for r in listwise["ranking"]]
    top_ids = [jid for jid in candidate_ids if jid in tables_by_id]

    bt = bradley_terry(top_ids, pairwise) if len(top_ids) >= 2 and pairwise else {jid: 0.0 for jid in top_ids}

    DOM_RANK = {"strong": 3, "adjacent": 2, "weak": 1, "mismatch": 0}
    lw_index = {jid: i for i, jid in enumerate(ordered_ids)}

    def fitlvl(jid):
        return fits[jid]["level"]

    def domrank(jid):
        return DOM_RANK.get(domain_ctx.get(jid, {}).get("domain_alignment", "weak"), 1)

    # Pairwise candidates: Bradley-Terry is the PRIMARY key — clear pairwise winners are preserved.
    # fit_level / domain only break exact BT ties (BT rounded so 1.6475==1.6475 ties).
    top_sorted = sorted(
        top_ids, key=lambda x: (-round(bt.get(x, 0.0), 6), -fitlvl(x), -domrank(x), lw_index.get(x, 999), x))
    # Tail (not pairwise-compared): order by fit_level, then domain, then listwise position.
    rest = [jid for jid in ordered_ids if jid not in set(top_ids)]
    rest_sorted = sorted(rest, key=lambda x: (-fitlvl(x), -domrank(x), lw_index[x], x))
    pre_guard_order = top_sorted + rest_sorted

    # Domain-priority guard: a `mismatch`-domain role (marketing/design/product) must never
    # outrank a non-mismatch (engineering) role. Stable partition — BT/pairwise order is preserved
    # WITHIN each partition; this only moves mismatch roles below all non-mismatch roles.
    def is_mismatch(jid):
        return domain_ctx.get(jid, {}).get("domain_alignment", "weak") == "mismatch"

    non_mismatch = [j for j in pre_guard_order if not is_mismatch(j)]
    mismatch = [j for j in pre_guard_order if is_mismatch(j)]
    final_order = non_mismatch + mismatch

    old_rank = {j: i + 1 for i, j in enumerate(pre_guard_order)}
    guard_moves = []
    for new_i, jid in enumerate(final_order, 1):
        if old_rank[jid] != new_i:
            job = jobs_by_id.get(jid)
            guard_moves.append({"job_id": jid, "title": job.title if job else "",
                                "old_rank": old_rank[jid], "new_rank": new_i,
                                "reason": "domain_priority_guard"})

    lw_reason = {r["job_id"]: r.get("reason", "") for r in listwise["ranking"]}
    results: List[FitResult] = []
    for rank, jid in enumerate(final_order, 1):
        job = jobs_by_id.get(jid)
        fit = fits[jid]
        ctx = domain_ctx.get(jid, {})
        results.append(FitResult(
            job_id=jid,
            company=job.company if job else "",
            title=job.title if job else "",
            url=job.url if job else "",
            role_family=ctx.get("role_family", job.role_family if job else "other"),
            domain_alignment=ctx.get("domain_alignment", "weak"),
            domain_alignment_reason=ctx.get("domain_alignment_reason", ""),
            rank=rank,
            fit_level=fit["level"],
            fit_label=fit["label"],
            bt_score=round(bt.get(jid, 0.0), 4),
            listwise_reason=lw_reason.get(jid, ""),
            coverage=fit["coverage"],
            strong_matches=fit["strong"],
            weak_or_missing=fit["weak"],
            preferred_gaps=fit["preferred_gaps"],
            product_duties=fit["product_duties"],
            invalid_matches=fit["invalid"],
            risk_notes=fit["risks"],
        ))
    return results, bt, guard_moves
