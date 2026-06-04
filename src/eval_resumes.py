"""Multi-resume diagnostic eval suite (generalization check).

The v0 ranking algorithm was validated against ONE real frontend/fullstack resume. This module
runs the SAME pipeline against several synthetic personas (backend / junior-frontend / ai-ml /
devops-infra) and labels each result with coarse, product-level invariants — pass / warning / fail.

This is a DIAGNOSTIC, not an accuracy benchmark. It does not modify the ranking algorithm; it only
reads back the artifacts the pipeline writes (final_ranking.json, matching_tables.json, …) and
asserts direction-level expectations from data/eval/expected_behavior.json.

Pure functions only — this module never imports `main`, so the CLI can import it without a cycle.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import verify_matches as V
from .models import EvidenceItem

MISMATCH_FAMILIES = {"marketing", "design", "product"}

# Resume sections we expect each synthetic persona to provide (heading keyword → label).
# Matched case-insensitively against any markdown heading line.
REQUIRED_SECTIONS = {
    "summary": r"summary|요약",
    "skills": r"skills?|기술",
    "experience": r"experience|경력",
    "projects": r"projects?|프로젝트",
    "education": r"education|학력",
    "preferences": r"preferences|선호|희망",
}

# Severity of each invariant. "fail" invariants are hard product rules; "warning" invariants are
# direction signals that LLM variance can legitimately bend.
SEVERITY = {
    "extractive": "fail",
    "fit_scale": "fail",
    "mismatch_priority": "fail",
    "expected_top_in_top3": "warning",
    "domain_order": "warning",
    "primary_domain_available": "warning",
}


# --------------------------------------------------------------------------- loading
def load_expected(path: Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "personas" not in data or not isinstance(data["personas"], dict):
        raise ValueError(f"{path}: expected a top-level 'personas' object")
    return data


def discover_resumes(resume_dir: Path) -> List[Path]:
    return sorted(p for p in Path(resume_dir).glob("*.md") if p.is_file())


def plan_personas(resume_dir: Path, expected: dict,
                  only: Optional[str] = None) -> Tuple[List[dict], List[str]]:
    """Match resume files to expected_behavior entries by slug (filename stem).
    Returns (personas, warnings). Each persona dict: slug, path, entry."""
    personas: List[dict] = []
    warnings: List[str] = []
    files = {p.stem: p for p in discover_resumes(resume_dir)}
    entries = expected.get("personas", {})

    for slug in sorted(set(files) | set(entries)):
        if only and slug != only:
            continue
        path = files.get(slug)
        entry = entries.get(slug)
        if path is None:
            warnings.append(f"expected_behavior has '{slug}' but no resume file {resume_dir}/{slug}.md")
            continue
        if entry is None:
            warnings.append(f"resume {path.name} has no entry in expected_behavior.json — skipped")
            continue
        personas.append({"slug": slug, "path": path, "entry": entry})
    if only and not personas:
        warnings.append(f"--only {only}: no matching persona found")
    return personas, warnings


def validate_sections(text: str) -> List[str]:
    """Return the list of REQUIRED_SECTIONS missing from the resume markdown headings."""
    heading_lines = [ln for ln in text.splitlines() if re.match(r"^\s*#{1,6}\s+", ln)]
    blob = "\n".join(heading_lines).lower()
    missing = []
    for name, pat in REQUIRED_SECTIONS.items():
        if not re.search(pat, blob, re.I):
            missing.append(name)
    return missing


# --------------------------------------------------------------------------- diagnosis
def _extractive_failures(tables: dict, resume_parsed: dict) -> List[Tuple[str, str]]:
    """Re-validate that every surviving evidence quote is extractive from the resume."""
    ev = [EvidenceItem(**e) for e in resume_parsed.get("evidence", [])]
    hay = V._build_haystack(resume_parsed.get("raw_text", ""), ev)
    bad = []
    for jid, t in tables.items():
        for row in t.get("rows", []):
            for q in row.get("evidence_quotes", []):
                if not V._is_extractive(q, hay):
                    bad.append((jid, q))
    return bad


def _job_brief(r: dict) -> dict:
    return {
        "rank": r.get("rank"),
        "company": r.get("company", ""),
        "title": r.get("title", ""),
        "role_family": r.get("role_family", "other"),
        "domain_alignment": r.get("domain_alignment", "weak"),
        "fit_level": r.get("fit_level"),
        "fit_label": r.get("fit_label", ""),
    }


def diagnose(slug: str, entry: dict, art: dict) -> dict:
    """Run coarse invariants over one persona's artifacts. Returns a summary dict.

    art keys: ranking (list), tables (dict), pairwise (dict), resume_parsed (dict),
              selection (dict, optional), listwise (dict, optional), fetch_failures (list, optional)
    """
    ranking: List[dict] = art.get("ranking", [])
    tables: dict = art.get("tables", {})
    pairwise: dict = art.get("pairwise", {})
    selection: dict = art.get("selection", {}) or {}
    listwise: dict = art.get("listwise", {}) or {}
    fetch_failures: List[str] = art.get("fetch_failures", []) or []
    n = len(ranking)

    present_rf = {r.get("role_family") for r in ranking}
    top3_rf = {r.get("role_family") for r in ranking[:3]}
    top5_rf = {r.get("role_family") for r in ranking[:5]}
    expected_top = set(entry.get("expected_top_role_families", []))

    checks: List[dict] = []

    def add(key: str, ok, detail: str, na: bool = False):
        status = "n/a" if na else ("pass" if ok else SEVERITY.get(key, "warning"))
        checks.append({"invariant": key, "severity": SEVERITY.get(key, "warning"),
                       "status": status, "detail": detail})

    # 1) extractive (fail): every surviving quote is extractive from the resume
    bad = _extractive_failures(tables, resume_parsed=art.get("resume_parsed", {}))
    add("extractive", not bad,
        "모든 잔존 인용이 추출형" if not bad else f"비추출 인용 {len(bad)}건 잔존 (예: {bad[0][1][:40]!r})")

    # 2) fit_scale (fail): fit is an integer 1..5 (never a percentage / probability)
    levels = [r.get("fit_level") for r in ranking]
    scale_ok = all(isinstance(lv, int) and 1 <= lv <= 5 for lv in levels) if levels else True
    bad_keys = {k for r in ranking for k in r if re.search(r"percent|probab|확률", k, re.I)}
    add("fit_scale", scale_ok and not bad_keys,
        "모든 fit_level 이 1~5 정수" + ("" if not bad_keys else f"; 금지 필드 {sorted(bad_keys)}")
        if scale_ok else f"1~5 범위를 벗어난 fit_level: {sorted({lv for lv in levels if not (isinstance(lv,int) and 1<=lv<=5)})}")

    # 3) mismatch_priority (fail): no mismatch role ranks above any non-mismatch role
    mm = [r["rank"] for r in ranking if r.get("domain_alignment") == "mismatch"]
    nm = [r["rank"] for r in ranking if r.get("domain_alignment") != "mismatch"]
    mm_ok = (not mm) or (not nm) or (min(mm) > max(nm))
    add("mismatch_priority", mm_ok,
        "mismatch 역할 없음" if not mm else
        ("mismatch 가 모든 non-mismatch 아래" if mm_ok else "⚠ mismatch 역할이 엔지니어링 역할 위로 랭크됨"))

    # 4) expected_top_in_top3 (warning, na-able): an expected-top family must appear in top 3
    exp_present = expected_top & present_rf
    if not expected_top or not exp_present:
        add("expected_top_in_top3", True,
            f"선택된 JD에 expected_top role_family({sorted(expected_top)}) 없음 → 평가 불가", na=True)
    else:
        ok = bool(expected_top & top3_rf)
        add("expected_top_in_top3", ok,
            f"top3 role_family {sorted(top3_rf)} 에 expected_top {sorted(exp_present)} "
            + ("포함" if ok else "미포함"))

    # 5) domain_order (warning, na-able): strong/adjacent generally outrank weak/mismatch
    good = [r["rank"] for r in ranking if r.get("domain_alignment") in ("strong", "adjacent")]
    low = [r["rank"] for r in ranking if r.get("domain_alignment") in ("weak", "mismatch")]
    inversions = sum(1 for g in good for l in low if g > l)
    if not good or not low:
        add("domain_order", True, "strong/adjacent 또는 weak/mismatch 한쪽이 없어 비교 불가", na=True)
    else:
        rate = inversions / (len(good) * len(low))
        add("domain_order", inversions == 0,
            f"strong/adjacent 가 weak/mismatch 보다 모두 상위" if inversions == 0
            else f"도메인 역전 {inversions}건 (역전율 {rate:.0%}) — strong/adjacent 가 weak/mismatch 아래로")

    # 6) primary_domain_available (warning): was any primary-domain JD even selected?
    primary_found = selection.get("primary_domain_jobs_found")
    if primary_found is None:
        add("primary_domain_available", True, "선택 리포트 없음(고정 픽스처일 수 있음) → 평가 불가", na=True)
    else:
        add("primary_domain_available", bool(primary_found),
            "주력 도메인 JD가 풀에서 선택됨" if primary_found
            else "⚠ 라이브 풀에 주력 도메인 JD가 없어 결과가 비대표적일 수 있음")

    # --- aggregate label ---
    statuses = [c["status"] for c in checks]
    label = "fail" if "fail" in statuses else ("warning" if "warning" in statuses else "pass")

    # --- diagnostics surfaced in the summary ---
    invalid_rows = sum(1 for t in tables.values() for row in t.get("rows", []) if row.get("invalid_match"))
    disagreements = [c for c in pairwise.get("comparisons", []) if not c.get("agreed", True)]
    warnings: List[str] = []
    if fetch_failures:
        warnings.append(f"fetch/parse 경고 {len(fetch_failures)}건")
    if (listwise.get("warnings") or {}):
        warnings.append(f"listwise 보정: {list((listwise.get('warnings') or {}).keys())}")
    if primary_found is False:
        warnings.append("주력 도메인 JD 미선택(라이브 풀 제약)")
    if bad:
        warnings.append(f"비추출 인용 {len(bad)}건 잔존")

    return {
        "persona": slug,
        "resume_path": entry.get("resume_path", ""),
        "label": label,
        "n_jobs": n,
        "primary_domains": entry.get("primary_domains", []),
        "secondary_domains": entry.get("secondary_domains", []),
        "selected_role_family_distribution": selection.get("selected_role_family_distribution", {}),
        "top5": [_job_brief(r) for r in ranking[:5]],
        "fit_levels": levels,
        "expected_top_role_families": sorted(expected_top),
        "expected_top_in_top3": bool(expected_top & top3_rf) if (expected_top & present_rf) else None,
        "expected_top_in_top5": bool(expected_top & top5_rf) if (expected_top & present_rf) else None,
        "mismatch_below_nonmismatch": mm_ok,
        "domain_inversion_occurred": (bool(good) and bool(low) and inversions > 0),
        "domain_inversion_count": inversions,
        "non_extractive_removed_count": invalid_rows,
        "surviving_non_extractive_count": len(bad),
        "pairwise_disagreement_count": len(disagreements),
        "checks": checks,
        "warnings": warnings,
    }


def error_summary(slug: str, entry: dict, message: str) -> dict:
    """A summary entry for a persona whose pipeline run failed to produce artifacts."""
    return {
        "persona": slug,
        "resume_path": entry.get("resume_path", "") if entry else "",
        "label": "fail",
        "error": message,
        "checks": [{"invariant": "pipeline_run", "severity": "fail", "status": "fail",
                    "detail": message}],
        "warnings": [message],
        "top5": [],
        "fit_levels": [],
    }


# --------------------------------------------------------------------------- rendering
_LABEL_MARK = {"pass": "✅ pass", "warning": "⚠️ warning", "fail": "❌ fail"}


def build_summary_md(summaries: List[dict], meta: dict) -> str:
    L: List[str] = []
    L.append("# 멀티-이력서 진단 평가 요약 (Multi-resume diagnostic eval)")
    L.append("")
    L.append("> 모든 이력서는 **합성 데이터**입니다. 이 표는 정확도 벤치마크가 아니라 v0 알고리즘의 "
             "**방향성 일반화**를 진단합니다. 라벨: pass / warning / fail (자세한 해석: `docs/EVAL_SUITE.md`).")
    L.append("")
    if meta:
        L.append(f"- 실행 모드: {meta.get('mode', '-')} · pool-size: {meta.get('pool_size', '-')} "
                 f"· limit: {meta.get('limit', '-')} · cache: {meta.get('cache_namespace', '-')}")
        if meta.get("fixture"):
            L.append(f"- 고정 픽스처: `{meta['fixture']}` (모든 페르소나가 동일 JD 셋으로 비교됨)")
        L.append("")

    # overview table
    L.append("## 종합")
    L.append("| 페르소나 | 결과 | JD수 | expected_top@3 | mismatch<non-mm | 도메인역전 | 비추출제거 | pairwise불일치 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for s in summaries:
        if s.get("error"):
            L.append(f"| {s['persona']} | {_LABEL_MARK['fail']} | - | - | - | - | - | 오류: {s['error'][:30]} |")
            continue
        et = s.get("expected_top_in_top3")
        et_s = "n/a" if et is None else ("예" if et else "아니오")
        inv = f"{s['domain_inversion_count']}건" if s.get("domain_inversion_occurred") else "없음"
        L.append(f"| {s['persona']} | {_LABEL_MARK.get(s['label'], s['label'])} | {s.get('n_jobs','-')} "
                 f"| {et_s} | {'예' if s.get('mismatch_below_nonmismatch') else '아니오'} "
                 f"| {inv} | {s.get('non_extractive_removed_count',0)} "
                 f"| {s.get('pairwise_disagreement_count',0)} |")
    L.append("")

    # per persona detail
    for s in summaries:
        L.append("")
        L.append(f"## {s['persona']} — {_LABEL_MARK.get(s['label'], s['label'])}")
        L.append(f"- resume: `{s.get('resume_path','')}`")
        if s.get("error"):
            L.append(f"- ❌ 파이프라인 오류: {s['error']}")
            continue
        L.append(f"- primary_domains: {s.get('primary_domains')} · secondary_domains: {s.get('secondary_domains')}")
        L.append(f"- 선택된 role_family 분포: {s.get('selected_role_family_distribution')}")
        L.append(f"- expected_top_role_families: {s.get('expected_top_role_families')} "
                 f"→ top3 포함: {s.get('expected_top_in_top3')}, top5 포함: {s.get('expected_top_in_top5')}")
        L.append("")
        L.append("| 순위 | 회사 | 포지션 | role_family | domain | 적합도 | 레벨 |")
        L.append("|---|---|---|---|---|---|---|")
        for j in s.get("top5", []):
            L.append(f"| {j['rank']} | {j['company']} | {j['title']} | {j['role_family']} "
                     f"| {j['domain_alignment']} | **{j['fit_level']}** | {j['fit_label']} |")
        L.append("")
        L.append("**불변식:**")
        for c in s.get("checks", []):
            mark = {"pass": "✅", "warning": "⚠️", "fail": "❌", "n/a": "➖"}.get(c["status"], "?")
            L.append(f"- {mark} `{c['invariant']}` ({c['severity']}): {c['detail']}")
        if s.get("warnings"):
            L.append("")
            L.append(f"**경고:** {'; '.join(s['warnings'])}")
    L.append("")
    L.append("---")
    L.append("_이 평가가 증명하지 않는 것: 절대적 fit 정확도, 합격 가능성, 회사별 실제 채용 기준. "
             "방향성(도메인 우선순위·추출형·랭킹 방향)만 진단합니다._")
    return "\n".join(L)


# --------------------------------------------------------------------------- ranking-mode ablation
def _is_mismatch(r: dict) -> bool:
    return r.get("domain_alignment") == "mismatch"


def fit_rank_inversions(ranking: List[dict]) -> List[Tuple[dict, dict]]:
    """Pairs (a, b) where a ranks ABOVE b but has a LOWER fit_level, counted only when a and b are
    in the SAME domain-priority partition (both non-mismatch, or both mismatch). Fewer = the rank
    order tracks the headline fit number more closely (more legible)."""
    out: List[Tuple[dict, dict]] = []
    for i in range(len(ranking)):
        for j in range(i + 1, len(ranking)):
            a, b = ranking[i], ranking[j]  # a is ranked above b
            if _is_mismatch(a) != _is_mismatch(b):
                continue
            if (a.get("fit_level") or 0) < (b.get("fit_level") or 0):
                out.append((a, b))
    return out


_TIER_RANK = {"strong": 3, "adjacent": 2, "weak": 1, "mismatch": 0}


def domain_inversion_count(ranking: List[dict]) -> int:
    """strong/adjacent ranked below weak/mismatch (coarse domain-direction inversion)."""
    good = [r["rank"] for r in ranking if r.get("domain_alignment") in ("strong", "adjacent")]
    low = [r["rank"] for r in ranking if r.get("domain_alignment") in ("weak", "mismatch")]
    return sum(1 for g in good for l in low if g > l)


def tier_inversions(ranking: List[dict]) -> List[Tuple[dict, dict]]:
    """Pairs (a, b) where a ranks ABOVE b but is a STRICTLY LOWER domain tier
    (strong>adjacent>weak>mismatch). Sharper than domain_inversion_count: it also catches
    adjacent-above-strong and weak-above-adjacent, i.e. any role that jumped its domain tier.
    A primary-domain-first ranking should have zero tier inversions."""
    out: List[Tuple[dict, dict]] = []
    for i in range(len(ranking)):
        for j in range(i + 1, len(ranking)):
            a, b = ranking[i], ranking[j]  # a ranked above b
            if _TIER_RANK.get(a.get("domain_alignment"), 1) < _TIER_RANK.get(b.get("domain_alignment"), 1):
                out.append((a, b))
    return out


def mismatch_violation(ranking: List[dict]) -> bool:
    """True if any mismatch role ranks above any non-mismatch role (hard guard must prevent this)."""
    mm = [r["rank"] for r in ranking if _is_mismatch(r)]
    nm = [r["rank"] for r in ranking if not _is_mismatch(r)]
    return bool(mm and nm and min(mm) <= max(nm))


def _cmp_brief(r: dict) -> dict:
    return {"rank": r.get("rank"), "company": r.get("company", ""), "title": r.get("title", ""),
            "role_family": r.get("role_family"), "domain_alignment": r.get("domain_alignment"),
            "fit_level": r.get("fit_level"), "bt_score": r.get("bt_score")}


def _inv_example(a: dict, b: dict) -> str:
    return (f"#{a['rank']}(fit{a['fit_level']},{a['role_family']}/{a['domain_alignment']}) "
            f"> #{b['rank']}(fit{b['fit_level']},{b['role_family']}/{b['domain_alignment']})")


def compare_persona(slug: str, entry: dict, rankings_by_mode: Dict[str, List[dict]],
                    pairwise_disagree: int, modes: List[str]) -> dict:
    """Compare one persona's final orders across N ranking modes (same upstream signals).
    `rankings_by_mode` maps mode → ranking rows. `modes` is the display order."""
    expected_top = set(entry.get("expected_top_role_families", []))
    base = "bt_primary" if "bt_primary" in modes else modes[0]
    present = {r.get("role_family") for r in rankings_by_mode[base]}

    def top3(ranking):
        if not (expected_top & present):
            return None
        return bool(expected_top & {r.get("role_family") for r in ranking[:3]})

    metrics: Dict[str, dict] = {}
    for m in modes:
        rk = rankings_by_mode[m]
        fri, tinv = fit_rank_inversions(rk), tier_inversions(rk)
        metrics[m] = {
            "fit_rank_inversions": len(fri),
            "domain_inversions": domain_inversion_count(rk),
            "tier_inversions": len(tinv),
            "mismatch_violation": mismatch_violation(rk),
            "expected_top_in_top3": top3(rk),
            "fit_rank_inversion_examples": [_inv_example(a, b) for a, b in fri[:4]],
            "tier_inversion_examples": [_inv_example(a, b) for a, b in tinv[:4]],
        }

    # "new obvious misrank" = a mode introduces a domain-tier jump (or mismatch violation) that the
    # current default (base) does not have. This catches fit_primary putting adjacent above strong.
    new_misrank = {m: bool(metrics[m]["tier_inversions"] > metrics[base]["tier_inversions"]
                           or metrics[m]["mismatch_violation"]) for m in modes}

    # jobs whose rank differs across modes
    rank_of = {m: {r["job_id"]: r["rank"] for r in rankings_by_mode[m]} for m in modes}
    base_rows = {r["job_id"]: r for r in rankings_by_mode[base]}
    moved = []
    for jid, r in base_rows.items():
        ranks = {m: rank_of[m].get(jid) for m in modes}
        if len(set(ranks.values())) > 1:
            moved.append({"job_id": jid, "title": r.get("title", ""), "role_family": r.get("role_family"),
                          "domain_alignment": r.get("domain_alignment"), "fit_level": r.get("fit_level"),
                          "ranks": ranks})
    moved.sort(key=lambda mv: mv["ranks"].get(base) or 999)

    return {
        "persona": slug,
        "modes": modes,
        "expected_top_role_families": sorted(expected_top),
        "top6": {m: [_cmp_brief(r) for r in rankings_by_mode[m][:6]] for m in modes},
        "metrics": metrics,
        "moved": moved,
        "pairwise_disagreement_count": pairwise_disagree,
        "new_misrank": new_misrank,
    }


_MODE_LABEL = {"bt_primary": "bt_primary (BT 기준/디버그)", "fit_primary": "fit_primary (fit 정렬)",
               "domain_fit_bt": "domain_fit_bt (기본값)"}


def _cmp_top6_table(rows: List[dict]) -> List[str]:
    L = ["| # | 회사 | 포지션 | role | domain | fit |", "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['rank']} | {r['company']} | {r['title']} | {r['role_family']} "
                 f"| {r['domain_alignment']} | **{r['fit_level']}** |")
    return L


def build_comparison_md(comparisons: List[dict], meta: dict) -> str:
    modes = comparisons[0]["modes"] if comparisons and comparisons[0].get("modes") else \
        ["bt_primary", "fit_primary", "domain_fit_bt"]
    L: List[str] = []
    L.append("# 랭킹 모드 비교 (" + " vs ".join(modes) + ") — ablation")
    L.append("")
    L.append("> 동일한 업스트림 신호(matching/verify/fits/BT/listwise/pairwise) 위에서 **최종 정렬 방식만** "
             "다르게 한 비교입니다. 모든 모드가 도메인 우선순위 가드(mismatch < non-mismatch)를 적용하고, "
             "합격확률/퍼센트는 출력하지 않으며 fit 은 1~5 정수입니다. **기본값은 `domain_fit_bt`** 이며, "
             "`bt_primary`(BT/디버그)와 `fit_primary`(fit 정렬)도 `--ranking-mode` 로 선택할 수 있습니다.")
    L.append("")
    if meta:
        L.append(f"- 모드: {meta.get('mode','-')} · pool-size: {meta.get('pool_size','-')} "
                 f"· limit: {meta.get('limit','-')} · cache: {meta.get('cache_namespace','-')}")
        L.append("")
    L.append("## 지표 정의")
    L.append("- **fit-rank 역전**: 같은 mismatch 파티션 안에서 더 낮은 fit 공고가 더 높은 fit 공고 위에 온 쌍 수 "
             "(작을수록 순위가 headline fit 과 일치 → 가독성↑).")
    L.append("- **tier 역전**: 도메인 tier(strong>adjacent>weak>mismatch)가 더 낮은 공고가 더 높은 tier 공고 위에 온 쌍 수 "
             "(주력 도메인 우선 정렬이면 0; adjacent가 strong 위로 올라가는 것도 잡음).")
    L.append("- **도메인 역전**: strong/adjacent 가 weak/mismatch 아래로 간 쌍 수(거친 지표).")
    L.append("- **mismatch 위반**: mismatch 역할이 non-mismatch 위로 — 어떤 모드에서도 0 이어야 함(하드 가드).")
    L.append("")
    L.append("## 종합 (fit-rank 역전 / tier 역전, 모드 순서: " + " / ".join(modes) + ")")
    header = "| 페르소나 | fit-rank 역전 | tier 역전 | mismatch 위반 | 새 misrank 유발 모드 |"
    L.append(header)
    L.append("|---|---|---|---|---|")
    for c in comparisons:
        if c.get("error"):
            L.append(f"| {c['persona']} | - | - | - | {c['error']} |")
            continue
        met = c["metrics"]
        fr = " / ".join(str(met[m]["fit_rank_inversions"]) for m in modes)
        ti = " / ".join(str(met[m]["tier_inversions"]) for m in modes)
        mv = " / ".join(str(int(met[m]["mismatch_violation"])) for m in modes)
        nm = [m for m in modes if c["new_misrank"].get(m)] or ["없음"]
        L.append(f"| {c['persona']} | {fr} | {ti} | {mv} | {', '.join(nm)} |")
    L.append("")

    for c in comparisons:
        if c.get("error"):
            L.append(f"## {c['persona']} — 오류: {c['error']}")
            L.append("")
            continue
        met = c["metrics"]
        L.append(f"## {c['persona']}")
        L.append(f"- expected_top_role_families: {c['expected_top_role_families']} → top3 포함: "
                 + ", ".join(f"{m}={met[m]['expected_top_in_top3']}" for m in modes))
        L.append(f"- pairwise 불일치: {c['pairwise_disagreement_count']}")
        L.append("- 지표(mode: fit-rank / tier / domain / mismatch):")
        for m in modes:
            L.append(f"  - **{_MODE_LABEL.get(m, m)}**: {met[m]['fit_rank_inversions']} / "
                     f"{met[m]['tier_inversions']} / {met[m]['domain_inversions']} / "
                     f"{int(met[m]['mismatch_violation'])}")
        L.append("")
        for m in modes:
            L.append(f"**Top 6 — {_MODE_LABEL.get(m, m)}:**")
            L.extend(_cmp_top6_table(c["top6"][m]))
            L.append("")
        if c["moved"]:
            L.append("**모드 간 순위가 다른 공고 (" + " / ".join(modes) + "):**")
            for mv in c["moved"]:
                ranks = " / ".join(f"#{mv['ranks'][m]}" for m in modes)
                L.append(f"- {mv['title']} ({mv['role_family']}/{mv['domain_alignment']}, fit {mv['fit_level']}): {ranks}")
        else:
            L.append("**모드 간 순위가 다른 공고:** 없음 (세 모드 동일)")
        for m in modes:
            exs = met[m]["tier_inversion_examples"]
            if exs:
                L.append("")
                L.append(f"{m} tier 역전 예 (낮은 tier 가 높은 tier 위):")
                for ex in exs:
                    L.append(f"  - {ex}")
        L.append("")
    L.append("---")
    L.append("_이 비교는 최종 정렬 방식만 평가합니다. 기본값은 ablation 결과에 따라 domain_fit_bt 입니다 "
             "(bt_primary·fit_primary 도 --ranking-mode 로 선택 가능)._")
    return "\n".join(L)
