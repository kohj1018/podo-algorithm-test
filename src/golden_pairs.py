"""Human-labeled golden-pair evaluation (the FIRST real ranking-accuracy eval).

Everything else in this repo measures *direction* and *legibility*:
  - the fixture regression (`src/main.py::_check_invariants`) checks coarse invariants on ONE set,
  - the multi-resume suite (`src/eval_resumes.py`) checks domain-priority / extractive / scale
    invariants across personas,
  - the ranking-mode ablation checks fit-vs-rank / tier inversions.
None of those answer "does the system put the *better-fit* job above the worse one on a hard,
genuinely-close pair?" — because there is no ground truth to compare against. This module adds that
ground truth: a small set of **human-labeled pairs** (A_better / B_better / tie / unsure) and
measures the system's agreement with the human.

It does NOT touch the ranking algorithm and it does NOT call the LLM. Both entry points read back
ONLY the artifacts the pipeline already wrote into `outputs/eval/<persona>/` (the per-mode
`final_ranking_*.json` files + `pairwise_comparisons.json`). If a labeled job is missing from those
artifacts, the pair is reported as *unavailable* — never silently re-fetched.

Pure functions only — this module never imports `main`, so the CLI imports it without a cycle.
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple

from . import rank_aggregate
from .models import MatchingTable

# The three final-order modes (must mirror rank_aggregate.RANKING_MODES). domain_fit_bt is the
# product default and therefore the headline mode for accuracy.
MODES = ("bt_primary", "fit_primary", "domain_fit_bt")
DEFAULT_MODE = "domain_fit_bt"

# Human labels and the engineering-domain families used by the propose heuristics.
LABELS = ("A_better", "B_better", "tie", "unsure")
DIFFICULTIES = ("easy", "medium", "hard")
CATEGORIES = (
    "same_domain_close",            # same role_family + tier, near-identical — which fit wins?
    "adjacent_vs_primary",          # adjacent-domain role vs primary-domain role (does primary win?)
    "seniority_gap",                # same domain, one has an experience_level prerequisite gap
    "domain_transfer",              # different engineering families (e.g. backend vs ml_ai)
    "tool_stack_gap",               # same role, differ mainly by tool/framework coverage
    "product_duty_vs_prerequisite", # a gap that is a product duty vs a true prerequisite
    "weak_vs_adjacent",             # a weak-domain role vs an adjacent-domain role
    "mismatch_guard",               # mismatch (marketing/design/product) vs an engineering role
)
_LABEL_TO_LETTER = {"A_better": "A", "B_better": "B", "tie": "tie", "unsure": "unsure"}
_ENG_FAMILIES = {"frontend", "backend", "fullstack", "devops_infra", "ml_ai", "data",
                 "security", "android", "ios", "web", "mobile"}


# --------------------------------------------------------------------------- artifact loading
def _read_json(p: Path):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else None
    except Exception:  # noqa: BLE001
        return None


def _job_meta(r: dict) -> dict:
    """Flatten one final_ranking row into the fields the eval/propose logic needs."""
    cov = r.get("coverage", {}) or {}
    weak = r.get("weak_or_missing", []) or []
    cap = str(cov.get("cap_reason", "") or "")
    return {
        "job_id": r.get("job_id"),
        "title": r.get("title", ""),
        "company": r.get("company", ""),
        "role_family": r.get("role_family", "other"),
        "domain_alignment": r.get("domain_alignment", "weak"),
        "fit_level": r.get("fit_level"),
        "bt_score": r.get("bt_score", 0.0) or 0.0,
        "rank": r.get("rank"),
        # seniority signal: an unmet experience_level prerequisite, or an experience-related cap.
        "experience_gap": any("experience_level" in str(w) for w in weak) or ("experience" in cap),
        "product_duties": r.get("product_duties", []) or [],
        "cap_reason": cap,
    }


def load_persona_artifacts(eval_root: Path, persona: str) -> dict:
    """Read one persona's per-mode rankings + pairwise from outputs/eval/<persona>/.
    Returns a dict with available=False (and no jobs) if nothing usable was written."""
    d = Path(eval_root) / persona
    rankings_by_mode: Dict[str, List[dict]] = {}
    for m in MODES:
        data = _read_json(d / f"final_ranking_{m}.json")
        if data and data.get("ranking"):
            rankings_by_mode[m] = data["ranking"]
    # Fallback: the primary report file IS the default mode (domain_fit_bt).
    if DEFAULT_MODE not in rankings_by_mode:
        data = _read_json(d / "final_ranking.json")
        if data and data.get("ranking"):
            rankings_by_mode[DEFAULT_MODE] = data["ranking"]

    base = rankings_by_mode.get(DEFAULT_MODE) or next(iter(rankings_by_mode.values()), [])
    jobs = {r["job_id"]: _job_meta(r) for r in base}
    pairwise = _read_json(d / "pairwise_comparisons.json") or {}
    return {
        "persona": persona,
        "dir": str(d),
        "available": bool(rankings_by_mode),
        "modes_present": [m for m in MODES if m in rankings_by_mode],
        "rankings_by_mode": rankings_by_mode,
        "jobs": jobs,
        "pairwise": pairwise,
    }


def rescore_persona(eval_root: Path, persona: str, scoring_mode: str = "baseline") -> dict:
    """Recompute per-mode rankings for one persona from CACHED artifacts under a scoring mode,
    WITHOUT calling the LLM. Reuses rank_aggregate.compute_fit (+ dedup flag) and
    rank_aggregate.aggregate, so the ranking logic is identical to production — only the fit caps
    differ between baseline and dedup. Returns the same shape as load_persona_artifacts (so
    evaluate_pairs can consume it) plus a 'dedup_audit' map of duplicate groups found per job."""
    d = Path(eval_root) / persona
    fr = _read_json(d / "final_ranking.json") or {}
    meta = {r["job_id"]: r for r in fr.get("ranking", [])}
    tbls = _read_json(d / "matching_tables.json") or {}
    listwise = _read_json(d / "listwise.json") or {}
    pw = _read_json(d / "pairwise_comparisons.json") or {}
    jobs_json = _read_json(d / "jobs_parsed.json") or []

    if not (meta and tbls and listwise):
        return {"persona": persona, "available": False, "modes_present": [], "scoring_mode": scoring_mode,
                "rankings_by_mode": {}, "jobs": {}, "pairwise": pw, "dedup_audit": {},
                "rescore_error": "필수 캐시 산출물 누락(final_ranking/matching_tables/listwise)"}

    jobs_by_id = {j["job_id"]: SimpleNamespace(
        company=j.get("company", ""), title=j.get("title", ""), url=j.get("url", ""),
        role_family=j.get("role_family", "other")) for j in jobs_json if j.get("job_id")}
    for jid, m in meta.items():
        jobs_by_id.setdefault(jid, SimpleNamespace(
            company=m.get("company", ""), title=m.get("title", ""), url=m.get("url", ""),
            role_family=m.get("role_family", "other")))

    dedup = (scoring_mode == "dedup_required_preferred")
    tables_by_id, fits, domain_ctx, dedup_audit = {}, {}, {}, {}
    for jid, tj in tbls.items():
        try:
            tbl = MatchingTable(**tj)
        except Exception:  # noqa: BLE001
            continue
        align = meta.get(jid, {}).get("domain_alignment", "weak")
        tables_by_id[jid] = tbl
        domain_ctx[jid] = {
            "role_family": meta.get(jid, {}).get("role_family",
                                                 getattr(jobs_by_id.get(jid), "role_family", "other")),
            "domain_alignment": align,
            "domain_alignment_reason": meta.get(jid, {}).get("domain_alignment_reason", ""),
        }
        f = rank_aggregate.compute_fit(tbl, align, dedup_required_preferred=dedup)
        fits[jid] = f
        if f.get("dedup_audit"):
            dedup_audit[jid] = f["dedup_audit"]

    pairwise = [SimpleNamespace(job_a=c.get("job_a"), job_b=c.get("job_b"), outcome=c.get("outcome"))
                for c in (pw.get("comparisons") or [])]
    cand = [x.get("job_id") for x in ((pw.get("candidate_set") or {}).get("pairwise_candidate_set") or [])
            if x.get("job_id")]

    rankings_by_mode: Dict[str, List[dict]] = {}
    for mode in rank_aggregate.RANKING_MODES:
        try:
            results, _bt, _guard = rank_aggregate.aggregate(
                jobs_by_id, tables_by_id, listwise, pairwise, cand, fits, domain_ctx, ranking_mode=mode)
            rankings_by_mode[mode] = [r.model_dump() for r in results]
        except Exception:  # noqa: BLE001
            rankings_by_mode[mode] = []
    base = rankings_by_mode.get(DEFAULT_MODE) or next((v for v in rankings_by_mode.values() if v), [])
    return {
        "persona": persona, "available": bool(base), "scoring_mode": scoring_mode,
        "modes_present": [m for m in rank_aggregate.RANKING_MODES if rankings_by_mode.get(m)],
        "rankings_by_mode": rankings_by_mode,
        "jobs": {r["job_id"]: _job_meta(r) for r in base},
        "pairwise": pw, "dedup_audit": dedup_audit,
    }


def _compared_ids(pairwise: dict) -> set:
    """Job ids that actually received pairwise (Bradley-Terry) comparison."""
    cs = (pairwise or {}).get("candidate_set", {}) or {}
    return {x.get("job_id") for x in cs.get("pairwise_candidate_set", []) if x.get("job_id")}


def _winner(rankmap: Dict[str, int], a_id: str, b_id: str) -> Optional[str]:
    ra, rb = rankmap.get(a_id), rankmap.get(b_id)
    if ra is None or rb is None:
        return None
    return "A" if ra < rb else "B"


def system_winner(rankings_by_mode: Dict[str, List[dict]], mode: str,
                  a_id: str, b_id: str) -> Optional[str]:
    """Which job the system ranks HIGHER (lower rank number) under `mode`. None if either is absent."""
    rk = {r["job_id"]: r["rank"] for r in rankings_by_mode.get(mode, [])}
    return _winner(rk, a_id, b_id)


# --------------------------------------------------------------------------- pair loading
def load_pairs(path: Path) -> Tuple[List[dict], List[str]]:
    """Load + validate a golden-pairs file. Accepts a top-level list or {"pairs": [...]}.
    Returns (valid_pairs, errors, unlabeled). `unlabeled` holds pairs that are structurally fine
    but whose expected_winner is still blank/placeholder — these are NOT errors (the human just
    hasn't labeled them yet); the caller decides whether to skip them or fail. Other malformed pairs
    are skipped with an error message (lenient)."""
    raw = _read_json(path)
    errors: List[str] = []
    unlabeled: List[str] = []
    if raw is None:
        return [], [f"파일을 읽을 수 없거나 JSON이 아님: {path}"], []
    items = raw.get("pairs") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return [], [f"최상위가 리스트도 아니고 'pairs' 배열도 없음: {path}"], []

    core = ("pair_id", "persona", "job_a_id", "job_b_id")  # expected_winner handled separately
    valid: List[dict] = []
    seen_ids = set()
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            errors.append(f"[{i}] 객체가 아님 — 건너뜀")
            continue
        miss = [k for k in core if not it.get(k)]
        if miss:
            errors.append(f"[{i}] 필수 필드 누락 {miss} — 건너뜀")
            continue
        pid = it["pair_id"]
        if pid in seen_ids:
            errors.append(f"[{pid}] pair_id 중복 — 건너뜀")
            continue
        seen_ids.add(pid)
        if it["job_a_id"] == it["job_b_id"]:
            errors.append(f"[{pid}] job_a_id == job_b_id — 건너뜀")
            continue
        # blank / placeholder expected_winner = "not yet labeled" (distinct from an error)
        ew = str(it.get("expected_winner") or "").strip()
        if ew == "" or ew in ("____", "TODO", "TBD", "?"):
            unlabeled.append(pid)
            continue
        if ew not in LABELS:
            errors.append(f"[{pid}] expected_winner '{ew}' 가 {LABELS} 중 하나가 아님 — 건너뜀")
            continue
        cat = it.get("category")
        if cat and cat not in CATEGORIES:
            errors.append(f"[{pid}] 알 수 없는 category '{cat}' (계속 진행, 'uncategorized' 처리)")
            it = {**it, "category": "uncategorized"}
        diff = it.get("difficulty")
        if diff and diff not in DIFFICULTIES:
            errors.append(f"[{pid}] 알 수 없는 difficulty '{diff}' (계속 진행, 'medium' 처리)")
            it = {**it, "difficulty": "medium"}
        valid.append(it)
    return valid, errors, unlabeled


# --------------------------------------------------------------------------- evaluation
def _stub(job_id, title, company) -> dict:
    return {"job_id": job_id, "title": title or "?", "company": company or "?",
            "role_family": "?", "domain_alignment": "?", "fit_level": None, "bt_score": 0.0,
            "rank": None}


def evaluate_pairs(pairs: List[dict], artifacts_by_persona: Dict[str, dict],
                   modes: List[str]) -> List[dict]:
    """Evaluate each labeled pair against the cached artifacts under every available mode.
    Never fetches: a pair whose persona/job is absent is marked available=False."""
    results: List[dict] = []
    for p in pairs:
        persona = p["persona"]
        a_id, b_id = p["job_a_id"], p["job_b_id"]
        expected_label = p["expected_winner"]
        expected = _LABEL_TO_LETTER.get(expected_label)
        base = {
            "pair_id": p["pair_id"], "persona": persona,
            "category": p.get("category", "uncategorized"),
            "difficulty": p.get("difficulty", "medium"),
            "expected": expected, "expected_label": expected_label,
            "label_reason": p.get("label_reason", ""),
        }
        art = artifacts_by_persona.get(persona)
        if art is None or not art.get("available"):
            results.append({**base, "available": False, "near_tie": None, "per_mode": {},
                            "unavailable_reason": f"persona '{persona}' 산출물 없음 "
                                                  f"(outputs/eval/{persona}/ 비어있음 — 먼저 eval-resumes 실행)",
                            "job_a": _stub(a_id, p.get("job_a_title"), p.get("job_a_company")),
                            "job_b": _stub(b_id, p.get("job_b_title"), p.get("job_b_company"))})
            continue
        ja, jb = art["jobs"].get(a_id), art["jobs"].get(b_id)
        missing = [jid for jid, jm in ((a_id, ja), (b_id, jb)) if jm is None]
        if missing:
            results.append({**base, "available": False, "near_tie": None, "per_mode": {},
                            "unavailable_reason": f"공고 {missing} 가 {persona} 산출물에 없음 "
                                                  f"(재수집하지 않음 — unavailable 처리)",
                            "job_a": ja or _stub(a_id, p.get("job_a_title"), p.get("job_a_company")),
                            "job_b": jb or _stub(b_id, p.get("job_b_title"), p.get("job_b_company"))})
            continue

        per_mode: Dict[str, dict] = {}
        for m in modes:
            if m not in art["rankings_by_mode"]:
                per_mode[m] = {"winner": None, "rank_a": None, "rank_b": None,
                               "correct": None, "note": "mode 산출물 없음"}
                continue
            rk = {r["job_id"]: r["rank"] for r in art["rankings_by_mode"][m]}
            w = _winner(rk, a_id, b_id)
            correct = (w == expected) if (expected in ("A", "B") and w) else None
            per_mode[m] = {"winner": w, "rank_a": rk.get(a_id), "rank_b": rk.get(b_id),
                           "correct": correct}
        near_tie = (ja["fit_level"] == jb["fit_level"])  # system "tie" signal on the 1-5 scale
        results.append({**base, "available": True, "unavailable_reason": None,
                        "job_a": ja, "job_b": jb, "per_mode": per_mode, "near_tie": near_tie})
    return results


def _ratio(correct: int, total: int):
    return None if total == 0 else round(correct / total, 4)


def _pair_ref(r: dict) -> dict:
    return {"pair_id": r["pair_id"], "persona": r["persona"], "category": r["category"],
            "difficulty": r["difficulty"], "expected_winner": r["expected_label"],
            "job_a": f"{r['job_a']['company']} — {r['job_a']['title']}",
            "job_b": f"{r['job_b']['company']} — {r['job_b']['title']}"}


def aggregate_metrics(results: List[dict], modes: List[str]) -> dict:
    """Roll evaluated pairs up into accuracy metrics, breakdowns, and disagreement lists.

    - pairwise accuracy (strict): over DECISIVE pairs (A_better/B_better) with both jobs available;
      correct = the mode ranks the human-preferred job higher.
    - tie-aware accuracy: also counts `tie` pairs; a tie is 'correct' when the system shows a
      near-tie (equal fit_level), i.e. it did NOT manufacture a strong distinction humans don't see.
    - `unsure` pairs are NEVER scored (reported only).
    Breakdowns (persona/difficulty/category) use the headline mode (domain_fit_bt)."""
    headline = DEFAULT_MODE if DEFAULT_MODE in modes else (modes[0] if modes else DEFAULT_MODE)
    avail = [r for r in results if r["available"]]

    per_mode: Dict[str, dict] = {}
    for m in modes:
        decisive = [r for r in avail if r["expected"] in ("A", "B") and r["per_mode"].get(m, {}).get("winner")]
        correct = sum(1 for r in decisive if r["per_mode"][m]["winner"] == r["expected"])
        ties = [r for r in avail if r["expected"] == "tie"]
        tie_correct = sum(1 for r in ties if r["near_tie"])
        per_mode[m] = {
            "strict_correct": correct, "strict_total": len(decisive),
            "strict_acc": _ratio(correct, len(decisive)),
            "tie_aware_correct": correct + tie_correct, "tie_aware_total": len(decisive) + len(ties),
            "tie_aware_acc": _ratio(correct + tie_correct, len(decisive) + len(ties)),
        }

    def breakdown(keyfn) -> Dict[str, dict]:
        groups: Dict[str, List[int]] = {}
        for r in avail:
            if r["expected"] not in ("A", "B"):
                continue
            w = r["per_mode"].get(headline, {}).get("winner")
            if not w:
                continue
            g = groups.setdefault(keyfn(r), [0, 0])
            g[1] += 1
            if w == r["expected"]:
                g[0] += 1
        return {k: {"correct": v[0], "total": v[1], "acc": _ratio(v[0], v[1])}
                for k, v in sorted(groups.items())}

    # mode disagreements: the available modes don't all agree on the winner
    disagreements = []
    for r in avail:
        winners = {m: r["per_mode"].get(m, {}).get("winner") for m in modes}
        distinct = {w for w in winners.values() if w}
        if len(distinct) > 1:
            disagreements.append({**_pair_ref(r), "winners": winners})

    # system disagrees with the human (headline mode, decisive only) — the key "where to improve" list
    mismatches = []
    for r in avail:
        if r["expected"] not in ("A", "B"):
            continue
        w = r["per_mode"].get(headline, {}).get("winner")
        if w and w != r["expected"]:
            mismatches.append({
                **_pair_ref(r), "headline_winner": w, "expected": r["expected"],
                "fit_a": r["job_a"]["fit_level"], "fit_b": r["job_b"]["fit_level"],
                "winners": {m: r["per_mode"].get(m, {}).get("winner") for m in modes},
                "label_reason": r.get("label_reason", ""),
            })

    unavailable = [{**_pair_ref(r), "reason": r["unavailable_reason"]}
                   for r in results if not r["available"]]
    unsure = [_pair_ref(r) for r in results if r["expected"] == "unsure"]

    label_counts: Dict[str, int] = {}
    for r in results:
        label_counts[r["expected_label"]] = label_counts.get(r["expected_label"], 0) + 1

    return {
        "headline_mode": headline,
        "modes": modes,
        "n_pairs": len(results),
        "n_available": len(avail),
        "n_unavailable": len(results) - len(avail),
        "label_counts": label_counts,
        "per_mode": per_mode,
        "by_persona": breakdown(lambda r: r["persona"]),
        "by_difficulty": breakdown(lambda r: r["difficulty"]),
        "by_category": breakdown(lambda r: r["category"]),
        "mode_disagreements": disagreements,
        "system_vs_human": mismatches,
        "unavailable": unavailable,
        "unsure": unsure,
    }


# --------------------------------------------------------------------------- report rendering
def _md_cell(s) -> str:
    """Make a value safe inside a markdown table cell: escape pipes (job titles like
    'Frontend | 커머스' otherwise add phantom columns) and flatten newlines."""
    return str("" if s is None else s).replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def _acc_cell(d: dict, key_correct: str, key_total: str, key_acc: str) -> str:
    acc = d.get(key_acc)
    if acc is None:
        return "n/a"
    return f"{d[key_correct]}/{d[key_total]} ({acc*100:.0f}%)"


def build_report_md(metrics: dict, results: List[dict], meta: dict) -> str:
    L: List[str] = []
    modes = metrics["modes"]
    headline = metrics["headline_mode"]
    L.append("# 골든 페어 평가 — 사람이 라벨링한 랭킹 정확도 (Golden-pair accuracy eval)")
    L.append("")
    L.append("> 이 평가는 프로젝트에서 **처음으로 '정확도'를 측정**합니다. 다른 평가(불변식 회귀, "
             "멀티-페르소나 진단, 랭킹 모드 ablation)는 *방향성*과 *가독성*만 봅니다. 여기서는 사람이 "
             "직접 라벨링한 쌍(A_better / B_better / tie / unsure)과 시스템의 순위를 비교합니다. "
             "랭킹 알고리즘은 변경하지 않으며, LLM도 호출하지 않고 `outputs/eval/<persona>/` 의 "
             "기존 산출물만 읽습니다. (여기 정확도 %는 *평가 내부 지표*이며, 제품의 fit/합격확률이 아닙니다.)")
    L.append("")
    if meta:
        L.append(f"- pairs 파일: `{meta.get('pairs_path','-')}` · 산출물 루트: `{meta.get('eval_root','-')}`")
        L.append(f"- 평가 모드: {modes} · 헤드라인(기본값): **{headline}**")
    L.append(f"- 라벨 분포: {metrics['label_counts']}")
    L.append(f"- 총 {metrics['n_pairs']}쌍 중 평가가능 {metrics['n_available']}쌍, "
             f"unavailable {metrics['n_unavailable']}쌍")
    L.append("")

    L.append("## 1) 정확도 (모드별)")
    L.append("- **pairwise(strict)**: A_better/B_better 라벨만 분모. 시스템이 사람이 고른 쪽을 더 위에 두면 정답.")
    L.append("- **tie-aware**: tie 라벨도 포함. tie 는 시스템이 둘을 near-tie(같은 fit_level)로 보면 정답 처리.")
    L.append("- `unsure` 는 점수에서 제외(아래 목록에만 표기).")
    L.append("")
    L.append("| 모드 | pairwise(strict) | tie-aware |")
    L.append("|---|---|---|")
    for m in modes:
        d = metrics["per_mode"][m]
        star = " ⭐" if m == headline else ""
        L.append(f"| {m}{star} | {_acc_cell(d,'strict_correct','strict_total','strict_acc')} "
                 f"| {_acc_cell(d,'tie_aware_correct','tie_aware_total','tie_aware_acc')} |")
    L.append("")

    def breakdown_table(title: str, bd: dict):
        L.append(f"## {title} (헤드라인 모드 `{headline}`, decisive 쌍)")
        if not bd:
            L.append("_decisive 쌍 없음._")
            L.append("")
            return
        L.append("| 그룹 | 정확도 |")
        L.append("|---|---|")
        for k, v in bd.items():
            acc = "n/a" if v["acc"] is None else f"{v['correct']}/{v['total']} ({v['acc']*100:.0f}%)"
            L.append(f"| {k} | {acc} |")
        L.append("")

    breakdown_table("2) 페르소나별 정확도", metrics["by_persona"])
    breakdown_table("3) 난이도별 정확도", metrics["by_difficulty"])
    breakdown_table("4) 카테고리별 정확도", metrics["by_category"])

    L.append("## 5) 모드 간 불일치 (같은 쌍을 모드마다 다르게 정렬)")
    if not metrics["mode_disagreements"]:
        L.append("_없음 — 모든 평가가능 쌍에서 세 모드가 같은 순서._")
    else:
        L.append("| pair_id | persona | A | B | " + " | ".join(modes) + " |")
        L.append("|---|---|---|---|" + "---|" * len(modes))
        for d in metrics["mode_disagreements"]:
            ws = " | ".join(str(d["winners"].get(m) or "-") for m in modes)
            L.append(f"| {_md_cell(d['pair_id'])} | {_md_cell(d['persona'])} | "
                     f"{_md_cell(d['job_a'])} | {_md_cell(d['job_b'])} | {ws} |")
    L.append("")

    L.append("## 6) 시스템 ≠ 사람 (헤드라인 모드 오답 — 개선 후보)")
    if not metrics["system_vs_human"]:
        L.append("_없음 — 헤드라인 모드가 모든 decisive 쌍에서 사람 라벨과 일치._")
    else:
        L.append("| pair_id | persona | 카테고리 | 사람 | 시스템 | A(fit) | B(fit) | 모드별 | 라벨 사유 |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for d in metrics["system_vs_human"]:
            ws = " ".join(f"{m}={d['winners'].get(m) or '-'}" for m in modes)
            L.append(f"| {_md_cell(d['pair_id'])} | {_md_cell(d['persona'])} | {_md_cell(d['category'])} | "
                     f"{_md_cell(d['expected_winner'])} | {_md_cell(d['headline_winner'])} | "
                     f"{_md_cell(d['job_a'])} (fit{d['fit_a']}) | {_md_cell(d['job_b'])} (fit{d['fit_b']}) "
                     f"| {ws} | {_md_cell(d.get('label_reason'))} |")
    L.append("")

    if metrics["unsure"]:
        L.append("## 7) unsure (점수 제외)")
        for d in metrics["unsure"]:
            L.append(f"- {_md_cell(d['pair_id'])} ({_md_cell(d['persona'])}): "
                     f"{_md_cell(d['job_a'])} vs {_md_cell(d['job_b'])}")
        L.append("")
    if metrics["unavailable"]:
        L.append("## 8) unavailable (산출물에 없음 — 재수집 안 함)")
        for d in metrics["unavailable"]:
            L.append(f"- {d['pair_id']} ({d['persona']}): {d['reason']}")
        L.append("")

    L.append("---")
    L.append("_정확도 %는 이 평가의 내부 지표(시스템 vs 사람 라벨 일치율)이며, 제품이 노출하는 적합도(1~5)나 "
             "합격 가능성과는 무관합니다. N이 작을 때 한두 쌍이 %를 크게 흔들 수 있으니 분자/분모를 함께 보세요._")
    return "\n".join(L)


# --------------------------------------------------------------------------- proposing (no labels)
def _eng(rf: str) -> bool:
    return rf in _ENG_FAMILIES


def _score_candidate(a: dict, b: dict, modes: List[str],
                     rankmaps: Dict[str, Dict[str, int]], compared: set) -> dict:
    """Decide whether (a, b) is a useful HARD pair to hand a human, and why.
    Returns {} if nothing fired. Never assigns a label — only a category + difficulty hint."""
    reasons: List[str] = []
    cats: List[Tuple[str, int]] = []  # (category, hardness weight)
    fa, fb = a["fit_level"] or 0, b["fit_level"] or 0
    dfit = abs(fa - fb)
    same_rf = a["role_family"] == b["role_family"]
    same_tier = a["domain_alignment"] == b["domain_alignment"]
    tiers = {a["domain_alignment"], b["domain_alignment"]}
    mm_a, mm_b = a["domain_alignment"] == "mismatch", b["domain_alignment"] == "mismatch"

    # H1 — same role_family + same tier + near-identical fit: which fit truly wins?
    if same_rf and same_tier and dfit <= 1 and not (mm_a or mm_b):
        reasons.append(f"같은 role_family({a['role_family']}) · 같은 도메인 tier({a['domain_alignment']}) · "
                       f"근접 fit(Δ{dfit})")
        cats.append(("same_domain_close", 2 if dfit == 0 else 1))

    # H2 — adjacent-domain role whose fit is >= a primary(strong)-domain role: does primary still win?
    if tiers == {"strong", "adjacent"}:
        strong_job = a if a["domain_alignment"] == "strong" else b
        adj_job = b if strong_job is a else a
        if (adj_job["fit_level"] or 0) >= (strong_job["fit_level"] or 0):
            harder = (adj_job["fit_level"] or 0) > (strong_job["fit_level"] or 0)
            reasons.append(f"주력(strong, fit{strong_job['fit_level']}) vs 인접(adjacent, "
                           f"fit{adj_job['fit_level']}) — 주력 도메인이 그래도 위여야 하나?")
            cats.append(("adjacent_vs_primary", 3 if harder else 2))

    # H2b — weak vs adjacent (both non-primary): a coarser domain-distance call.
    if tiers == {"weak", "adjacent"}:
        reasons.append("weak 도메인 vs 인접(adjacent) 도메인 — 도메인 거리 판단")
        cats.append(("weak_vs_adjacent", 1))

    # H3 — same tier but exactly one has an experience_level prerequisite gap (seniority is the axis).
    if same_tier and (a["experience_gap"] != b["experience_gap"]) and not (mm_a or mm_b):
        reasons.append("같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손")
        cats.append(("seniority_gap", 2))

    # H4 — the default mode and the BT-primary mode order this pair in OPPOSITE directions.
    if "domain_fit_bt" in rankmaps and "bt_primary" in rankmaps:
        w_d = _winner(rankmaps["domain_fit_bt"], a["job_id"], b["job_id"])
        w_b = _winner(rankmaps["bt_primary"], a["job_id"], b["job_id"])
        if w_d and w_b and w_d != w_b:
            reasons.append("domain_fit_bt 와 bt_primary 가 이 쌍을 서로 반대로 정렬")
            cat = "same_domain_close" if same_rf else (
                "adjacent_vs_primary" if tiers == {"strong", "adjacent"} else "domain_transfer")
            cats.append((cat, 3))

    # H5 — headline fit and the pairwise Bradley-Terry order disagree (both pairwise-compared).
    if a["job_id"] in compared and b["job_id"] in compared:
        bta, btb = a["bt_score"] or 0.0, b["bt_score"] or 0.0
        if (fa > fb and bta < btb) or (fb > fa and btb < bta):
            reasons.append(f"headline fit 과 Bradley-Terry 순서가 불일치 "
                           f"(fit {fa}/{fb}, BT {bta:.2f}/{btb:.2f})")
            cats.append(("same_domain_close" if same_rf else "domain_transfer", 3))

    # H6 — same company, similar/cross roles (an apples-to-apples real-world choice).
    if a["company"] == b["company"] and dfit <= 2 and not (mm_a or mm_b):
        if same_rf:
            reasons.append(f"동일 회사({a['company']}) 같은 직군 비교")
            cats.append(("same_domain_close", 1))
        elif _eng(a["role_family"]) and _eng(b["role_family"]):
            reasons.append(f"동일 회사({a['company']}) 유사/인접 직군 비교")
            cat = "adjacent_vs_primary" if tiers == {"strong", "adjacent"} else "domain_transfer"
            cats.append((cat, 1))

    # H7 — mismatch vs a weak non-mismatch engineering role: a guard sanity pair (low priority).
    if mm_a != mm_b:
        nonmm = b if mm_a else a
        if (nonmm["fit_level"] or 0) <= 2:
            reasons.append("mismatch 역할 vs 약한 non-mismatch 역할 — 도메인 가드 sanity")
            cats.append(("mismatch_guard", 0))

    if not reasons:
        return {}
    cats.sort(key=lambda x: -x[1])
    hardness = sum(w for _, w in cats)
    difficulty = "hard" if hardness >= 3 else ("medium" if hardness == 2 else "easy")
    return {"reasons": reasons, "category": cats[0][0], "hardness": hardness, "difficulty": difficulty}


def _make_candidate(persona: str, ja: dict, jb: dict, res: dict,
                    modes: List[str], rankmaps: Dict[str, Dict[str, int]]) -> dict:
    rank_by_mode: Dict[str, dict] = {}
    winners = set()
    for m in modes:
        ra, rb = rankmaps[m].get(ja["job_id"]), rankmaps[m].get(jb["job_id"])
        w = ("A" if ra < rb else "B") if (ra is not None and rb is not None) else None
        rank_by_mode[m] = {"a": ra, "b": rb, "winner": w}
        if w:
            winners.add(w)
    return {
        "pair_id": None,  # assigned after global ordering
        "persona": persona,
        "resume_path": f"data/eval/resumes/{persona}.md",
        "job_a_id": ja["job_id"], "job_a_title": ja["title"], "job_a_company": ja["company"],
        "job_b_id": jb["job_id"], "job_b_title": jb["title"], "job_b_company": jb["company"],
        "expected_winner": "",   # UNLABELED — to be filled by a human
        "label_reason": "",       # UNLABELED
        "difficulty": res["difficulty"],
        "category": res["category"],
        "_proposed_reasons": res["reasons"],
        "_hardness": res["hardness"],
        "_system_view": {
            "role_family_a": ja["role_family"], "role_family_b": jb["role_family"],
            "domain_a": ja["domain_alignment"], "domain_b": jb["domain_alignment"],
            "fit_a": ja["fit_level"], "fit_b": jb["fit_level"],
            "bt_a": round(ja["bt_score"] or 0.0, 4), "bt_b": round(jb["bt_score"] or 0.0, 4),
            "rank_by_mode": rank_by_mode,
            "modes_disagree": len(winners) > 1,
        },
    }


def propose_pairs(artifacts_by_persona: Dict[str, dict], max_pairs: int = 50) -> Tuple[List[dict], dict]:
    """Surface hard candidate pairs for HUMAN labeling. Does not label anything.
    Orders A = the job the default mode ranks higher, so 'A_better' means the system agrees."""
    cand: Dict[tuple, dict] = {}
    stats = {"per_persona": {}, "per_category": {}}
    for persona, art in sorted(artifacts_by_persona.items()):
        if not art.get("available"):
            stats["per_persona"][persona] = "unavailable"
            continue
        modes = art["modes_present"]
        default_mode = DEFAULT_MODE if DEFAULT_MODE in modes else (modes[0] if modes else None)
        if not default_mode:
            stats["per_persona"][persona] = "no-modes"
            continue
        rankmaps = {m: {r["job_id"]: r["rank"] for r in art["rankings_by_mode"][m]} for m in modes}
        drank = rankmaps[default_mode]
        compared = _compared_ids(art["pairwise"])
        jobs = list(art["jobs"].values())
        found = 0
        for a, b in combinations(jobs, 2):
            res = _score_candidate(a, b, modes, rankmaps, compared)
            if not res:
                continue
            # order so A = higher default rank (lower rank number)
            ja, jb = (a, b) if drank.get(a["job_id"], 999) <= drank.get(b["job_id"], 999) else (b, a)
            key = (persona, frozenset((a["job_id"], b["job_id"])))
            cand[key] = _make_candidate(persona, ja, jb, res, modes, rankmaps)
            found += 1
        stats["per_persona"][persona] = found

    ordered = sorted(cand.values(),
                     key=lambda c: (-c["_hardness"], c["persona"], c["job_a_id"], c["job_b_id"]))
    total = len(ordered)
    kept = ordered[:max_pairs]
    counters: Dict[str, int] = {}
    for c in kept:
        counters[c["persona"]] = counters.get(c["persona"], 0) + 1
        c["pair_id"] = f"prop-{c['persona']}-{counters[c['persona']]:02d}"
        stats["per_category"][c["category"]] = stats["per_category"].get(c["category"], 0) + 1
    stats["total_candidates"] = total
    stats["returned"] = len(kept)
    stats["dropped"] = total - len(kept)
    return kept, stats


def build_proposed_md(proposed: List[dict], stats: dict, meta: dict) -> str:
    L: List[str] = []
    L.append("# 골든 페어 후보 (UNLABELED) — 사람 라벨링용")
    L.append("")
    L.append("> 이 목록은 **라벨이 없는 후보 쌍**입니다. `propose-golden-pairs` 가 기존 "
             "`outputs/eval` 산출물만 읽어 '판단이 갈릴 만한' 하드 케이스를 자동 추출한 것입니다. "
             "시스템은 여기서 **어느 쪽이 더 낫다고 라벨하지 않습니다** — 사람이 각 쌍에 "
             "`expected_winner`(A_better/B_better/tie/unsure)와 `label_reason`을 채워야 합니다.")
    L.append("")
    if meta:
        L.append(f"- 추출 소스: `{meta.get('from','outputs/eval')}` · 최대 {meta.get('max_pairs','-')}쌍 요청")
    L.append(f"- 후보 총 {stats.get('total_candidates',0)}쌍 발견 → 상위 {stats.get('returned',0)}쌍 반환 "
             f"(난이도/하드니스 순; {stats.get('dropped',0)}쌍은 상한으로 생략 — `--max-pairs` 로 더 받기).")
    L.append(f"- 페르소나별 후보 수: {stats.get('per_persona',{})}")
    L.append(f"- 반환된 쌍의 카테고리 분포: {stats.get('per_category',{})}")
    L.append("")
    L.append("**A/B 정렬 규약:** A = 현재 기본 모드(domain_fit_bt)가 **더 높게** 매긴 공고입니다. "
             "따라서 시스템에 동의하면 `A_better`, 뒤집어야 한다고 보면 `B_better` 입니다.")
    L.append("")

    by_persona: Dict[str, List[dict]] = {}
    for c in proposed:
        by_persona.setdefault(c["persona"], []).append(c)

    for persona, items in by_persona.items():
        L.append(f"## {persona} ({len(items)}쌍)")
        L.append("")
        for c in items:
            sv = c["_system_view"]
            modes = list(sv["rank_by_mode"].keys())
            ranks = " · ".join(f"{m}: A#{sv['rank_by_mode'][m]['a']}/B#{sv['rank_by_mode'][m]['b']}"
                               for m in modes)
            L.append(f"### {c['pair_id']}  ·  [{c['category']}] / 난이도 힌트: {c['difficulty']}"
                     + ("  ·  ⚠ 모드 불일치" if sv["modes_disagree"] else ""))
            L.append(f"- **A** `{c['job_a_id']}` — {c['job_a_company']} · {c['job_a_title']}  "
                     f"(role={sv['role_family_a']}, domain={sv['domain_a']}, "
                     f"fit={sv['fit_a']}, BT={sv['bt_a']})")
            L.append(f"- **B** `{c['job_b_id']}` — {c['job_b_company']} · {c['job_b_title']}  "
                     f"(role={sv['role_family_b']}, domain={sv['domain_b']}, "
                     f"fit={sv['fit_b']}, BT={sv['bt_b']})")
            L.append(f"- 추출 사유: {'; '.join(c['_proposed_reasons'])}")
            L.append(f"- 모드별 순위: {ranks}")
            L.append(f"- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), "
                     f"`label_reason` = ____")
            L.append("")
    L.append("---")
    L.append("## 라벨링 후 다음 단계")
    L.append("1. `proposed_pairs.json` 의 각 쌍에 `expected_winner` 와 `label_reason` 을 채웁니다 "
             "(unsure 는 자유롭게 사용 — 점수에서 제외됩니다).")
    L.append("2. 라벨링한 파일을 `data/eval/golden_pairs/golden_pairs.json` 으로 저장합니다.")
    L.append("3. `python -m src.main eval-golden-pairs --pairs data/eval/golden_pairs/golden_pairs.json` "
             "로 정확도를 측정합니다 (LLM 호출 없음).")
    return "\n".join(L)
