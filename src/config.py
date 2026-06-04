"""Configuration, paths, provider selection, and prompt loading."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

# --- paths ---
DATA_DIR = ROOT / "data"
RAW_JOBS_DIR = DATA_DIR / "raw" / "jobs"
RESUME_PATH = DATA_DIR / "resume.md"
JOBS_MANUAL_PATH = DATA_DIR / "jobs_manual.md"
PROMPTS_DIR = ROOT / "prompts"
OUTPUTS_DIR = ROOT / "outputs"
LATEST_DIR = OUTPUTS_DIR / "latest"
CACHE_DIR = OUTPUTS_DIR / "cache"
FIXTURES_DIR = DATA_DIR / "fixtures"

# Bump when model/schema or scoring semantics change in a way that should invalidate caches.
SCHEMA_VERSION = "3"
# Fixed seed for the OpenAI path (used when the model supports it; cache is the main mechanism).
LLM_SEED = int(os.getenv("LLM_SEED", "7"))

# --- LLM config ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or None
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
# Model is selected via the OPENAI_MODEL env var (never hardcoded in business logic).
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
LLM_PROVIDER = (os.getenv("LLM_PROVIDER") or "").strip().lower() or None

# --- pipeline params ---
MAX_JD_PAGES = int(os.getenv("MAX_JD_PAGES", "10"))
DEFAULT_POOL_SIZE = int(os.getenv("POOL_SIZE", "50"))
TOP_K_PAIRWISE = int(os.getenv("TOP_K_PAIRWISE", "5"))
MAX_PAIRWISE_CANDIDATES = int(os.getenv("MAX_PAIRWISE_CANDIDATES", "8"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
USER_AGENT = "Mozilla/5.0 (compatible; fit-rank-prototype/0.1)"

# Target job keywords (substring match on title, case/space/hyphen-insensitive).
# Defaults REQUIRE an engineering token — bare "intern/인턴/web/웹" are intentionally excluded
# so marketing/ops roles don't slip in. Override via env TARGET_KEYWORDS (comma-separated).
_DEFAULT_KEYWORDS = [
    "software", "engineer", "developer", "frontend", "backend", "fullstack",
    "android", "ios", "server", "platform",
    "소프트웨어", "엔지니어", "개발자", "프론트엔드", "백엔드", "서버", "플랫폼",
]
TARGET_KEYWORDS = [
    k.strip() for k in os.getenv("TARGET_KEYWORDS", ",".join(_DEFAULT_KEYWORDS)).split(",") if k.strip()
]


def _csv_env(name: str, default):
    raw = os.getenv(name)
    if raw is None:
        return list(default)
    return [x.strip().lower() for x in raw.split(",") if x.strip()]


# User domain profile — surfaced in the report so it is inspectable. Override via env
# USER_PRIMARY_DOMAINS / USER_SECONDARY_DOMAINS (comma-separated).
USER_PRIMARY_DOMAINS = _csv_env("USER_PRIMARY_DOMAINS", ["frontend", "fullstack", "web", "robot_web"])
USER_SECONDARY_DOMAINS = _csv_env("USER_SECONDARY_DOMAINS", ["backend", "cloud", "mobile"])


def get_provider() -> Optional[str]:
    """Return 'anthropic', 'openai', or None based on env keys / override."""
    if LLM_PROVIDER == "anthropic":
        return "anthropic" if ANTHROPIC_API_KEY else None
    if LLM_PROVIDER == "openai":
        return "openai" if OPENAI_API_KEY else None
    if ANTHROPIC_API_KEY:
        return "anthropic"
    if OPENAI_API_KEY:
        return "openai"
    return None


def provider_help() -> str:
    return (
        "No LLM API key found.\n"
        "  1) Copy .env.example to .env\n"
        "  2) Add ANTHROPIC_API_KEY=... (preferred) or OPENAI_API_KEY=...\n"
        "  3) (optional) set ANTHROPIC_MODEL / OPENAI_MODEL to a model your key can access\n"
        "Then re-run the command."
    )


def ensure_dirs() -> None:
    for d in (DATA_DIR, RAW_JOBS_DIR, LATEST_DIR, CACHE_DIR):
        d.mkdir(parents=True, exist_ok=True)


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def render(template: str, **kwargs) -> str:
    out = template
    for key, value in kwargs.items():
        out = out.replace("{{" + key + "}}", str(value))
    return out
