"""CLI entry point.

Commands:
  python -m src.main run            full pipeline (fetch -> parse -> match -> verify -> rank -> report)
  python -m src.main fetch-jobs     fetch Toss/Daangn JDs into data/raw/jobs/
  python -m src.main parse-resume   extract evidence items from data/resume.md
  python -m src.main rank           run the ranking pipeline on already-fetched jobs
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List, Tuple

from rich.console import Console
from rich.table import Table

from . import (
    cache,
    compare_pairwise,
    config,
    fetch_jobs,
    llm,
    matching,
    parse_job,
    parse_resume,
    rank_aggregate,
    report,
    rerank_listwise,
    verify_matches,
)
from .models import JobPosting, MatchingTable, Resume

console = Console()


# --------------------------------------------------------------------------- helpers
def _save(name: str, obj) -> None:
    config.ensure_dirs()
    (config.LATEST_DIR / name).write_text(
        json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _llm_ready() -> bool:
    if config.get_provider() is None:
        console.print("[bold red]✗ LLM 미설정[/]")
        console.print(config.provider_help())
        return False
    return True


def _resume_ready() -> Tuple[bool, str]:
    parse_resume.ensure_resume()
    text = parse_resume.load_resume_text()
    if parse_resume.is_placeholder(text):
        console.print(f"[bold red]✗ 이력서가 아직 플레이스홀더입니다:[/] {config.RESUME_PATH}")
        console.print("  실제 이력서로 교체하고 맨 위 '<!-- RESUME_PLACEHOLDER -->' 줄을 삭제하세요.")
        return False, text
    return True, text


def _print_fetch_failures(failures: List[str]) -> None:
    for f in failures:
        console.print(f"  [yellow]·[/] {f}")


def _apply_cache_flags(args) -> None:
    cache.REFRESH = bool(getattr(args, "refresh_cache", False))
    cache.reset_stats()
    console.print(f"   [dim]cache namespace: {cache.NAMESPACE or 'normal'} "
                  f"(refresh={'on' if cache.REFRESH else 'off'})[/]")
    if cache.REFRESH:
        console.print("   [yellow]--refresh-cache: 기존 캐시를 무시하고 재파싱합니다(새로 저장).[/]")


def _print_cache_log() -> None:
    for line in cache.LOG:
        console.print(f"   [dim]{line}[/]")
    console.print(f"   [cyan]{cache.summary()}[/] → {config.CACHE_DIR}")


def _load_fixture_jobs(args):
    """Return (raw_jobs, ok). Loads the fixture if --fixture was given, else (None, True)."""
    fixture = getattr(args, "fixture", None)
    if not fixture:
        return None, True
    try:
        jobs = fetch_jobs.load_fixture(fixture)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]픽스처 로드 실패:[/] {fixture} ({e})")
        return [], False
    lim = getattr(args, "limit", None)
    if lim and lim > 0:
        jobs = jobs[:lim]
    console.print(f"[bold]0) 픽스처 로드[/] {fixture} → {len(jobs)}건")
    return jobs, True


# --------------------------------------------------------------------------- commands
def _limit(args) -> int:
    lim = getattr(args, "limit", None)
    return lim if lim and lim > 0 else config.MAX_JD_PAGES


def _pool(args) -> int:
    p = getattr(args, "pool_size", None)
    return p if p and p > 0 else config.DEFAULT_POOL_SIZE


def _print_selection(selection: dict) -> None:
    console.print(f"   [cyan]pool: matched={selection['total_matched']} "
                  f"considered={selection['pool_considered']} → selected={selection['selected_count']} "
                  f"· primary found: {selection['primary_domain_jobs_found']}[/]")
    console.print(f"   [dim]selected role_family: {selection['selected_role_family_distribution']}[/]")


def cmd_fetch_jobs(args) -> List[dict]:
    console.rule("[bold]Fetch jobs (Toss · Daangn) — domain-aware selection")
    config.ensure_dirs()
    fetch_jobs.ensure_manual_template()
    jobs, failures, selection = fetch_jobs.fetch_all(_limit(args), _pool(args))
    report.write_selection_report(selection)
    _print_selection(selection)
    if jobs:
        fetch_jobs.save_raw(jobs)
        t = Table(title=f"선택된 공고 {len(jobs)}건", show_lines=False)
        t.add_column("job_id"); t.add_column("company"); t.add_column("title"); t.add_column("role(heur)")
        for j in jobs:
            t.add_row(j["job_id"], j["company"], j["title"], j.get("pre_role_family", "?"))
        console.print(t)
        console.print(f"[green]✓ 원본 저장:[/] {config.RAW_JOBS_DIR}")
        console.print(f"[green]✓ 선택 리포트:[/] {config.LATEST_DIR / 'fetch_selection_report.md'}")
    else:
        console.print("[yellow]자동 수집 결과가 없습니다.[/] "
                      f"`{config.JOBS_MANUAL_PATH}` 에 JD를 직접 붙여넣어 주세요.")
    if getattr(args, "selection_report", False):
        console.print("\n[bold]전체 선택 내역(--selection-report):[/]")
        for s in selection["selected"]:
            console.print(f"  [green]선택[/] {s['tier']:8s} {s['pre_role_family']:12s} {s['company']} — {s['title']}")
        for s in selection["skipped"][:30]:
            console.print(f"  [dim]제외 {s['tier']:8s} {s['pre_role_family']:12s} {s['company']} — {s['title']}[/]")
        if len(selection["skipped"]) > 30:
            console.print(f"  [dim]… 외 {len(selection['skipped']) - 30}건 제외[/]")
    if failures:
        console.print("[dim]수집 경고:[/]")
        _print_fetch_failures(failures)
    return jobs


def cmd_parse_resume(_args) -> bool:
    console.rule("[bold]Parse resume")
    ok, text = _resume_ready()
    if not ok:
        return False
    if not _llm_ready():
        return False
    console.print("이력서에서 evidence 추출 중...")
    resume = parse_resume.extract_evidence(text)
    _save("resume_parsed.json", resume.model_dump())
    console.print(f"[green]✓ evidence {len(resume.evidence)}개 추출[/] → outputs/latest/resume_parsed.json")
    for e in resume.evidence:
        console.print(f"  [dim]{e.evidence_id}[/] {e.title}  ({e.evidence_type}/{e.strength})")
    return True


_DOM_RANK = {"strong": 3, "adjacent": 2, "weak": 1, "mismatch": 0}


def _build_pairwise_candidates(ordered_ids, fits, domain_ctx, top_k):
    """Build the pairwise candidate set so strong-domain jobs get a fair comparison.
    Inclusion is comparison-only; final order is still decided by BT + tie-breakers."""
    def fit(j): return fits[j]["level"]
    def dom(j): return domain_ctx.get(j, {}).get("domain_alignment", "weak")
    def rf(j): return domain_ctx.get(j, {}).get("role_family", "other")
    def is_strong_fe(j): return dom(j) == "strong" and rf(j) in ("frontend", "fullstack")
    lw_rank = {j: i for i, j in enumerate(ordered_ids)}

    candidates, reasons = [], {}

    def add(j, why):
        if j not in reasons:
            candidates.append(j); reasons[j] = why

    # 1) listwise top-5 (any domain)
    for j in ordered_ids[:top_k]:
        add(j, "listwise top-5")
    # 2) any fit>=4 (weak/mismatch can't reach fit>=4 due to caps, so this is engineering-only)
    for j in ordered_ids:
        if fit(j) >= 4:
            add(j, "fit>=4")
    # 3) strong frontend/fullstack with fit > the weakest fit currently in the set
    for j in ordered_ids:
        if j in reasons or not is_strong_fe(j):
            continue
        weakest = min((fit(c) for c in candidates), default=0)
        if fit(j) > weakest:
            add(j, f"strong frontend rescue (fit {fit(j)} > weakest-in-set {weakest})")
    # 4) catch-all: a strong-domain job is excluded while a LOWER-fit adjacent/weak job is compared
    for j in ordered_ids:
        if j in reasons or dom(j) != "strong":
            continue
        if any(dom(c) in ("adjacent", "weak", "mismatch") and fit(c) < fit(j) for c in candidates):
            add(j, "strong-domain rescue (a lower-fit adjacent/weak role is compared)")

    # bound the set; prefer higher fit, then domain, then listwise rank. Never via weak/mismatch (rules 2-4).
    cap = config.MAX_PAIRWISE_CANDIDATES
    if len(candidates) > cap:
        kept = set(sorted(candidates,
                          key=lambda j: (-fit(j), -_DOM_RANK.get(dom(j), 1), lw_rank.get(j, 999)))[:cap])
        for j in candidates:
            if j not in kept:
                reasons[j] += " [bounded out]"
        candidates = [j for j in ordered_ids if j in kept]

    info = {
        "pairwise_candidate_set": [
            {"job_id": j, "reason": reasons[j], "fit": fit(j),
             "domain_alignment": dom(j), "role_family": rf(j)} for j in candidates],
        "rescued_strong_domain": [j for j in candidates if reasons[j].startswith("strong")],
        "strong_domain_excluded": [
            {"job_id": j, "fit": fit(j),
             "reason": ("bounded out (max candidates)" if "[bounded out]" in reasons.get(j, "")
                        else f"not rescued (fit {fit(j)} not above weakest-in-set)")}
            for j in ordered_ids if is_strong_fe(j) and j not in candidates],
    }
    return candidates, info


def _parse_all_jobs(raw_jobs: List[dict]) -> Tuple[List[JobPosting], List[str]]:
    jobs: List[JobPosting] = []
    warnings: List[str] = []
    for i, rj in enumerate(raw_jobs, 1):
        console.print(f"  [dim]({i}/{len(raw_jobs)})[/] JD 구조화: {rj.get('title','?')}")
        try:
            jobs.append(parse_job.structure_job(rj))
        except llm.LLMError:
            raise
        except Exception as e:  # noqa: BLE001
            warnings.append(f"JD 파싱 실패 {rj.get('job_id')}: {e}")
    return jobs, warnings


def _pipeline_rank(raw_jobs: List[dict], resume_text: str,
                   fetch_failures: List[str], manual_used: bool) -> bool:
    if not raw_jobs:
        console.print("[yellow]사용할 JD가 없습니다.[/] 먼저 `python -m src.main fetch-jobs` 를 실행하거나 "
                      f"`{config.JOBS_MANUAL_PATH}` 를 채우세요.")
        return False

    # Stage 1: resume -> evidence
    console.print("[bold]1) 이력서 evidence 추출[/]")
    resume: Resume = parse_resume.extract_evidence(resume_text)
    resume.primary_domains = config.USER_PRIMARY_DOMAINS
    resume.secondary_domains = config.USER_SECONDARY_DOMAINS
    _save("resume_parsed.json", resume.model_dump())
    sk_dbg = parse_resume.skills_debug(resume)
    _save("resume_skills_debug.json", sk_dbg)
    console.print(f"   evidence {len(resume.evidence)}개 (skills items: {sk_dbg['skills_evidence_ids']})")
    console.print(f"   user primary_domains={resume.primary_domains} · secondary_domains={resume.secondary_domains}")
    missing_keys = [k for k, v in sk_dbg["key_frontend_skills_present"].items() if not v]
    console.print(f"   key frontend skills present: {'all' if not missing_keys else 'missing ' + str(missing_keys)}")

    # Stage 2: structure JDs
    console.print(f"[bold]2) JD 구조화 ({len(raw_jobs)}건)[/]")
    jobs, warns = _parse_all_jobs(raw_jobs)
    fetch_failures = fetch_failures + warns
    if not jobs:
        console.print("[red]구조화된 JD가 없습니다. 중단합니다.[/]")
        return False
    _save("jobs_parsed.json", [j.model_dump() for j in jobs])

    # Domain-alignment context (drives the visible domain-distance signal + fit cap).
    domain_ctx = {}
    for job in jobs:
        align, reason = rank_aggregate.domain_alignment(
            job.role_family, resume.primary_domains, resume.secondary_domains)
        domain_ctx[job.job_id] = {
            "role_family": job.role_family,
            "domain_alignment": align,
            "domain_alignment_reason": reason,
        }
        console.print(f"   [dim]{job.job_id}[/] role_family={job.role_family} → domain_alignment={align}")

    # Stages 5-6: matching + verify, per JD. A single JD's failure is non-fatal so the
    # overall run still completes (it is dropped from the ranking with a warning).
    console.print("[bold]3) 요구사항-근거 매칭 + 검증(보수적)[/]")
    tables: List[MatchingTable] = []
    raw_snaps = {}
    for i, job in enumerate(jobs, 1):
        console.print(f"   [dim]({i}/{len(jobs)})[/] {job.company} — {job.title}")
        try:
            tbl = matching.build_matching_table(job, resume.evidence)
            raw_snaps[tbl.job_id] = tbl.model_dump()  # snapshot before verify mutates it
            verify_matches.verify_table(tbl, resume_text, resume.evidence)
            tables.append(tbl)
        except llm.LLMError as e:
            fetch_failures.append(f"매칭/검증 실패로 제외됨 {job.job_id}: {e}")
            console.print(f"   [yellow]· 건너뜀(JD 제외): {job.job_id} — {e}[/]")
    if not tables:
        console.print("[red]매칭된 JD가 없습니다. 중단합니다.[/]")
        return False
    _save("matching_tables_raw.json", raw_snaps)

    # Precompute fit levels once (shared by listwise placement, pairwise candidate safety, aggregate).
    tables_by_id = {t.job_id: t for t in tables}
    fits = {jid: rank_aggregate.compute_fit(t, domain_ctx.get(jid, {}).get("domain_alignment", "weak"))
            for jid, t in tables_by_id.items()}

    # Stage 7: listwise rerank (with omission/duplicate handling + fit-aware placement)
    console.print("[bold]5) Listwise 재랭킹[/]")
    listwise = rerank_listwise.listwise_rank(tables, domain_ctx, fits)
    _save("listwise.json", {k: v for k, v in listwise.items()})
    ordered_ids = [r["job_id"] for r in listwise["ranking"]]
    if listwise.get("warnings"):
        console.print(f"   [yellow]listwise 경고: {listwise['warnings']}[/]")

    # Stage 8: pairwise candidate set (comparison-only safety so strong-domain jobs get a fair compare)
    top_k = min(config.TOP_K_PAIRWISE, len(ordered_ids))
    candidates, pairwise_info = _build_pairwise_candidates(ordered_ids, fits, domain_ctx, top_k)
    console.print(f"[bold]6) Pairwise 비교 (후보 {len(candidates)}건, A/B·B/A 교차)[/]")
    if pairwise_info["rescued_strong_domain"]:
        console.print(f"   [yellow]강 도메인 구제 포함: {pairwise_info['rescued_strong_domain']}[/]")
    pairwise = compare_pairwise.run_pairwise(tables, candidates, domain_ctx)

    # Stage 9+10: aggregate + fit levels
    console.print("[bold]7) Bradley-Terry 집계 + 적합도(1~5) 산출[/]")
    jobs_by_id = {j.job_id: j for j in jobs}
    fit_results, bt, guard_moves = rank_aggregate.aggregate(
        jobs_by_id, tables_by_id, listwise, pairwise, candidates, fits, domain_ctx)
    if guard_moves:
        console.print(f"   [yellow]domain-priority guard moved: "
                      f"{[(m['job_id'], m['old_rank'], '→', m['new_rank']) for m in guard_moves]}[/]")

    # Report
    report.write_outputs(fit_results, tables_by_id, listwise, pairwise, bt,
                         fetch_failures, manual_used,
                         primary_domains=resume.primary_domains,
                         secondary_domains=resume.secondary_domains,
                         skills_debug=sk_dbg, pairwise_info=pairwise_info,
                         guard_moves=guard_moves)

    _print_final(fit_results)
    _print_cache_log()
    console.print(f"\n[green]✓ 리포트 생성 완료[/] → {config.LATEST_DIR}")
    console.print("   final_report.md · final_ranking.json · matching_tables.json · pairwise_comparisons.json")
    return True


def _print_final(fit_results) -> None:
    t = Table(title="최종 적합도(Fit) 랭킹 — 합격확률 아님")
    t.add_column("#", justify="right")
    t.add_column("회사"); t.add_column("포지션")
    t.add_column("role", justify="center"); t.add_column("domain", justify="center")
    t.add_column("적합도", justify="center"); t.add_column("레벨 설명")
    t.add_column("BT", justify="right")
    for r in fit_results:
        t.add_row(str(r.rank), r.company, r.title, r.role_family, r.domain_alignment,
                  str(r.fit_level), r.fit_label, f"{r.bt_score:.3f}")
    console.print(t)


def cmd_rank(args) -> bool:
    console.rule("[bold]Rank (already-fetched jobs)")
    config.ensure_dirs()
    _apply_cache_flags(args)
    ok, text = _resume_ready()
    if not ok or not _llm_ready():
        return False
    fixture_jobs, fok = _load_fixture_jobs(args)
    if not fok:
        return False
    if fixture_jobs is not None:
        raw_jobs = fixture_jobs
        manual_used = False
    else:
        raw_jobs = fetch_jobs.load_raw_jobs()
        lim = getattr(args, "limit", None)
        if lim and lim > 0:
            raw_jobs = raw_jobs[:lim]
        manual_used = bool(raw_jobs) and all(j["job_id"].startswith("manual-") for j in raw_jobs)
    return _pipeline_rank(raw_jobs, text, [], manual_used)


def cmd_run(args) -> bool:
    console.rule("[bold]Run full pipeline")
    config.ensure_dirs()
    fetch_jobs.ensure_manual_template()
    _apply_cache_flags(args)
    limit = _limit(args)
    failures: List[str] = []

    fixture_jobs, fok = _load_fixture_jobs(args)
    if not fok:
        return False
    if fixture_jobs is not None:
        # Fixed regression set — skip fetching entirely.
        raw_jobs = fixture_jobs
        manual_used = False
    else:
        # Fetch first (free, no LLM). Domain-aware: pool → balanced selection.
        pool_size = _pool(args)
        console.print(f"[bold]0) 공고 수집 (domain-aware)[/] (limit={limit}, pool-size={pool_size})")
        jobs, failures, selection = fetch_jobs.fetch_all(limit, pool_size)
        report.write_selection_report(selection)
        _print_selection(selection)
        if jobs:
            fetch_jobs.save_raw(jobs)
            raw_jobs = jobs            # use the fresh fetch directly so --limit is respected
            manual_used = False
            console.print(f"   [green]수집 {len(jobs)}건[/] → 선택 리포트: outputs/latest/fetch_selection_report.md")
        else:
            console.print("   [yellow]자동 수집 0건 — 수동 입력(jobs_manual.md) 확인[/]")
            raw_jobs = fetch_jobs.load_raw_jobs()
            if limit:
                raw_jobs = raw_jobs[:limit]
            manual_used = bool(raw_jobs)
        if failures:
            _print_fetch_failures(failures)

    # Preflight for the LLM stages.
    ok, text = _resume_ready()
    llm_ok = _llm_ready()
    if not raw_jobs:
        console.print(f"[yellow]사용할 JD가 없습니다.[/] `{config.JOBS_MANUAL_PATH}` 를 채운 뒤 다시 실행하세요.")
    if not (ok and llm_ok and raw_jobs):
        console.print("\n[bold yellow]LLM 단계 전에 필요한 항목이 빠져 중단합니다.[/] "
                      "위 안내를 처리한 뒤 다시 실행하세요. (수집된 원본은 data/raw/jobs/ 에 저장되어 있습니다.)")
        return False

    return _pipeline_rank(raw_jobs, text, failures, manual_used)


def cmd_doctor(_args) -> bool:
    """Preflight check: provider/model, resume, prompts, jobs, and a live LLM ping."""
    console.rule("[bold]Doctor (preflight)")
    rows = []  # (name, ok, detail)

    provider = config.get_provider()
    model = config.OPENAI_MODEL if provider == "openai" else (
        config.ANTHROPIC_MODEL if provider == "anthropic" else "-")
    rows.append(("LLM provider", provider is not None, f"{provider or '없음'} (model={model})"))

    # resume
    config_ok_resume = config.RESUME_PATH.exists()
    if config_ok_resume:
        txt = parse_resume.load_resume_text()
        is_ph = parse_resume.is_placeholder(txt)
        rows.append(("Resume", not is_ph, "플레이스홀더" if is_ph else f"{config.RESUME_PATH.name} ({len(txt)} chars)"))
    else:
        rows.append(("Resume", False, f"없음: {config.RESUME_PATH}"))

    # prompts
    needed = ["resume_extract", "jd_extract", "requirement_evidence_match",
              "match_verifier", "listwise_rerank", "pairwise_compare"]
    missing = [n for n in needed if not (config.PROMPTS_DIR / f"{n}.md").exists()]
    rows.append(("Prompts", not missing, "모두 존재" if not missing else f"누락: {missing}"))

    # jobs availability (informational)
    raw = fetch_jobs.load_raw_jobs()
    rows.append(("JDs available", True, f"{len(raw)}건 (run 시 자동 수집 가능)"))

    # live LLM ping (the real check)
    ping_ok = False
    if provider is None:
        ping_detail = "키 없음 — 핑 생략"
    else:
        try:
            used = llm.ping()
            ping_ok = True
            ping_detail = f"OK — {provider}/{used} 응답 정상"
        except llm.LLMError as e:
            ping_detail = str(e)
    rows.append(("LLM live ping", ping_ok, ping_detail))

    t = Table(title="Doctor", show_lines=False)
    t.add_column("점검"); t.add_column("결과", justify="center"); t.add_column("상세")
    for name, ok, detail in rows:
        t.add_row(name, "[green]PASS[/]" if ok else "[red]FAIL[/]", detail)
    console.print(t)

    critical_ok = (provider is not None) and (not missing) and ping_ok and \
        config_ok_resume and not (config_ok_resume and parse_resume.is_placeholder(parse_resume.load_resume_text()))
    if critical_ok:
        console.print("[green]✓ 준비 완료 — `python -m src.main run` 실행 가능[/]")
    else:
        if provider is None:
            console.print("[red]✗ LLM 키가 없습니다.[/] " + config.provider_help())
        elif not ping_ok:
            console.print("[red]✗ LLM 라이브 핑 실패.[/] 위 상세 메시지를 확인하세요 "
                          "(키가 잘못됐거나, 모델 이름이 유효하지 않을 수 있습니다).")
    return critical_ok


def _check_invariants() -> bool:
    """Invariant-based fixture regression (replaces exact 5/2/1 matching)."""
    out = config.LATEST_DIR
    ranking = json.loads((out / "final_ranking.json").read_text(encoding="utf-8"))["ranking"]
    tables = json.loads((out / "matching_tables.json").read_text(encoding="utf-8"))
    pw = json.loads((out / "pairwise_comparisons.json").read_text(encoding="utf-8"))
    resume = json.loads((out / "resume_parsed.json").read_text(encoding="utf-8"))

    by_rf = {}
    for r in ranking:  # first (best-ranked) entry of each role_family
        by_rf.setdefault(r["role_family"], r)
    fe, an, mk = by_rf.get("frontend"), by_rf.get("android"), by_rf.get("marketing")
    n = len(ranking)

    checks = []
    checks.append(("Frontend ranks #1", bool(fe) and fe["rank"] == 1))
    checks.append(("Frontend fit >= 4", bool(fe) and fe["fit_level"] >= 4))
    checks.append(("Android ranks below Frontend", bool(an and fe) and an["rank"] > fe["rank"]))
    checks.append(("Android fit <= 3", bool(an) and an["fit_level"] <= 3))
    checks.append(("Android fit < Frontend fit", bool(an and fe) and an["fit_level"] < fe["fit_level"]))
    checks.append(("Marketing ranks last", bool(mk) and mk["rank"] == n))
    checks.append(("Marketing fit <= 2", bool(mk) and mk["fit_level"] <= 2))
    # domain-priority: no mismatch role may rank above any non-mismatch role
    mismatch_ranks = [r["rank"] for r in ranking if r["domain_alignment"] == "mismatch"]
    nonmismatch_ranks = [r["rank"] for r in ranking if r["domain_alignment"] != "mismatch"]
    dp_ok = (not mismatch_ranks) or (not nonmismatch_ranks) or (min(mismatch_ranks) > max(nonmismatch_ranks))
    checks.append(("Mismatch role not above any non-mismatch role", dp_ok))

    # all surviving evidence quotes extractive (re-validated against the resume)
    from . import verify_matches as V
    from .models import EvidenceItem
    ev = [EvidenceItem(**e) for e in resume.get("evidence", [])]
    hay = V._build_haystack(resume.get("raw_text", ""), ev)
    bad = [(jid, q) for jid, t in tables.items() for row in t["rows"]
           for q in row["evidence_quotes"] if not V._is_extractive(q, hay)]
    checks.append(("All surviving quotes extractive", not bad))

    # pairwise: no disagreement, OR disagreement that does not change the top ranking
    dis = [c for c in pw["comparisons"] if not c["agreed"]]
    top_unchanged = bool(fe) and fe["rank"] == 1
    checks.append(("Pairwise: no disagreement OR top unchanged", (not dis) or top_unchanged))

    t = Table(title="Regression invariants (fixture)")
    t.add_column("invariant"); t.add_column("result", justify="center")
    for name, ok in checks:
        t.add_row(name, "[green]PASS[/]" if ok else "[red]FAIL[/]")
    console.print(t)
    if dis:
        console.print(f"[yellow]⚠ pairwise disagreements: {len(dis)} (top ranking unchanged: {top_unchanged})[/]")
        for c in dis:
            console.print(f"   {c['job_a']} vs {c['job_b']}: ab={c['ab_winner']} ba={c['ba_winner']} → outcome={c['outcome']}")
    if bad:
        console.print(f"[red]non-extractive surviving quotes: {len(bad)}[/]")
        for jid, q in bad[:5]:
            console.print(f"   {jid}: {q[:50]}")
    all_ok = all(ok for _, ok in checks)
    console.print("[green]✓ 모든 불변식 통과[/]" if all_ok else "[red]✗ 불변식 위반 — 중단 권장[/]")
    return all_ok


def cmd_regression(args) -> bool:
    console.rule("[bold]Regression (fixture, invariant-based)")
    config.ensure_dirs()
    cache.NAMESPACE = "fixture"  # isolated cache so full --refresh-cache runs never touch the golden
    _apply_cache_flags(args)
    fixture = getattr(args, "fixture", None) or str(config.FIXTURES_DIR / "original_3_jds.json")
    ok, text = _resume_ready()
    if not ok or not _llm_ready():
        return False
    try:
        raw_jobs = fetch_jobs.load_fixture(fixture)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]픽스처 로드 실패:[/] {fixture} ({e})")
        return False
    console.print(f"[bold]픽스처:[/] {fixture} → {len(raw_jobs)}건")
    if not _pipeline_rank(raw_jobs, text, [], manual_used=False):
        return False
    console.rule("[bold]Invariants")
    return _check_invariants()


COMMANDS = {
    "run": cmd_run,
    "fetch-jobs": cmd_fetch_jobs,
    "parse-resume": cmd_parse_resume,
    "rank": cmd_rank,
    "doctor": cmd_doctor,
    "regression": cmd_regression,
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m src.main",
                                     description="Local job–resume fit ranking prototype")
    sub = parser.add_subparsers(dest="command", required=True)
    p_run = sub.add_parser("run", help="full pipeline (fetch -> rank -> report)")
    p_run.add_argument("--limit", type=int, default=None, help="max number of JDs to evaluate")
    p_run.add_argument("--pool-size", type=int, default=None, help="candidate pool size before selection (default 50)")
    p_run.add_argument("--fixture", default=None, help="use a fixed JD set from a fixture JSON (skips fetching)")
    p_run.add_argument("--refresh-cache", action="store_true", help="ignore cached parses and re-parse")
    p_fetch = sub.add_parser("fetch-jobs", help="fetch Toss/Daangn JDs (domain-aware selection)")
    p_fetch.add_argument("--limit", type=int, default=None, help="max number of JDs to select")
    p_fetch.add_argument("--pool-size", type=int, default=None, help="candidate pool size before selection (default 50)")
    p_fetch.add_argument("--selection-report", action="store_true", help="print full selection/skip breakdown")
    sub.add_parser("parse-resume", help="extract evidence items from data/resume.md")
    p_rank = sub.add_parser("rank", help="run ranking on already-fetched jobs")
    p_rank.add_argument("--limit", type=int, default=None, help="max number of stored JDs to evaluate")
    p_rank.add_argument("--fixture", default=None, help="use a fixed JD set from a fixture JSON")
    p_rank.add_argument("--refresh-cache", action="store_true", help="ignore cached parses and re-parse")
    sub.add_parser("doctor", help="preflight check (config + live LLM ping)")
    p_reg = sub.add_parser("regression", help="invariant-based fixture regression check")
    p_reg.add_argument("--fixture", default=None, help="fixture JSON (default data/fixtures/original_3_jds.json)")
    p_reg.add_argument("--refresh-cache", action="store_true", help="ignore cached parses and re-parse")
    args = parser.parse_args(argv)
    try:
        ok = COMMANDS[args.command](args)
    except llm.LLMError as e:
        console.print(f"\n[bold red]LLM 오류:[/] {e}")
        return 2
    except KeyboardInterrupt:
        console.print("\n[yellow]중단됨[/]")
        return 130
    return 0 if ok or ok is None else 1


if __name__ == "__main__":
    sys.exit(main())
