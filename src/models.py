"""Pydantic models for every structured artifact in the pipeline."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

# --- allowed enum values + clamping helpers ---
EVIDENCE_TYPES = {"work_experience", "project", "education", "award", "activity", "skills", "other"}
STRENGTHS = {"strong", "medium", "weak"}
REQ_TYPES = {"critical", "required", "preferred", "optional"}
MATCH_LEVELS = {"direct", "adjacent", "weak", "missing"}
CONFIDENCES = {"high", "medium", "low"}

ROLE_FAMILIES = {
    "frontend", "backend", "fullstack", "android", "ios", "data", "ml_ai",
    "devops_infra", "security", "product", "marketing", "design", "other",
}
REQ_NATURES = {
    "technical", "domain", "experience_level", "behavioral",
    "language", "location", "employment", "other",
}
# Where a requirement came from in the JD.
REQ_ORIGINS = {"explicit_requirement", "responsibility_inferred", "product_context", "company_value"}
# What the requirement actually is, for fit-capping purposes.
#   prerequisite        = something the candidate must ALREADY have before joining (can cap fit)
#   product_duty        = something the candidate will DO after joining (must NOT cap fit)
#   context             = domain/product background (informational only)
#   behavioral_preference = soft trait (should not aggressively cap fit)
PREREQ_STATUSES = {"prerequisite", "product_duty", "context", "behavioral_preference"}
# Category of an interchangeable tool/library group (for same-category grouping).
REQ_CATEGORIES = {
    "state_management", "styling", "data_fetching", "build_tooling", "testing",
    "framework", "language", "other",
}
# How alternatives may be satisfied: a same-category equivalent counts (adjacent), or exact only.
ALT_MATCH_POLICIES = {"exact_or_same_category", "exact_only"}
# Natures that meaningfully gate role fit (drive caps).
CORE_NATURES = {"technical", "domain", "experience_level", "language"}
DOMAIN_ALIGNMENTS = {"strong", "adjacent", "weak", "mismatch"}

# Maps a JD role_family to the broader domain tokens it "is", for alignment vs. the user profile.
ROLE_FAMILY_TO_DOMAINS = {
    "frontend": {"frontend", "web"},
    "backend": {"backend"},
    "fullstack": {"fullstack", "frontend", "backend", "web"},
    "android": {"mobile", "android"},
    "ios": {"mobile", "ios"},
    "data": {"data"},
    "ml_ai": {"ml_ai", "ai"},
    "devops_infra": {"devops", "cloud", "infra"},
    "security": {"security"},
    "product": {"product"},
    "marketing": {"marketing"},
    "design": {"design"},
    "other": {"other"},
}

MATCH_SEVERITY = {"missing": 0, "weak": 1, "adjacent": 2, "direct": 3}
SEVERITY_TO_LEVEL = {v: k for k, v in MATCH_SEVERITY.items()}
CONF_RANK = {"low": 0, "medium": 1, "high": 2}

FIT_LABELS = {
    5: "매우 높음: 강력 추천",
    4: "높음: 추천",
    3: "보통: 검토 가능",
    2: "낮음: 아쉬움",
    1: "매우 낮음: 비추천",
}


def clamp(value: Any, allowed: set, default: str) -> str:
    v = str(value or "").strip().lower()
    return v if v in allowed else default


def as_list(v: Any) -> List[str]:
    if v is None:
        return []
    if isinstance(v, str):
        s = v.strip()
        return [p.strip() for p in s.split(",") if p.strip()] if s else []
    if isinstance(v, (list, tuple)):
        return [str(x).strip() for x in v if str(x).strip()]
    return [str(v)]


# --- resume evidence ---
class EvidenceItem(BaseModel):
    evidence_id: str
    title: str = ""
    source_section: str = ""
    exact_quote: str = ""
    normalized_summary: str = ""
    skills: List[str] = Field(default_factory=list)
    domain: List[str] = Field(default_factory=list)
    evidence_type: str = "other"
    strength: str = "medium"
    recency: Optional[str] = None

    @field_validator("skills", "domain", mode="before")
    @classmethod
    def _coerce_lists(cls, v):
        return as_list(v)

    @field_validator("evidence_type", mode="before")
    @classmethod
    def _ev_type(cls, v):
        return clamp(v, EVIDENCE_TYPES, "other")

    @field_validator("strength", mode="before")
    @classmethod
    def _strength(cls, v):
        return clamp(v, STRENGTHS, "medium")


class Resume(BaseModel):
    raw_text: str = ""
    evidence: List[EvidenceItem] = Field(default_factory=list)
    primary_domains: List[str] = Field(default_factory=list)
    secondary_domains: List[str] = Field(default_factory=list)


# --- job posting ---
class Requirement(BaseModel):
    requirement_id: str
    requirement_text: str = ""
    requirement_type: str = "required"
    requirement_nature: str = "other"
    requirement_origin: str = "explicit_requirement"
    prerequisite_status: str = "prerequisite"
    alternatives: List[str] = Field(default_factory=list)  # OR-group options (one is enough)
    requirement_category: str = "other"
    alternative_match_policy: str = "exact_or_same_category"

    @field_validator("alternatives", mode="before")
    @classmethod
    def _alts(cls, v):
        return as_list(v)

    @field_validator("requirement_type", mode="before")
    @classmethod
    def _rt(cls, v):
        return clamp(v, REQ_TYPES, "required")

    @field_validator("requirement_nature", mode="before")
    @classmethod
    def _rn(cls, v):
        return clamp(v, REQ_NATURES, "other")

    @field_validator("requirement_origin", mode="before")
    @classmethod
    def _ro(cls, v):
        return clamp(v, REQ_ORIGINS, "explicit_requirement")

    @field_validator("prerequisite_status", mode="before")
    @classmethod
    def _ps(cls, v):
        return clamp(v, PREREQ_STATUSES, "prerequisite")

    @field_validator("requirement_category", mode="before")
    @classmethod
    def _rc(cls, v):
        return clamp(v, REQ_CATEGORIES, "other")

    @field_validator("alternative_match_policy", mode="before")
    @classmethod
    def _amp(cls, v):
        return clamp(v, ALT_MATCH_POLICIES, "exact_or_same_category")


class JobPosting(BaseModel):
    job_id: str
    company: str = ""
    title: str = ""
    url: str = ""
    role_family: str = "other"
    employment_type: str = ""
    location: str = ""
    team: str = ""
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[Requirement] = Field(default_factory=list)
    preferred_requirements: List[Requirement] = Field(default_factory=list)
    hard_constraints: List[str] = Field(default_factory=list)
    seniority: str = ""
    tech_stack: List[str] = Field(default_factory=list)
    raw_text: str = ""

    @field_validator("responsibilities", "hard_constraints", "tech_stack", mode="before")
    @classmethod
    def _coerce_lists(cls, v):
        return as_list(v)

    @field_validator("role_family", mode="before")
    @classmethod
    def _rf(cls, v):
        return clamp(v, ROLE_FAMILIES, "other")

    def all_requirements(self) -> List[Requirement]:
        return list(self.requirements) + list(self.preferred_requirements)


# --- matching table ---
class MatchRow(BaseModel):
    requirement_id: str
    requirement_text: str = ""
    requirement_type: str = "required"
    requirement_nature: str = "other"
    requirement_origin: str = "explicit_requirement"
    prerequisite_status: str = "prerequisite"
    alternatives: List[str] = Field(default_factory=list)  # OR-group options, if any
    requirement_category: str = "other"
    alternative_match_policy: str = "exact_or_same_category"
    matched_evidence_ids: List[str] = Field(default_factory=list)
    evidence_quotes: List[str] = Field(default_factory=list)
    evidence_source_sections: List[str] = Field(default_factory=list)
    match_level: str = "missing"
    confidence: str = "low"
    explanation: str = ""
    risk_note: str = ""
    # verifier-added / pipeline fields
    extractive_ok: Optional[bool] = None
    downgraded: bool = False
    invalid_match: bool = False
    rematched: bool = False
    verifier_note: str = ""

    @field_validator("matched_evidence_ids", "evidence_quotes", "evidence_source_sections",
                     "alternatives", mode="before")
    @classmethod
    def _coerce_lists(cls, v):
        return as_list(v)

    @field_validator("requirement_type", mode="before")
    @classmethod
    def _rt(cls, v):
        return clamp(v, REQ_TYPES, "required")

    @field_validator("requirement_nature", mode="before")
    @classmethod
    def _rn(cls, v):
        return clamp(v, REQ_NATURES, "other")

    @field_validator("requirement_origin", mode="before")
    @classmethod
    def _ro(cls, v):
        return clamp(v, REQ_ORIGINS, "explicit_requirement")

    @field_validator("prerequisite_status", mode="before")
    @classmethod
    def _ps(cls, v):
        return clamp(v, PREREQ_STATUSES, "prerequisite")

    @field_validator("requirement_category", mode="before")
    @classmethod
    def _rc(cls, v):
        return clamp(v, REQ_CATEGORIES, "other")

    @field_validator("alternative_match_policy", mode="before")
    @classmethod
    def _amp(cls, v):
        return clamp(v, ALT_MATCH_POLICIES, "exact_or_same_category")

    @field_validator("match_level", mode="before")
    @classmethod
    def _ml(cls, v):
        return clamp(v, MATCH_LEVELS, "missing")

    @field_validator("confidence", mode="before")
    @classmethod
    def _conf(cls, v):
        return clamp(v, CONFIDENCES, "low")


class MatchingTable(BaseModel):
    job_id: str
    company: str = ""
    title: str = ""
    rows: List[MatchRow] = Field(default_factory=list)


# --- pairwise ---
class PairwiseResult(BaseModel):
    job_a: str
    job_b: str
    ab_winner: str = "tie"   # job_id or "tie"
    ba_winner: str = "tie"   # job_id or "tie"
    agreed: bool = False
    outcome: str = "tie"     # job_id of winner, or "tie"
    confidence: str = "low"
    reason_ab: str = ""
    reason_ba: str = ""


# --- final fit result ---
class FitResult(BaseModel):
    job_id: str
    company: str = ""
    title: str = ""
    url: str = ""
    role_family: str = "other"
    domain_alignment: str = "weak"
    domain_alignment_reason: str = ""
    rank: int = 0
    fit_level: int = 1
    fit_label: str = ""
    bt_score: float = 0.0
    listwise_reason: str = ""
    coverage: Dict[str, Any] = Field(default_factory=dict)
    strong_matches: List[str] = Field(default_factory=list)
    weak_or_missing: List[str] = Field(default_factory=list)
    preferred_gaps: List[str] = Field(default_factory=list)
    product_duties: List[str] = Field(default_factory=list)
    invalid_matches: List[str] = Field(default_factory=list)
    risk_notes: List[str] = Field(default_factory=list)
