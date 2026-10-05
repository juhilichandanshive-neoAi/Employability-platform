"""Build session outputs from a student's profile and the approved data sources."""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from neoai.services.assessment import score_assessment
    from neoai.services.employability import calculate_score, profile_completion
    from neoai.services.job_data import (
        ROLE_TERMS,
        SKILL_COLUMNS,
        load_rows,
        role_requirements,
        rows_for_role,
        salary_snapshot,
    )
except ImportError:
    from services.assessment_service import score_assessment
    from services.employability_service import calculate_score, profile_completion
    from services.job_data_service import (
        ROLE_TERMS,
        SKILL_COLUMNS,
        load_rows,
        role_requirements,
        rows_for_role,
        salary_snapshot,
    )

SUPPORTED_ROLES = tuple(ROLE_TERMS)

SKILL_ALIASES = {
    "aws": "AWS core",
    "amazon web services": "AWS core",
    "cyber security": "Cybersecurity",
    "cybersecurity": "Cybersecurity",
    "communication skills": "Communication",
    "communication": "Communication",
    "networking fundamentals": "Networking",
}

CERTIFICATION_CATALOG = {
    "Python": ("Python Institute", "PCEP – Certified Entry-Level Python Programmer", "Foundational"),
    "Linux": ("Linux Foundation", "Linux Foundation Certified IT Associate", "Foundational"),
    "Networking": ("Cisco", "CCNA", "Associate"),
    "AWS core": ("Amazon Web Services", "AWS Certified Solutions Architect – Associate", "Associate"),
    "Azure": ("Microsoft", "Azure Fundamentals (AZ-900)", "Foundational"),
    "Docker": ("Docker", "Docker Certified Associate", "Associate"),
    "Kubernetes": ("Cloud Native Computing Foundation", "Kubernetes and Cloud Native Associate", "Foundational"),
    "Terraform": ("HashiCorp", "Terraform Associate", "Associate"),
    "Cybersecurity": ("ISC2", "Certified in Cybersecurity", "Foundational"),
}


def empty_profile() -> dict[str, Any]:
    """Return a blank profile; the app must not seed a fictional student."""
    return {
        "name": "",
        "initials": "",
        "track": "",
        "target_role": SUPPORTED_ROLES[0],
        "semester": "",
        "email": "",
        "phone": "",
        "enrolment_id": "",
        "degree": "",
        "cgpa": None,
        "github": "",
        "linkedin": "",
        "languages": "",
        "skills": [],
        "projects": [],
        "certifications": [],
        "internships": [],
        "education_entries": [],
        "resume": None,
    }


def canonical_skill_name(name: str) -> str | None:
    normalized = " ".join(str(name or "").strip().lower().split())
    if normalized in SKILL_ALIASES:
        return SKILL_ALIASES[normalized]
    return next(
        (skill for skill in SKILL_COLUMNS if skill.lower() == normalized),
        None,
    )


def proficiency_to_job_requirement(level: float | int) -> int:
    """Map the profile's 0–5 proficiency onto the model/dataset's 1–10 scale."""
    bounded = max(0.0, min(5.0, float(level)))
    return max(1, min(10, math.floor(bounded * 2 + 0.5)))


def _profile_skill_levels(profile: dict[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in profile.get("skills") or []:
        if not isinstance(item, dict):
            continue
        name = canonical_skill_name(item.get("name", ""))
        if name is None:
            continue
        try:
            level = max(0.0, min(5.0, float(item.get("level", 0))))
        except (TypeError, ValueError):
            continue
        result[name] = level
    return result


def _profile_has_evidence(profile: dict[str, Any]) -> bool:
    return any(
        profile.get(field)
        for field in ("name", "email", "degree", "skills", "projects", "certifications")
    )


def calculate_skill_gaps(
    profile: dict[str, Any],
    role: str,
    rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    source_rows = rows if rows is not None else load_rows()
    evidence = role_requirements(role, source_rows)
    levels = _profile_skill_levels(profile)
    requirements = evidence["requirements_1_to_10"]
    compared: list[dict[str, Any]] = []

    if evidence["row_count"]:
        for skill, required_10 in requirements.items():
            if skill not in levels:
                continue
            required_5 = math.ceil(required_10 / 2)
            level_5 = levels[skill]
            gap = max(0.0, required_5 - level_5)
            priority = "Met" if gap == 0 else "High" if gap >= 2 else "Medium"
            compared.append(
                {
                    "skill": skill,
                    "asked": f"{evidence['row_count']} dataset rows",
                    "required": f"{required_10}/10 ({required_5}/5)",
                    "have": f"{level_5:g}/5",
                    "student_level_0_to_5": level_5,
                    "required_level_1_to_10": required_10,
                    "required_level_0_to_5": required_5,
                    "priority": priority,
                    "gap_0_to_5": gap,
                    "impact": gap,
                    "action": (
                        f"Build evidence in {skill} to reach the role requirement."
                        if gap
                        else f"Your recorded {skill} level meets this snapshot requirement."
                    ),
                }
            )

    gaps = [item for item in compared if item["priority"] in ("High", "Medium")]
    gaps.sort(key=lambda item: (-item["gap_0_to_5"], item["skill"]))
    met_count = sum(item["priority"] == "Met" for item in compared)
    high_count = sum(item["priority"] == "High" for item in compared)
    return {
        "role": role,
        "source": evidence["source"],
        "row_count": evidence["row_count"],
        "requirements_1_to_10": requirements,
        "compared_count": len(compared),
        "total_requirement_count": len(requirements),
        "rows": compared,
        "gaps": gaps,
        "met_count": met_count,
        "high_count": high_count,
        "radar": {
            "categories": [item["skill"] for item in compared],
            "you": [item["student_level_0_to_5"] for item in compared],
            "role_requires": [math.ceil(item["required_level_1_to_10"] / 2) for item in compared],
        },
        "companies": evidence["companies"],
        "salary": salary_snapshot(role, rows_for_role(role, source_rows)),
    }


def calculate_career_matches(
    profile: dict[str, Any],
    rows: list[dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    source_rows = rows if rows is not None else load_rows()
    levels = _profile_skill_levels(profile)
    if not levels:
        return []

    recommendations: list[dict[str, Any]] = []
    for role in SUPPORTED_ROLES:
        evidence = role_requirements(role, source_rows)
        if not evidence["row_count"]:
            continue
        requirements = evidence["requirements_1_to_10"]
        covered_value = 0.0
        skills_ok: list[str] = []
        skills_gap: list[str] = []
        unreported: list[str] = []

        for skill, required_10 in requirements.items():
            level_5 = levels.get(skill)
            if level_5 is None:
                unreported.append(skill)
                continue
            mapped_level = proficiency_to_job_requirement(level_5)
            covered_value += min(mapped_level / required_10, 1.0)
            if level_5 >= math.ceil(required_10 / 2):
                skills_ok.append(skill)
            else:
                skills_gap.append(skill)

        match = round(covered_value / len(requirements) * 100) if requirements else 0
        salary = salary_snapshot(role, rows_for_role(role, source_rows))
        if salary["status"] == "available":
            low, high = salary["range"]
            salary_label = f"{low:g}–{high:g} LPA (dataset snapshot; not a model prediction)"
        else:
            salary_label = "Unavailable in the dataset snapshot"

        recommendations.append(
            {
                "role": role,
                "match": match,
                "status": "Calculated from recorded skills",
                "skills_ok": skills_ok,
                "skills_gap": skills_gap,
                "skills_not_provided": unreported,
                "salary": salary_label,
                "companies": evidence["companies"],
                "row_count": evidence["row_count"],
                "source": evidence["source"],
                "requirements_1_to_10": requirements,
            }
        )

    return sorted(recommendations, key=lambda item: (-item["match"], item["role"]))


def recommend_certifications(
    profile: dict[str, Any],
    skill_gap: dict[str, Any],
) -> list[dict[str, Any]]:
    held_text = " ".join(
        str(item.get("name", "")).lower()
        for item in profile.get("certifications") or []
        if isinstance(item, dict)
    )
    recommendations: list[dict[str, Any]] = []
    for gap in skill_gap["gaps"]:
        skill = gap["skill"]
        entry = CERTIFICATION_CATALOG.get(skill)
        if entry is None:
            continue
        provider, name, level = entry
        if name.lower() in held_text or skill.lower() in held_text:
            continue
        recommendations.append(
            {
                "provider": provider,
                "vendor": provider,
                "rank": len(recommendations) + 1,
                "match": f"Addresses the {skill} gap for {skill_gap['role']}",
                "name": name,
                "level": level,
                "duration": "Not estimated",
                "cost": "Not provided by the current data source",
                "rating": None,
                "gaps_closed": skill,
                "uplift": "Not estimated",
                "asked_in": f"{skill_gap['row_count']} dataset rows",
                "skills": [skill],
                "source": "static certification catalog; not live pricing or ratings",
            }
        )
        if len(recommendations) == 3:
            break
    return recommendations


def build_roadmap(
    skill_gap: dict[str, Any],
    assessment: dict[str, Any] | None,
    certifications: list[dict[str, Any]],
) -> dict[str, Any]:
    cert_by_skill = {
        skill: cert
        for cert in certifications
        for skill in cert["skills"]
    }
    tasks: list[dict[str, Any]] = []
    for gap in skill_gap["gaps"]:
        cert = cert_by_skill.get(gap["skill"])
        tasks.append(
            {
                "title": f"Build {gap['skill']} proficiency",
                "reason": (
                    f"Recorded level {gap['have']} is below the role requirement "
                    f"{gap['required']}."
                ),
                "priority": gap["priority"],
                "status": "Not started",
                "certification": cert["name"] if cert else None,
                "source": "student profile and dataset snapshot",
            }
        )

    for weakness in (assessment or {}).get("improvements", []):
        tasks.append(
            {
                "title": f"Review assessment area: {weakness['name']}",
                "reason": f"Current assessment result: {weakness['pct']}%.",
                "priority": "Assessment review",
                "status": "Not started",
                "certification": None,
                "source": "current assessment",
            }
        )

    return {
        "role": skill_gap["role"],
        "tasks": tasks,
        "status": "available" if tasks else "no_identified_actions",
        "progress_pct": 0,
    }


def build_app_data(
    profile: dict[str, Any],
    assessment: dict[str, Any] | None,
    assessment_history: list[dict[str, Any]] | None = None,
    generated_reports: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return all screen data from one profile and current-session evidence."""
    profile = profile or empty_profile()
    assessment = assessment if assessment and assessment.get("status") == "completed" else None
    profile_pct = profile_completion(profile)
    rows = load_rows()
    target_role = profile.get("target_role") if profile.get("target_role") in SUPPORTED_ROLES else SUPPORTED_ROLES[0]
    skill_gap = calculate_skill_gaps(profile, target_role, rows)
    careers = calculate_career_matches(profile, rows)
    certifications = recommend_certifications(profile, skill_gap)
    roadmap = build_roadmap(skill_gap, assessment, certifications)
    history = list(assessment_history or [])

    if assessment and _profile_has_evidence(profile):
        score = calculate_score(profile, assessment)
    else:
        score = {
            "source": "deterministic_employability_service",
            "status": "awaiting_profile_and_assessment",
            "overall": None,
            "band": "Not calculated",
            "verdict": "Complete your profile and assessment",
            "job_ready_threshold": 80,
            "cohort_average": None,
            "percentile": None,
            "cohort_size": None,
            "points_this_week": None,
            "confidence": None,
            "components": {},
            "breakdown": [],
            "drivers": [],
            "weights": None,
        }

    assessment_categories = (assessment or {}).get("categories", [])
    seen_attempts = set()
    deduped_history = []
    for item in history:
        att_key = item.get("attempt_id") or (item.get("domain_key"), item.get("submitted_at"), item.get("overall_pct"))
        if att_key not in seen_attempts:
            seen_attempts.add(att_key)
            deduped_history.append(item)

    current_attempts = [
        {
            "attempt_id": item.get("attempt_id", f"att_{idx}"),
            "name": f"{item.get('domain_name', 'Assessment')} assessment",
            "when": item.get("submitted_at", "Current session"),
            "score": f"{item.get('overall_pct', 0)}%",
            "kind": "success" if item.get("overall_pct", 0) >= 70 else "warning",
            "overall_pct": item.get("overall_pct", 0),
            "categories": item.get("categories", []),
        }
        for idx, item in enumerate(deduped_history)
    ]

    student = {
        **profile,
        "initials": (
            "".join(part[0] for part in profile.get("name", "").split()[:2]).upper()
            if profile.get("name", "").strip()
            else "?"
        ),
        "profile_completion": profile_pct,
    }
    education = []
    # If legacy degree field is present, add it as first entry
    if profile.get("degree"):
        details = []
        if profile.get("semester"):
            details.append(str(profile["semester"]))
        if profile.get("cgpa") is not None:
            details.append(f"CGPA {profile['cgpa']}")
        education.append(
            {
                "id": "legacy_degree",
                "level": profile["degree"],
                "meta": " · ".join(details) if details else "Student-provided profile",
                "score": str(profile.get("cgpa") or "Not provided"),
                "description": "",
                "institution": "",
                "field_of_study": "",
                "start_year": "",
                "grad_year": "",
            }
        )

    # User-added education entries
    for entry in profile.get("education_entries", []):
        meta_parts = []
        field = (entry.get("field_of_study") or "").strip()
        inst = (entry.get("institution") or "").strip()
        start = (entry.get("start_year") or "").strip()
        grad = (entry.get("grad_year") or entry.get("year") or "").strip()
        if field:
            meta_parts.append(field)
        if inst:
            meta_parts.append(inst)
        if start and grad:
            meta_parts.append(f"{start}–{grad}")
        elif grad:
            meta_parts.append(grad)

        education.append(
            {
                "id": entry.get("id"),
                "level": entry.get("degree") or entry.get("level") or "Degree",
                "meta": " · ".join(meta_parts) if meta_parts else "Student-provided education",
                "score": str(entry.get("score") or entry.get("percentage") or "Not provided"),
                "description": entry.get("description", ""),
                "institution": inst,
                "field_of_study": field,
                "start_year": start,
                "grad_year": grad,
            }
        )

    profile_steps = [
        {
            "label": label,
            "status": "done" if ready else "pending",
        }
        for label, ready in (
            ("Personal details", bool(profile.get("name") and profile.get("email"))),
            ("Education", bool(profile.get("degree") or profile.get("education_entries"))),
            ("Skills", bool(profile.get("skills"))),
            ("Projects", bool(profile.get("projects"))),
            ("Certifications", bool(profile.get("certifications"))),
            ("Internship", bool(profile.get("internships"))),
            ("Assessment", bool(assessment)),
        )
    ]
    for item in profile_steps:
        if item["status"] == "pending":
            item["status"] = "current"
            break

    return {
        "student": student,
        "profile": profile,
        "profile_completion": profile_pct,
        "profile_steps": profile_steps,
        "education": education,
        "skills": list(profile.get("skills") or []),
        "certifications_held": list(profile.get("certifications") or []),
        "projects": list(profile.get("projects") or []),
        "internships": list(profile.get("internships") or []),
        "resume": profile.get("resume"),
        "score": score,
        "score_breakdown": score["breakdown"],
        "score_drivers": score["drivers"],
        "score_delta_from_cohort": None,
        "points_to_ready": (
            max(0, score["job_ready_threshold"] - score["overall"])
            if score["overall"] is not None
            else None
        ),
        "skill_gap": skill_gap,
        "career_matches": careers,
        "fit_breakdown": [
            {"label": "Calculated skill match", "value": role["match"]}
            for role in careers
            if role["role"] == target_role
        ],
        "role_requirements": [
            {
                "item": row["skill"],
                "asked": row["asked"],
                "status": row["priority"],
            }
            for row in skill_gap["rows"]
        ],
        "certification_recommendations": certifications,
        "certification_table": certifications,
        "roadmap": roadmap,
        "analytics": {
            "assessment_count": len(history),
            "latest_assessment": assessment,
            "section_performance": [
                {"section": item["name"], "score": item["pct"]}
                for item in assessment_categories
            ],
            "attempt_history": current_attempts,
            "practice_hours_available": False,
        },
        "reports": list(generated_reports or []),
        "dataset": {
            "status": "available" if rows else "unavailable",
            "row_count": len(rows),
            "source": "bundled industry-jobs dataset snapshot",
        },
        "salary_model": {
            "status": "unavailable",
            "reason": "The approved final_salary_model.pkl artifact is not present.",
        },
    }