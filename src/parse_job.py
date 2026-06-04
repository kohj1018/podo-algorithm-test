"""Stage 2: structure each raw JD into a JobPosting with classified requirements."""
from __future__ import annotations

from . import config, llm
from .models import JobPosting, Requirement

MAX_RAW_CHARS = 12000


def _requirements(raw_list, prefix: str, default_type: str):
    out = []
    if not isinstance(raw_list, list):
        return out
    for i, r in enumerate(raw_list):
        alts = []
        rorigin = "explicit_requirement"
        rstatus = None
        rcategory = "other"
        rpolicy = "exact_or_same_category"
        if isinstance(r, dict):
            rid = r.get("requirement_id") or f"{prefix}{i + 1}"
            text = r.get("requirement_text") or r.get("text") or ""
            rtype = r.get("requirement_type") or default_type
            rnature = r.get("requirement_nature") or "other"
            rorigin = r.get("requirement_origin") or "explicit_requirement"
            rstatus = r.get("prerequisite_status")
            alts = r.get("alternatives") or []
            rcategory = r.get("requirement_category") or "other"
            rpolicy = r.get("alternative_match_policy") or "exact_or_same_category"
        else:
            rid = f"{prefix}{i + 1}"
            text = str(r)
            rtype = default_type
            rnature = "other"
        if not str(text).strip():
            continue
        # Default prerequisite_status when the model omits it: behavioral traits are preferences,
        # everything else defaults to a prerequisite (conservative; duties must be marked explicitly).
        if not rstatus:
            rstatus = "behavioral_preference" if str(rnature).lower() == "behavioral" else "prerequisite"
        out.append(Requirement(requirement_id=rid, requirement_text=str(text).strip(),
                                requirement_type=rtype, requirement_nature=rnature,
                                requirement_origin=rorigin, prerequisite_status=rstatus,
                                alternatives=alts, requirement_category=rcategory,
                                alternative_match_policy=rpolicy))
    # ensure unique ids within the list
    seen = set()
    for k, req in enumerate(out):
        if req.requirement_id in seen:
            req.requirement_id = f"{prefix}{k + 1}"
        seen.add(req.requirement_id)
    return out


def structure_job(raw_job: dict) -> JobPosting:
    prompt = config.render(
        config.load_prompt("jd_extract"),
        COMPANY=raw_job.get("company", ""),
        TITLE=raw_job.get("title", ""),
        URL=raw_job.get("url", ""),
        RAW_TEXT=(raw_job.get("raw_text", "") or "")[:MAX_RAW_CHARS],
    )

    def validate(obj) -> JobPosting:
        if not isinstance(obj, dict):
            raise ValueError("expected a JSON object for the job posting")
        reqs = _requirements(obj.get("requirements"), "R", "required")
        prefs = _requirements(obj.get("preferred_requirements"), "P", "preferred")
        if not reqs and not prefs:
            raise ValueError("no requirements extracted from JD")
        return JobPosting(
            job_id=raw_job["job_id"],
            company=raw_job.get("company", ""),
            title=raw_job.get("title", ""),
            url=raw_job.get("url", ""),
            role_family=obj.get("role_family", "other") or "other",
            employment_type=obj.get("employment_type", "") or "",
            location=obj.get("location", "") or "",
            team=obj.get("team", "") or "",
            seniority=obj.get("seniority", "") or "",
            tech_stack=obj.get("tech_stack", []) or [],
            responsibilities=obj.get("responsibilities", []) or [],
            hard_constraints=obj.get("hard_constraints", []) or [],
            requirements=reqs,
            preferred_requirements=prefs,
            raw_text=raw_job.get("raw_text", "") or "",
        )

    return llm.call_structured(llm.JSON_SYSTEM, prompt, validate, max_tokens=4096,
                               cache_label=f"jd_{raw_job['job_id']}")
