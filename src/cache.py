"""Tiny inspectable on-disk cache for LLM JSON outputs (reproducibility).

Cache entries live under outputs/cache/ as one JSON file per call:
    <label>__<key12>.json   e.g. resume__9f1c3a2b7d4e.json

Each file stores the raw parsed JSON the LLM returned, plus a small _meta block.
Keys are derived from the full rendered prompt + model + schema version, so any change
to the resume/JD text, the prompt files, the model, or SCHEMA_VERSION invalidates the entry.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Optional

from . import config

# Set by the CLI: when True, ignore existing entries (re-parse) but still write fresh ones.
REFRESH = False
# Cache namespace: "" = normal (outputs/cache/), "fixture" = isolated (outputs/cache/fixture/).
# The fixture regression uses its own namespace so full `--refresh-cache` runs never touch it.
NAMESPACE = ""
# Counters for an end-of-run summary.
STATS = {"hit": 0, "miss": 0, "refresh": 0, "stale": 0}
# Collected one-line logs (printed by the CLI).
LOG: list = []


def reset_stats() -> None:
    STATS.update({"hit": 0, "miss": 0, "refresh": 0, "stale": 0})
    LOG.clear()


def _dir():
    return (config.CACHE_DIR / NAMESPACE) if NAMESPACE else config.CACHE_DIR


def make_key(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _safe(label: str) -> str:
    return re.sub(r"[^0-9A-Za-z_.-]+", "-", label)[:60]


def _path(label: str, key: str):
    return _dir() / f"{_safe(label)}__{key[:12]}.json"


def get(label: str, key: str) -> Optional[Any]:
    """Return cached payload, or None on miss / refresh / unreadable."""
    p = _path(label, key)
    if REFRESH:
        if p.exists():
            STATS["refresh"] += 1
            LOG.append(f"[cache refresh] {label}")
        else:
            STATS["miss"] += 1
            LOG.append(f"[cache miss] {label}")
        return None
    if not p.exists():
        STATS["miss"] += 1
        LOG.append(f"[cache miss] {label}")
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        STATS["hit"] += 1
        LOG.append(f"[cache hit] {label}")
        return data.get("payload")
    except Exception:  # noqa: BLE001
        STATS["miss"] += 1
        LOG.append(f"[cache miss:unreadable] {label}")
        return None


def put(label: str, key: str, payload: Any) -> None:
    config.ensure_dirs()
    d = _dir()
    d.mkdir(parents=True, exist_ok=True)
    p = _path(label, key)
    record = {
        "_meta": {"label": label, "key": key, "namespace": NAMESPACE or "normal",
                  "schema_version": config.SCHEMA_VERSION},
        "payload": payload,
    }
    p.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


def mark_stale(label: str) -> None:
    STATS["stale"] += 1
    LOG.append(f"[cache stale→reparse] {label}")


def summary() -> str:
    return (f"cache[{NAMESPACE or 'normal'}]: hit={STATS['hit']} miss={STATS['miss']} "
            f"refresh={STATS['refresh']} stale={STATS['stale']} (dir={_dir()})")
