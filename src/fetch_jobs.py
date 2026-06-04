"""Fetch software-engineering JDs from Toss and Daangn official career sources.

Both companies expose JSON APIs (Greenhouse-backed), so requests + BeautifulSoup are
enough and Playwright is not needed:
  - Toss:   https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs  (+ /jobs/{id} for content)
  - Daangn: https://boards-api.greenhouse.io/v1/boards/daangn/jobs?content=true

If fetching fails, we fall back to data/jobs_manual.md so the rest of the pipeline still runs.
"""
from __future__ import annotations

import html as ihtml
import json
import re
from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup

from . import config

HEADERS = {"User-Agent": config.USER_AGENT, "Accept": "application/json, text/html"}

TOSS_BASE = "https://api-public.toss.im/api/v3/ipd-eggnog/career"
DAANGN_BASE = "https://boards-api.greenhouse.io/v1/boards/daangn"

MANUAL_TEMPLATE = (config.JOBS_MANUAL_PATH.read_text(encoding="utf-8")
                   if config.JOBS_MANUAL_PATH.exists() else "")


# --------------------------------------------------------------------------- helpers
def _norm(s: str) -> str:
    return re.sub(r"[\s\-_/]+", "", (s or "").lower())


def keyword_match(title: str) -> bool:
    nt = _norm(title)
    return any(_norm(kw) in nt for kw in config.TARGET_KEYWORDS)


def _clean_html(raw: str) -> str:
    if not raw:
        return ""
    soup = BeautifulSoup(raw, "html.parser")
    text = soup.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines()]
    out: List[str] = []
    blank = 0
    for ln in lines:
        if ln:
            out.append(ln)
            blank = 0
        else:
            blank += 1
            if blank <= 1:
                out.append("")
    return "\n".join(out).strip()


def _slug(s: str) -> str:
    s = re.sub(r"[^0-9A-Za-z가-힣]+", "-", (s or "").strip()).strip("-").lower()
    return s[:60]


# --------------------------------------------------------------------------- Toss
def _list_toss() -> Tuple[List[dict], List[str]]:
    failures: List[str] = []
    try:
        r = requests.get(f"{TOSS_BASE}/jobs", headers=HEADERS, timeout=config.REQUEST_TIMEOUT)
        r.raise_for_status()
        items = r.json().get("success") or []
    except Exception as e:  # noqa: BLE001
        return [], [f"Toss list fetch failed: {e}"]
    meta = []
    for it in items:
        title = it.get("title", "")
        if not keyword_match(title):
            continue
        meta.append({
            "_source": "toss",
            "_gid": it.get("id"),
            "company": "Toss",
            "title": title,
            "url": it.get("absolute_url", ""),
        })
    return meta, failures


def _toss_detail(gid) -> Tuple[str, str]:
    """Return (html_content, error)."""
    try:
        d = requests.get(f"{TOSS_BASE}/jobs/{gid}", headers=HEADERS, timeout=config.REQUEST_TIMEOUT)
        d.raise_for_status()
        payload = d.json()
        job = payload.get("success") if isinstance(payload.get("success"), dict) else payload
        content = (job or {}).get("content", "") if isinstance(job, dict) else ""
        return ihtml.unescape(content or ""), ""
    except Exception as e:  # noqa: BLE001
        return "", f"Toss detail {gid} failed: {e}"


# --------------------------------------------------------------------------- Daangn
def _list_daangn() -> Tuple[List[dict], List[str]]:
    failures: List[str] = []
    try:
        r = requests.get(f"{DAANGN_BASE}/jobs?content=true", headers=HEADERS, timeout=config.REQUEST_TIMEOUT)
        r.raise_for_status()
        items = r.json().get("jobs") or []
    except Exception as e:  # noqa: BLE001
        return [], [f"Daangn list fetch failed: {e}"]
    meta = []
    for it in items:
        title = it.get("title", "")
        if not keyword_match(title):
            continue
        meta.append({
            "_source": "daangn",
            "_gid": it.get("id"),
            "company": "Daangn",
            "title": title,
            "url": it.get("absolute_url", ""),
            "_content": ihtml.unescape(it.get("content", "") or ""),
        })
    return meta, failures


# --------------------------------------------------------------------------- pre-selection
# Cheap, deterministic role_family classification from the title (no LLM). The LLM-parsed
# role_family during JD structuring remains authoritative; this is only for SELECTION.
# Order matters: more specific / higher-signal patterns first.
ROLE_PATTERNS = [
    ("fullstack", ["fullstack", "full-stack", "full stack", "풀스택"]),
    ("frontend", ["frontend", "front-end", "front end", "프론트엔드", "프론트", "web frontend",
                  "웹 프론트", "웹프론트", "react", "vue", "웹 프론트엔드"]),
    ("android", ["android", "안드로이드"]),
    ("ios", ["ios"]),
    ("ml_ai", ["ai engineer", " ai ", "machine learning", "ml engineer", "mlops",
               "deep learning", "data scientist", "llm", "인공지능", "생성형"]),
    ("data", ["data analytics", "analytics engineer", "data engineer", "data platform",
              "데이터 엔지니어", "데이터 분석", "데이터"]),
    ("security", ["security", "보안", "모의해킹", "detection", "response", "appsec", "침해사고"]),
    ("devops_infra", ["aiops", "devops", "sre", "platform engineer", "platform", "infra",
                      "인프라", "network", "네트워크", "cloud", "클라우드", "kubernetes",
                      "reliability", "플랫폼"]),
    ("backend", ["backend", "back-end", "back end", "서버", "백엔드", "server"]),
    ("marketing", ["marketer", "marketing", "마케팅", "마케터"]),
    ("design", ["designer", "design", "디자인"]),
    ("product", ["product manager", "프로덕트 매니저", "프로덕트매니저", "기획자"]),
]

_TIER_FROM_ALIGN = {"strong": "primary", "adjacent": "adjacent", "weak": "weak", "mismatch": "mismatch"}
TIER_ORDER = ["primary", "adjacent", "weak", "mismatch"]


def classify_role_family(title: str, team: str = "") -> str:
    t = f"{title} {team}".lower()
    for rf, kws in ROLE_PATTERNS:
        if any(kw in t for kw in kws):
            return rf
    return "other"


def role_tier(role_family: str) -> str:
    """Map a role_family to a selection tier using the same domain logic as fit scoring."""
    from .rank_aggregate import domain_alignment  # local import avoids any import cycle
    align, _ = domain_alignment(role_family, config.USER_PRIMARY_DOMAINS, config.USER_SECONDARY_DOMAINS)
    return _TIER_FROM_ALIGN.get(align, "weak")


def _interleave_company(items: List[dict]) -> List[dict]:
    toss = [m for m in items if m["_source"] == "toss"]
    daangn = [m for m in items if m["_source"] == "daangn"]
    out: List[dict] = []
    i = j = 0
    while i < len(toss) or j < len(daangn):
        if i < len(toss):
            out.append(toss[i]); i += 1
        if j < len(daangn):
            out.append(daangn[j]); j += 1
    return out


def build_pool(pool_size: int) -> Tuple[List[dict], List[dict], List[str]]:
    """List keyword-matched candidates from both companies (cheap, title-level), classify each,
    and return (pool, all_matched, failures). The pool is tier-priority ordered then capped at
    pool_size so primary-domain roles are never lost to alphabetical/API truncation."""
    toss_meta, f1 = _list_toss()
    daangn_meta, f2 = _list_daangn()
    seen = set()
    matched: List[dict] = []
    for m in toss_meta + daangn_meta:
        key = f"{m['_source']}-{m['_gid']}"
        if key in seen or not m["_gid"]:
            continue
        seen.add(key)
        m["job_id"] = key
        m["pre_role_family"] = classify_role_family(m["title"])
        m["tier"] = role_tier(m["pre_role_family"])
        matched.append(m)
    by_tier = {t: _interleave_company([m for m in matched if m["tier"] == t]) for t in TIER_ORDER}
    # Always include primary (priority), then fill the rest round-robin across adjacent/weak/mismatch
    # so the pool stays DIVERSE and contrast (weak/mismatch) cases remain available for selection.
    pool: List[dict] = list(by_tier["primary"])[:pool_size]
    rest = [by_tier["adjacent"], by_tier["weak"], by_tier["mismatch"]]
    idxs = [0, 0, 0]
    while len(pool) < pool_size and any(idxs[k] < len(rest[k]) for k in range(len(rest))):
        for k in range(len(rest)):
            if len(pool) >= pool_size:
                break
            if idxs[k] < len(rest[k]):
                pool.append(rest[k][idxs[k]]); idxs[k] += 1
    return pool, matched, f1 + f2


def select_balanced(pool: List[dict], limit: int) -> Tuple[List[dict], List[dict]]:
    """Pick ~50% primary, ~30% adjacent, rest weak/mismatch (contrast), with priority backfill.
    Returns (selected, skipped)."""
    by_tier = {t: [m for m in pool if m["tier"] == t] for t in TIER_ORDER}
    q_primary = round(limit * 0.5)
    q_adjacent = round(limit * 0.3)
    q_contrast = max(0, limit - q_primary - q_adjacent)
    chosen_ids = set()
    selected: List[dict] = []

    def take(lst, n):
        added = 0
        for m in lst:
            if len(selected) >= limit or added >= n:
                break
            if m["job_id"] not in chosen_ids:
                selected.append(m); chosen_ids.add(m["job_id"]); added += 1

    take(by_tier["primary"], q_primary)
    take(by_tier["adjacent"], q_adjacent)
    take(by_tier["weak"] + by_tier["mismatch"], q_contrast)  # weak preferred over mismatch
    # backfill remaining slots by priority (extra primary first, then adjacent, weak, mismatch)
    if len(selected) < limit:
        for m in by_tier["primary"] + by_tier["adjacent"] + by_tier["weak"] + by_tier["mismatch"]:
            if len(selected) >= limit:
                break
            if m["job_id"] not in chosen_ids:
                selected.append(m); chosen_ids.add(m["job_id"])

    skipped = []
    for m in pool:
        if m["job_id"] not in chosen_ids:
            skipped.append({"job_id": m["job_id"], "company": m["company"], "title": m["title"],
                            "url": m["url"], "pre_role_family": m["pre_role_family"], "tier": m["tier"],
                            "reason": f"{m['tier']} tier 정원/우선순위에서 제외"})
    return selected, skipped


def _fetch_details(selected: List[dict]) -> Tuple[List[dict], List[str]]:
    jobs: List[dict] = []
    failures: List[str] = []
    for m in selected:
        if m["_source"] == "toss":
            content, err = _toss_detail(m["_gid"])
            if err:
                failures.append(err)
        else:
            content = m.get("_content", "")
        text = _clean_html(content)
        if not text.strip():
            failures.append(f"{m['company']} {m['_gid']}: empty content, skipped")
            continue
        jobs.append({
            "job_id": m["job_id"],
            "company": m["company"],
            "title": m["title"],
            "url": m["url"],
            "pre_role_family": m["pre_role_family"],
            "raw_text": text,
            "_html": content,
        })
    return jobs, failures


def _distribution(items: List[dict], key: str) -> dict:
    out: dict = {}
    for m in items:
        out[m[key]] = out.get(m[key], 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def fetch_all(limit: int = None, pool_size: int = None) -> Tuple[List[dict], List[str], dict]:
    """Domain-aware fetch: build a larger pool, select a balanced subset, fetch detail only for
    the selected. Returns (jobs, failures, selection_report)."""
    limit = limit or config.MAX_JD_PAGES
    pool_size = pool_size or config.DEFAULT_POOL_SIZE
    pool, matched, list_failures = build_pool(pool_size)
    selected, skipped = select_balanced(pool, limit)
    jobs, fetch_failures = _fetch_details(selected)
    fetched_ids = {j["job_id"] for j in jobs}

    selected_view = [{"job_id": m["job_id"], "company": m["company"], "title": m["title"],
                      "url": m["url"], "pre_role_family": m["pre_role_family"], "tier": m["tier"],
                      "fetched": m["job_id"] in fetched_ids} for m in selected]
    primary_in_matched = sum(1 for m in matched if m["tier"] == "primary")
    selection = {
        "pool_size_requested": pool_size,
        "limit": limit,
        "total_matched": len(matched),
        "pool_considered": len(pool),
        "selected_count": len(selected),
        "fetched_count": len(jobs),
        "skipped_count": len(skipped),
        "primary_domain_jobs_found": primary_in_matched > 0,
        "primary_in_matched": primary_in_matched,
        "matched_tier_distribution": _distribution(matched, "tier"),
        "matched_role_family_distribution": _distribution(matched, "pre_role_family"),
        "selected_tier_distribution": _distribution(selected, "tier"),
        "selected_role_family_distribution": _distribution(selected, "pre_role_family"),
        "selected": selected_view,
        "skipped": skipped,
        "note": "pre-selection role_family is a heuristic from the title; the LLM-parsed "
                "role_family during ranking is authoritative.",
    }
    return jobs, list_failures + fetch_failures, selection


def save_raw(jobs: List[dict]) -> None:
    config.ensure_dirs()
    # Clear stale raw files so the directory reflects exactly this fetch.
    for old in list(config.RAW_JOBS_DIR.glob("*.json")) + list(config.RAW_JOBS_DIR.glob("*.html")):
        try:
            old.unlink()
        except OSError:
            pass
    index = []
    for j in jobs:
        jid = j["job_id"]
        (config.RAW_JOBS_DIR / f"{jid}.html").write_text(j.get("_html", ""), encoding="utf-8")
        meta = {k: v for k, v in j.items() if k != "_html"}
        (config.RAW_JOBS_DIR / f"{jid}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        index.append({"job_id": jid, "company": j["company"], "title": j["title"], "url": j["url"]})
    (config.RAW_JOBS_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def _field(block: str, name: str) -> str:
    m = re.search(rf"(?mi)^{name}:\s*(.*)$", block)
    return m.group(1).strip() if m else ""


def parse_manual(text: str) -> List[dict]:
    jobs: List[dict] = []
    blocks = re.split(r"(?mi)^===\s*JOB\s*===\s*$", text)
    for i, b in enumerate(blocks):
        b = b.strip()
        if not b:
            continue
        m = re.search(r"(?ms)^TEXT:\s*\n?(.*)$", b)
        body = m.group(1).strip() if m else ""
        # skip empty / untouched template blocks
        if not body or body.lower().startswith("<paste") or "<paste the full" in body.lower():
            continue
        company = _field(b, "COMPANY") or "Unknown"
        title = _field(b, "TITLE") or f"Manual Job {i}"
        url = _field(b, "URL")
        jid = _slug(f"manual-{company}-{title}") or f"manual-{i}"
        jobs.append({
            "job_id": jid,
            "company": company,
            "title": title,
            "url": url,
            "raw_text": body,
        })
    return jobs


def load_raw_jobs() -> List[dict]:
    """Load fetched raw jobs; fall back to manually-pasted jobs_manual.md."""
    jobs: List[dict] = []
    if config.RAW_JOBS_DIR.exists():
        for f in sorted(config.RAW_JOBS_DIR.glob("*.json")):
            if f.name == "index.json":
                continue
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            if (d.get("raw_text") or "").strip():
                jobs.append(d)
    if jobs:
        return jobs
    if config.JOBS_MANUAL_PATH.exists():
        return parse_manual(config.JOBS_MANUAL_PATH.read_text(encoding="utf-8"))
    return []


def load_fixture(path: str) -> List[dict]:
    """Load a fixed set of raw JDs from a fixture JSON file (list, or {"jobs": [...]})."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    jobs = data.get("jobs", []) if isinstance(data, dict) else data
    out = []
    for j in jobs:
        if (j.get("raw_text") or "").strip():
            out.append({
                "job_id": j["job_id"],
                "company": j.get("company", ""),
                "title": j.get("title", ""),
                "url": j.get("url", ""),
                "raw_text": j["raw_text"],
            })
    return out


def ensure_manual_template() -> None:
    """Make sure data/jobs_manual.md exists so manual entry is always possible."""
    if config.JOBS_MANUAL_PATH.exists():
        return
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.JOBS_MANUAL_PATH.write_text(MANUAL_TEMPLATE or _FALLBACK_MANUAL, encoding="utf-8")


_FALLBACK_MANUAL = """# 수동 JD 입력 (Manual JD input)

스크래핑이 실패하면 여기에 JD를 직접 붙여넣으세요.

=== JOB ===
COMPANY: Toss
TITLE: Frontend Developer
URL:
TEXT:
<paste the full job description text here>
"""
