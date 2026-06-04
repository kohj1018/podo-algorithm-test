"""Stage 1/4: read the resume and extract structured evidence items via the LLM.

A deterministic Skills evidence item is ALWAYS added (code-first, not LLM-dependent) so that
explicitly-listed tools (Tailwind, styled-components, Socket.io, WebTransport, …) are never
dropped and stay visible to the ID-based matcher.
"""
from __future__ import annotations

import re
from typing import Dict, List

from . import config, llm
from .models import EvidenceItem, Resume

PLACEHOLDER_MARKER = "<!-- RESUME_PLACEHOLDER -->"

# Headings that denote a skills/tech-stack section.
_SKILL_HEADING = re.compile(r"^#{1,6}\s*(skills?|기술\s*스택|기술\s*및\s*도구|tech\s*stack)\b", re.I)
_ANY_HEADING = re.compile(r"^#{1,6}\s+")
# Key frontend skills to confirm visibility (matched on normalized text).
_KEY_FRONTEND_SKILLS = ["React", "Next.js", "TypeScript", "JavaScript", "styled-components",
                        "Tailwind", "Socket.io", "WebTransport", "Zustand", "React Query",
                        "TanStack Query", "Vite", "Vitest"]


def _norm(s: str) -> str:
    return re.sub(r"[\s\-_.]+", "", s.lower())


def _parse_skill_tokens(line: str) -> List[str]:
    s = line.lstrip("-*• \t").strip()
    if ":" in s:  # drop a leading "Category:" label
        s = s.split(":", 1)[1]
    return [t.strip() for t in re.split(r"[,/·;]", s) if t.strip()]


def extract_skills_evidence(resume_text: str) -> List[EvidenceItem]:
    """Deterministically build Skills evidence item(s) from the resume's Skills section(s).
    exact_quote is the verbatim bullet line (extractive); skills are parsed from it."""
    lines = resume_text.splitlines()
    items: List[EvidenceItem] = []
    n = 0
    for i, ln in enumerate(lines):
        if not _SKILL_HEADING.match(ln.strip()):
            continue
        for j in range(i + 1, len(lines)):
            body = lines[j]
            if _ANY_HEADING.match(body.strip()):
                break
            if not body.strip() or not re.match(r"^\s*[-*•]", body):
                continue
            tokens = _parse_skill_tokens(body)
            if not tokens:
                continue
            n += 1
            label = body.lstrip("-*• \t").split(":", 1)[0].strip() if ":" in body else "Skills"
            items.append(EvidenceItem(
                evidence_id=f"skills_{n}",
                title=f"Skills: {label}" if label and label != "Skills" else "Skills",
                source_section="Skills",
                exact_quote=body.strip(),          # verbatim → extractive
                normalized_summary=f"보유 기술: {', '.join(tokens)}",
                skills=tokens,
                evidence_type="skills",
                strength="medium",
                recency=None,
            ))
    return items


def skills_debug(resume: Resume) -> Dict:
    """Debug view: total evidence, skills items, extracted skills, key-frontend-skill presence."""
    skills_items = [e for e in resume.evidence if e.evidence_type == "skills"]
    all_skills = sorted({s for e in resume.evidence for s in e.skills})
    blob = _norm(" ".join((e.exact_quote + " " + " ".join(e.skills)) for e in resume.evidence))
    present = {k: (_norm(k) in blob) for k in _KEY_FRONTEND_SKILLS}
    return {
        "total_evidence_items": len(resume.evidence),
        "skills_evidence_ids": [e.evidence_id for e in skills_items],
        "extracted_skills": all_skills,
        "key_frontend_skills_present": present,
    }

_PLACEHOLDER_BODY = """<!-- RESUME_PLACEHOLDER -->
# 이력서 (Resume) — 플레이스홀더

> 이 파일은 자동 생성된 플레이스홀더입니다. 본인의 실제 이력서로 전체를 교체하세요.
> 파이프라인은 이 텍스트에서만 근거(evidence)를 추출하며 없는 사실은 지어내지 않습니다.
> 교체 후 맨 위 `<!-- RESUME_PLACEHOLDER -->` 줄을 삭제하세요.

## 요약
## 경력
## 프로젝트
## 학력
## 기술 스택
## 수상/활동
"""


def ensure_resume() -> None:
    """Create a placeholder resume if none exists. Never overwrites an existing file."""
    if config.RESUME_PATH.exists():
        return
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.RESUME_PATH.write_text(_PLACEHOLDER_BODY, encoding="utf-8")


def load_resume_text() -> str:
    return config.RESUME_PATH.read_text(encoding="utf-8")


def is_placeholder(text: str) -> bool:
    return PLACEHOLDER_MARKER in text


def extract_evidence(resume_text: str) -> Resume:
    prompt = config.render(config.load_prompt("resume_extract"), RESUME_TEXT=resume_text)

    def validate(obj) -> List[EvidenceItem]:
        items = obj.get("evidence") if isinstance(obj, dict) else obj
        if not isinstance(items, list) or not items:
            raise ValueError("expected a non-empty 'evidence' list")
        out = []
        seen = set()
        for i, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            ev = EvidenceItem(**it)
            if not ev.evidence_id or ev.evidence_id in seen:
                ev.evidence_id = f"E{i + 1}"
            seen.add(ev.evidence_id)
            out.append(ev)
        if not out:
            raise ValueError("no valid evidence items parsed")
        return out

    evidence = llm.call_structured(llm.JSON_SYSTEM, prompt, validate, max_tokens=8000,
                                   cache_label="resume")

    # ALWAYS add deterministic Skills evidence (in addition to LLM evidence), so explicitly
    # listed tools are never lost. Avoid id collisions with the LLM evidence.
    existing_ids = {e.evidence_id for e in evidence}
    for sk in extract_skills_evidence(resume_text):
        if sk.evidence_id in existing_ids:
            sk.evidence_id = sk.evidence_id + "_x"
        existing_ids.add(sk.evidence_id)
        evidence.append(sk)
    return Resume(raw_text=resume_text, evidence=evidence)
