"""Job service module connecting EmployaAI to the admin-provided job postings CSV.

The source of truth is: data/Merged_industry_jobs_industry_jobs.csv.
This service treats the CSV as read-only admin data, normalizes rows safely,
caches results based on file modification timestamp, and calculates genuine
profile match scores without fabricating statistics.
"""

from __future__ import annotations

import csv
import os
import re
from pathlib import Path
from typing import Any

try:
    from utils.paths import JOBS_DATA_PATH, DATA_DIR
    ADMIN_JOBS_CSV = JOBS_DATA_PATH
except Exception:
    ADMIN_JOBS_CSV = Path(__file__).resolve().parent.parent / "data" / "Merged_industry_jobs_industry_jobs.csv"

from services.db import (
    save_user_job,
    unsave_user_job,
    get_user_saved_job_ids,
    is_job_saved,
)

# Standardized skill column mappings in the admin CSV
SKILL_FIELDS = {
    "Python": "PythonRequired",
    "Linux": "LinuxRequired",
    "Networking": "NetworkingRequired",
    "AWS": "AWSRequired",
    "Azure": "AzureRequired",
    "Docker": "DockerRequired",
    "Kubernetes": "KubernetesRequired",
    "Terraform": "TerraformRequired",
    "Cybersecurity": "CyberSecurityRequired",
    "Communication": "CommunicationRequired",
}

# Known Indian tech hubs detectable in URL slugs
LOCATION_KEYWORDS = [
    "hyderabad", "mumbai", "noida", "ahmedabad", "bhubaneswar",
    "bangalore", "bengaluru", "pune", "chennai", "gurgaon", "gurugram", "delhi", "kolkata"
]

# Internal in-memory cache holding parsed jobs and file mtime
_CACHE: dict[str, Any] = {
    "mtime": 0.0,
    "jobs": [],
}


def _clean_experience_label(exp: str) -> str:
    """Normalize corrupted encoding characters like dashes in experience strings."""
    if not exp or not str(exp).strip():
        return "Not Specified"
    cleaned = str(exp).strip()
    cleaned = re.sub(r'[\uFFFD\u2013\u2014\u00A0]', '-', cleaned)
    # Normalize multiple spaces
    cleaned = " ".join(cleaned.split())
    return cleaned


def _clean_salary_label(val: str | None) -> tuple[str, bool]:
    """Return formatted salary display string and boolean indicating if disclosed."""
    if not val or not str(val).strip():
        return "Not Disclosed", False
    s = str(val).strip()
    if s.upper() in ("NA", "N/A", "NONE", "NULL", "0"):
        return "Not Disclosed", False
    s = re.sub(r'[\uFFFD\u2013\u2014\u00A0]', '-', s)
    if "LPA" not in s.upper():
        return f"{s} LPA", True
    return s, True


def _extract_location_from_url(url: str) -> str | None:
    """Attempt to detect location mentioned in the job posting URL slug."""
    if not url:
        return None
    url_lower = url.lower()
    for loc in LOCATION_KEYWORDS:
        if loc in url_lower:
            return loc.title()
    return None


def get_csv_metadata() -> dict[str, Any]:
    """Return exact metadata about the admin CSV file."""
    path = ADMIN_JOBS_CSV
    exists = path.exists()
    return {
        "filename": path.name,
        "path": str(path),
        "exists": exists,
        "size_bytes": path.stat().st_size if exists else 0,
        "mtime": path.stat().st_mtime if exists else 0.0,
    }


def load_admin_jobs(force_reload: bool = False) -> list[dict[str, Any]]:
    """Load and normalize all jobs from the admin-provided CSV.
    
    Caches the parsed rows in memory; invalidates automatically if CSV file is modified.
    Never alters the underlying CSV file.
    """
    if not ADMIN_JOBS_CSV.exists():
        return []

    curr_mtime = ADMIN_JOBS_CSV.stat().st_mtime
    if not force_reload and _CACHE["jobs"] and _CACHE["mtime"] == curr_mtime:
        return _CACHE["jobs"]

    parsed_jobs: list[dict[str, Any]] = []

    with ADMIN_JOBS_CSV.open(mode="r", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            # Handle whitespace in column names
            clean_row = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k}

            try:
                job_id = int(clean_row.get("Job_ID", 0))
            except (ValueError, TypeError):
                continue

            raw_url = clean_row.get("Link of the Job", clean_row.get("Link of the Job ", ""))
            has_valid_url = bool(raw_url and raw_url.startswith("http"))
            company = clean_row.get("Company") or "Company Confidential / Disclosed upon application"
            role = clean_row.get("Role") or "Tech Specialist"
            experience_raw = clean_row.get("Experience", "")
            experience = _clean_experience_label(experience_raw)
            salary_raw = clean_row.get("SalaryLPA", "")
            salary_display, is_salary_disclosed = _clean_salary_label(salary_raw)

            # Parse the 10 skill requirements (1-10)
            skills: dict[str, int] = {}
            for skill_name, col_name in SKILL_FIELDS.items():
                val = clean_row.get(col_name, "1")
                try:
                    skills[skill_name] = max(1, min(10, int(float(val))))
                except (ValueError, TypeError):
                    skills[skill_name] = 1

            # Top required skills (priority >= 6)
            top_skills = [
                {"name": s, "level": lvl}
                for s, lvl in sorted(skills.items(), key=lambda x: x[1], reverse=True)
                if lvl >= 6
            ]
            if not top_skills:
                # Fallback to top 3 skills
                top_skills = [
                    {"name": s, "level": lvl}
                    for s, lvl in sorted(skills.items(), key=lambda x: x[1], reverse=True)[:3]
                ]

            location = _extract_location_from_url(raw_url)

            job_record = {
                "id": job_id,
                "title": role,
                "role": role,
                "company": company,
                "experience": experience,
                "salary_display": salary_display,
                "salary_disclosed": is_salary_disclosed,
                "salary_raw": salary_raw,
                "url": raw_url if has_valid_url else "",
                "has_url": has_valid_url,
                "location": location or "Multi-city / Remote",
                "skills": skills,
                "top_skills": top_skills,
            }
            parsed_jobs.append(job_record)

    _CACHE["mtime"] = curr_mtime
    _CACHE["jobs"] = parsed_jobs
    return parsed_jobs


def filter_jobs(
    jobs: list[dict[str, Any]],
    search_query: str = "",
    role_filter: str = "All",
    experience_filter: str = "All",
    skill_filter: str = "All",
    salary_only: bool = False,
) -> list[dict[str, Any]]:
    """Filter jobs based exclusively on fields that exist in the admin dataset."""
    filtered = jobs

    # 1. Search Query
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered = [
            j for j in filtered
            if q in j["title"].lower()
            or q in j["company"].lower()
            or q in j["experience"].lower()
            or q in j["location"].lower()
            or any(q in s.lower() for s in j["skills"])
        ]

    # 2. Role Filter
    if role_filter and role_filter != "All":
        filtered = [j for j in filtered if j["role"] == role_filter]

    # 3. Experience Filter
    if experience_filter and experience_filter != "All":
        filtered = [j for j in filtered if j["experience"] == experience_filter]

    # 4. Skill Filter
    if skill_filter and skill_filter != "All":
        # Match if the job requires this skill at level >= 5
        filtered = [j for j in filtered if j["skills"].get(skill_filter, 0) >= 5]

    # 5. Disclosed Salary Only
    if salary_only:
        filtered = [j for j in filtered if j["salary_disclosed"]]

    return filtered


def calculate_job_match(
    job: dict[str, Any],
    profile: dict[str, Any] | None,
) -> dict[str, Any]:
    """Calculate a genuine match score between a job posting and an applicant profile.
    
    Uses real student skills from profile['skills'] (rated 1-5, normalized to 1-10)
    and compares against the job's 10 skill requirements (1-10).
    Never fabricates scores.
    """
    if not profile:
        return {
            "has_data": False,
            "score": None,
            "matched_skills": [],
            "gap_skills": [],
            "message": "Complete your profile to receive personalized job matching.",
        }

    user_skills = profile.get("skills", [])
    if not user_skills:
        return {
            "has_data": False,
            "score": None,
            "matched_skills": [],
            "gap_skills": [],
            "message": "Add your skills in your Profile to calculate your match score.",
        }

    # Normalize user skills dictionary: name -> level (scaled to 1-10)
    student_skills_map: dict[str, float] = {}
    for item in user_skills:
        name = (item.get("name") or "").strip().lower()
        raw_lvl = float(item.get("level") or 0)
        # Convert 1-5 scale to 1-10 scale
        student_skills_map[name] = max(1.0, min(10.0, raw_lvl * 2.0))

    job_skills = job.get("skills", {})
    if not job_skills:
        return {
            "has_data": False,
            "score": None,
            "matched_skills": [],
            "gap_skills": [],
            "message": "Job skill requirements not specified.",
        }

    total_weight = 0.0
    matched_weight = 0.0
    matched_list: list[str] = []
    gap_list: list[str] = []

    for skill_name, req_level in job_skills.items():
        weight = float(req_level)  # Higher required skills weigh more
        total_weight += weight

        # Find closest match in user skills
        s_lower = skill_name.lower()
        user_level = student_skills_map.get(s_lower)
        if user_level is None:
            # Check partial match (e.g. "aws" in "aws core" or "python" in "python programming")
            for k, v in student_skills_map.items():
                if s_lower in k or k in s_lower:
                    user_level = v
                    break

        if user_level is not None:
            ratio = min(1.0, user_level / req_level)
            matched_weight += ratio * weight
            if user_level >= req_level:
                matched_list.append(f"{skill_name} ({round(user_level/2, 1)}/5)")
            else:
                gap_list.append(f"{skill_name} (Need {req_level}/10)")
        else:
            gap_list.append(f"{skill_name} (Missing)")

    if total_weight == 0:
        match_pct = 50
    else:
        match_pct = round((matched_weight / total_weight) * 100)

    # Optional boost if student target role matches job role
    target_role = (profile.get("target_role") or "").strip().lower()
    if target_role and (target_role in job["role"].lower() or job["role"].lower() in target_role):
        match_pct = min(100, match_pct + 10)

    return {
        "has_data": True,
        "score": match_pct,
        "matched_skills": matched_list,
        "gap_skills": gap_list,
        "message": f"{match_pct}% Match based on your profile skills",
    }


def get_job_by_id(job_id: int) -> dict[str, Any] | None:
    """Retrieve a single job record by ID."""
    jobs = load_admin_jobs()
    for j in jobs:
        if j["id"] == job_id:
            return j
    return None


def get_saved_jobs_for_user(user_id: str) -> list[dict[str, Any]]:
    """Retrieve list of saved job dictionaries for the authenticated user."""
    if not user_id:
        return []
    saved_ids = get_user_saved_job_ids(user_id)
    if not saved_ids:
        return []
    all_jobs = load_admin_jobs()
    return [j for j in all_jobs if j["id"] in saved_ids]


__all__ = [
    "load_admin_jobs",
    "filter_jobs",
    "calculate_job_match",
    "get_job_by_id",
    "get_csv_metadata",
    "get_saved_jobs_for_user",
    "save_user_job",
    "unsave_user_job",
    "is_job_saved",
    "get_user_saved_job_ids",
    "SKILL_FIELDS",
]
