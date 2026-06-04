"""Final report: writes JSON + Markdown artifacts to outputs/latest/."""
from __future__ import annotations

import json
from typing import Dict, List

from . import config
from .models import FIT_LABELS, FitResult, MatchingTable, PairwiseResult


def _w(path, text):
    path.write_text(text, encoding="utf-8")


def _dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_outputs(
    fit_results: List[FitResult],
    tables_by_id: Dict[str, MatchingTable],
    listwise: dict,
    pairwise: List[PairwiseResult],
    bt_scores: Dict[str, float],
    fetch_failures: List[str],
    manual_used: bool,
    primary_domains: List[str] = None,
    secondary_domains: List[str] = None,
    skills_debug: dict = None,
    pairwise_info: dict = None,
    guard_moves: list = None,
) -> None:
    config.ensure_dirs()
    out = config.LATEST_DIR
    primary_domains = primary_domains or []
    secondary_domains = secondary_domains or []
    pairwise_info = pairwise_info or {}
    guard_moves = guard_moves or []

    # --- JSON artifacts ---
    _dump(out / "final_ranking.json", {
        "note": "fit_level/bt_score represent FIT 적합도 only, NOT pass probability. No percentages.",
        "fit_levels_legend": FIT_LABELS,
        "user_profile": {"primary_domains": primary_domains, "secondary_domains": secondary_domains},
        "domain_priority_guard_moves": guard_moves,
        "ranking": [r.model_dump() for r in fit_results],
    })
    _dump(out / "matching_tables.json", {jid: t.model_dump() for jid, t in tables_by_id.items()})
    _dump(out / "pairwise_comparisons.json", {
        "bradley_terry_scores": bt_scores,
        "candidate_set": pairwise_info,
        "comparisons": [p.model_dump() for p in pairwise],
    })

    # --- Markdown report ---
    _w(out / "final_report.md", _markdown(
        fit_results, tables_by_id, listwise, pairwise, bt_scores, fetch_failures, manual_used,
        primary_domains, secondary_domains, skills_debug, pairwise_info, guard_moves))


def write_selection_report(selection: dict) -> None:
    """Write outputs/latest/fetch_selection_report.{json,md} describing pool → selection."""
    config.ensure_dirs()
    out = config.LATEST_DIR
    _dump(out / "fetch_selection_report.json", selection)

    L: List[str] = []
    L.append("# JD 후보 선택 리포트 (domain-aware selection)")
    L.append("")
    L.append(f"- 요청 pool-size: {selection.get('pool_size_requested')} · limit: {selection.get('limit')}")
    L.append(f"- 키워드 매칭된 총 후보(엔지니어링): **{selection.get('total_matched')}**")
    L.append(f"- 풀 고려 수(pool_considered): {selection.get('pool_considered')}")
    L.append(f"- 선택: **{selection.get('selected_count')}** · 실제 수집: {selection.get('fetched_count')} · 제외: {selection.get('skipped_count')}")
    pf = selection.get("primary_domain_jobs_found")
    L.append(f"- **주력 도메인(primary) 직무 발견 여부: {'예' if pf else '아니오'}** "
             f"(매칭된 primary 수: {selection.get('primary_in_matched')})")
    if not pf:
        L.append("  > ⚠️ 주력 도메인(frontend/fullstack) 직무가 매칭되지 않았습니다. 후보 셋이 비대표적일 수 있습니다.")
    L.append("")
    L.append(f"- 선택 분포(role_family, 휴리스틱): {selection.get('selected_role_family_distribution')}")
    L.append(f"- 선택 분포(tier): {selection.get('selected_tier_distribution')}")
    L.append(f"- 전체 매칭 분포(role_family): {selection.get('matched_role_family_distribution')}")
    L.append("")
    L.append("## 선택된 JD")
    L.append("| job_id | 회사 | 제목 | pre_role_family | tier | 수집됨 |")
    L.append("|---|---|---|---|---|---|")
    for s in selection.get("selected", []):
        L.append(f"| {s['job_id']} | {s['company']} | {s['title']} | {s['pre_role_family']} "
                 f"| {s['tier']} | {'✓' if s.get('fetched') else '✗'} |")
    L.append("")
    # skipped grouped by tier
    skipped = selection.get("skipped", [])
    if skipped:
        L.append(f"## 제외된 후보 ({len(skipped)}) — tier별")
        by_tier: dict = {}
        for s in skipped:
            by_tier.setdefault(s["tier"], []).append(s)
        for tier, items in by_tier.items():
            L.append(f"- **{tier}** ({len(items)}): " +
                     ", ".join(f"{i['title']}({i['pre_role_family']})" for i in items[:12]) +
                     (" …" if len(items) > 12 else ""))
    L.append("")
    L.append(f"> {selection.get('note')}")
    _w(out / "fetch_selection_report.md", "\n".join(L))


def _title(r: FitResult) -> str:
    return f"{r.company} — {r.title}"


def _markdown(fit_results, tables_by_id, listwise, pairwise, bt_scores, fetch_failures, manual_used,
              primary_domains=None, secondary_domains=None, skills_debug=None, pairwise_info=None,
              guard_moves=None) -> str:
    primary_domains = primary_domains or []
    secondary_domains = secondary_domains or []
    pairwise_info = pairwise_info or {}
    guard_moves = guard_moves or []
    L: List[str] = []
    L.append("# 직무 적합도(Fit) 랭킹 리포트")
    L.append("")
    L.append("> 이 리포트는 **합격 확률을 예측하지 않습니다.** 합격 가능성 퍼센트 수치도 제공하지 않습니다.")
    L.append("> 오직 지원자–공고 간 **적합도(fit)** 만 1~5 단계로 평가합니다.")
    L.append("")

    # user profile (domains)
    L.append("## 사용자 도메인 프로파일")
    L.append(f"- primary_domains: {', '.join(primary_domains) or '-'}")
    L.append(f"- secondary_domains: {', '.join(secondary_domains) or '-'}")
    L.append("> domain_alignment = JD의 role_family 와 위 도메인 프로파일의 거리(strong/adjacent/weak/mismatch).")
    L.append("")

    # fit level legend
    L.append("## 적합도 레벨 (1~5)")
    for lv in sorted(FIT_LABELS, reverse=True):
        L.append(f"- **{lv}** = {FIT_LABELS[lv]}")
    L.append("")

    # 1. final ranking table
    L.append("## 1. 최종 랭킹")
    L.append("")
    L.append("| 순위 | 회사 | 포지션 | role_family | domain_alignment | 적합도 | 레벨 설명 | BT 점수 | 핵심 충족 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in fit_results:
        cov = r.coverage
        crit = f"{cov.get('critical_met', 0)}/{cov.get('critical_total', 0)}"
        req = f"{cov.get('required_met', 0)}/{cov.get('required_total', 0)}"
        L.append(
            f"| {r.rank} | {r.company} | {r.title} | {r.role_family} | {r.domain_alignment} "
            f"| **{r.fit_level}** | {r.fit_label} | {r.bt_score:.3f} | crit {crit}, req {req} |"
        )
    L.append("")
    L.append("> BT 점수 = Bradley-Terry 상대 적합도 강도(비교된 상위 공고 한정). 합격 확률이 아닙니다.")
    if guard_moves:
        L.append("")
        L.append("> **도메인 우선순위 가드(domain_priority_guard) 적용** — mismatch 도메인 역할이 비-mismatch 역할 위로 오지 못하도록 보정:")
        for m in guard_moves:
            L.append(f"> - {m['job_id']} ({m.get('title','')}): rank {m['old_rank']} → {m['new_rank']} (사유: {m['reason']})")
    L.append("")

    # 3-6 per job
    L.append("## 2. 공고별 상세")
    for r in fit_results:
        L.append("")
        L.append(f"### #{r.rank} · {_title(r)} — 적합도 {r.fit_level} ({r.fit_label})")
        if r.url:
            L.append(f"- 링크: {r.url}")
        dcap = r.coverage.get("domain_cap")
        L.append(f"- **role_family / domain_alignment:** {r.role_family} / **{r.domain_alignment}**"
                 + (f" → 레벨 상한 {dcap}" if dcap else "")
                 + (f" — {r.domain_alignment_reason}" if r.domain_alignment_reason else ""))
        L.append(f"- **이 순위인 이유:** {r.listwise_reason or '(listwise 사유 없음)'}")
        cov = r.coverage
        L.append(
            f"- **핵심 요구사항 충족:** critical {cov.get('critical_met', 0)}/{cov.get('critical_total', 0)}, "
            f"required {cov.get('required_met', 0)}/{cov.get('required_total', 0)} "
            f"(prerequisite 미충족: critical {cov.get('prereq_critical_unmet', 0)}, "
            f"required {cov.get('prereq_required_unmet', 0)})"
        )
        L.append(f"- **적합도 상한 사유(cap_reason):** {cov.get('cap_reason', '-')}"
                 + (" · ⚠ role-defining gap" if cov.get('role_defining_gap') else ""))
        tbl = tables_by_id.get(r.job_id)
        grouped = [row for row in (tbl.rows if tbl else []) if row.alternatives]
        if grouped:
            L.append("- **그룹/대체 가능 요구사항 (alternatives · 감사용):**")
            for row in grouped:
                kind = ("exact" if row.match_level == "direct"
                        else "same-category" if row.match_level == "adjacent" else row.match_level)
                ev = ", ".join(row.matched_evidence_ids) if row.matched_evidence_ids else "-"
                quotes = "; ".join(q[:40] for q in row.evidence_quotes) if row.evidence_quotes else ""
                L.append(f"  - [{row.requirement_category}] {row.requirement_text} "
                         f"(alts: {', '.join(row.alternatives)}) → **{row.match_level}** ({kind}); 근거: {ev}"
                         + (f" — {quotes}" if quotes else ""))
        if r.strong_matches:
            L.append("- **강한 매칭(strong/direct):**")
            for s in r.strong_matches:
                L.append(f"  - {s}")
        if r.weak_or_missing:
            L.append("- **약하거나 누락된 핵심 prerequisite(사전 보유 역량) 필수 요구사항:**")
            for w in r.weak_or_missing:
                L.append(f"  - {w}")
        if r.preferred_gaps:
            L.append("- **참고: 누락된 우대 prerequisite 기술(랭킹에는 약하게만 반영):**")
            for pg in r.preferred_gaps:
                L.append(f"  - {pg}")
        if r.product_duties:
            L.append("- **참고: 입사 후 수행 업무(product duty, 사전 자격 아님 → 적합도에 페널티 없음):**")
            for pd in r.product_duties:
                L.append(f"  - {pd}")
        if r.invalid_matches:
            L.append("- **❌ 무효 매칭(비추출 근거로 제거됨):**")
            for im in r.invalid_matches:
                L.append(f"  - {im}")
        if r.risk_notes:
            L.append("- **리스크 / 주의:**")
            for rk in dict.fromkeys(r.risk_notes):  # de-dup, keep order
                L.append(f"  - {rk}")
    L.append("")

    # pairwise candidate set (comparison-only safety)
    cset = pairwise_info.get("pairwise_candidate_set") or []
    if cset:
        L.append("## 3. Pairwise 후보 집합 (비교 대상 — 순위 강제 아님)")
        L.append("| job_id | 포함 사유 | fit | domain |")
        L.append("|---|---|---|---|")
        for c in cset:
            L.append(f"| {c['job_id']} | {c['reason']} | {c['fit']} | {c['domain_alignment']} |")
        if pairwise_info.get("rescued_strong_domain"):
            L.append(f"- 강 도메인 구제 포함(pairwise): {pairwise_info['rescued_strong_domain']}")
        if pairwise_info.get("strong_domain_excluded"):
            L.append("- 포함되지 않은 강 도메인 frontend/fullstack:")
            for e in pairwise_info["strong_domain_excluded"]:
                L.append(f"  - {e['job_id']} (fit {e['fit']}): {e['reason']}")
        L.append("> 후보 집합 포함은 '비교 기회'일 뿐이며, 최종 순위는 pairwise/BT + 타이브레이커로 결정됩니다.")
        L.append("")

    # 7. pairwise summary
    L.append("## 4. Pairwise 비교 요약 (A/B · B/A 순서 교차 검증)")
    if pairwise:
        L.append("")
        L.append("| A | B | A/B 승자 | B/A 승자 | 합의 | 결과 | 신뢰도 |")
        L.append("|---|---|---|---|---|---|---|")
        for p in pairwise:
            agree = "✅" if p.agreed else "⚠️ 불일치→tie"
            outcome = "무승부" if p.outcome == "tie" else p.outcome
            L.append(
                f"| {p.job_a} | {p.job_b} | {p.ab_winner} | {p.ba_winner} | {agree} "
                f"| {outcome} | {p.confidence} |"
            )
        if bt_scores:
            L.append("")
            L.append("**Bradley-Terry 점수 (상위권):**")
            for jid, sc in sorted(bt_scores.items(), key=lambda kv: -kv[1]):
                L.append(f"- {jid}: {sc:.4f}")
    else:
        L.append("")
        L.append("- 비교 가능한 공고가 2개 미만이라 pairwise 비교를 건너뜀.")
    L.append("")

    # listwise uncertainty
    if listwise.get("uncertainty_notes"):
        L.append("## 4. 불확실성 메모 (listwise)")
        L.append(f"- {listwise['uncertainty_notes']}")
        L.append("")

    # listwise reliability warnings
    lw_warn = (listwise or {}).get("warnings") or {}
    L.append("## 5. Listwise 신뢰성")
    if lw_warn:
        L.append("- ⚠️ listwise 이슈가 감지되어 보정했습니다:")
        for k, v in lw_warn.items():
            L.append(f"  - {k}: {v}")
        L.append("  (누락/중복은 재질의 1회 + fit/domain 기준 안전 배치로 처리)")
    else:
        L.append("- listwise가 모든 job_id를 정확히 한 번씩 반환했습니다(누락/중복 없음).")
    L.append("")

    # resume skills debug
    if skills_debug:
        L.append("## 6. 이력서 스킬 추출(디버그)")
        L.append(f"- 전체 evidence 항목: {skills_debug.get('total_evidence_items')}")
        L.append(f"- Skills evidence ids: {skills_debug.get('skills_evidence_ids')}")
        present = skills_debug.get("key_frontend_skills_present", {})
        miss = [k for k, v in present.items() if not v]
        L.append(f"- 핵심 프론트엔드 스킬 가시성: {'모두 present' if not miss else 'missing ' + str(miss)}")
        L.append(f"- 추출된 스킬: {', '.join(skills_debug.get('extracted_skills', [])[:40])}")
        L.append("")

    # 8. scraping / manual notes
    L.append("## 7. 수집(scraping) 및 수동 입력 안내")
    if manual_used:
        L.append("- ⚠️ 자동 수집 결과가 없어 `data/jobs_manual.md` 의 수동 입력 JD를 사용했습니다.")
    else:
        L.append("- 공고는 Toss / Daangn 공식 API에서 자동 수집되었습니다.")
    if fetch_failures:
        L.append("- 수집 중 발생한 이슈:")
        for f in fetch_failures:
            L.append(f"  - {f}")
    else:
        L.append("- 수집 실패/경고 없음.")
    L.append("")
    L.append("---")
    L.append("_생성 산출물: outputs/latest/ (final_ranking.json, matching_tables.json, "
             "pairwise_comparisons.json, final_report.md)_")
    return "\n".join(L)
