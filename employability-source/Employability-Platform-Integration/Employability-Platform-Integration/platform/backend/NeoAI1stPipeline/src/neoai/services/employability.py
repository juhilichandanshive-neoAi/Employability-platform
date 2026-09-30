"""Configurable, explainable employability scoring."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_WEIGHTS_PATH = PROJECT_ROOT / "config" / "employability_weights.json"


def load_weights() -> dict[str, float]:
    path = Path(os.getenv("EMPLOYABILITY_WEIGHTS_PATH", DEFAULT_WEIGHTS_PATH))
    with path.open(encoding="utf-8") as handle:
        weights = {key: float(value) for key, value in json.load(handle).items()}
    if not weights or any(value < 0 for value in weights.values()):
        raise ValueError("Employability weights must be non-negative and non-empty.")
    if abs(sum(weights.values()) - 1.0) > 0.001:
        raise ValueError("Employability weights must sum to 1.0.")
    return weights


def _skill_score(profile: dict[str, Any]) -> float:
    skills = profile.get("skills", [])
    if not skills:
        return 0.0
    values = []
    for skill in skills:
        try:
            values.append(max(0.0, min(5.0, float(skill.get("level", 0)))))
        except (TypeError, ValueError):
            continue
    return round(sum(values) / len(values) / 5 * 100, 1) if values else 0.0


def _profile_completion(profile: dict[str, Any]) -> float:
    fields = (
        profile.get("name"),
        profile.get("email"),
        profile.get("degree"),
        profile.get("github"),
        profile.get("linkedin"),
        profile.get("skills"),
        profile.get("projects"),
        profile.get("certifications"),
    )
    return round(sum(bool(value) for value in fields) / len(fields) * 100, 1)


def profile_completion(profile: dict[str, Any]) -> float:
    """Return the configured profile-completeness component for UI consumers."""
    return _profile_completion(profile)


def calculate_score(
    profile: dict[str, Any],
    assessment: dict[str, Any] | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    weights = weights or load_weights()
    cgpa = float(profile.get("cgpa") or 0)
    components = {
        "technical_skills": _skill_score(profile),
        "assessment": float((assessment or {}).get("overall_pct", 0)),
        "academic": max(0.0, min(100.0, cgpa * 10)),
        "projects": min(len(profile.get("projects", [])) / 3 * 100, 100),
        "certifications": min(len(profile.get("certifications", [])) / 2 * 100, 100),
        "internships": 100.0 if profile.get("internships") else 0.0,
        "profile_completeness": _profile_completion(profile),
    }
    overall = round(sum(components[key] * weights[key] for key in weights))
    if overall >= 80:
        band, verdict = "Band A", "Job-ready"
    elif overall >= 60:
        band, verdict = "Band B", "Near-ready"
    else:
        band, verdict = "Band C", "Building"

    labels = {
        "technical_skills": "Technical skills",
        "assessment": "Assessment",
        "academic": "Academic fit",
        "projects": "Projects",
        "certifications": "Certifications",
        "internships": "Internships",
        "profile_completeness": "Profile completeness",
    }
    breakdown = [
        {"label": labels[key], "value": round(value), "cohort": None}
        for key, value in components.items()
    ]
    drivers = []
    for key, value in sorted(components.items(), key=lambda item: item[1], reverse=True):
        impact = round((value - overall) / 10, 1)
        if impact != 0:
            drivers.append({"label": labels[key], "impact": impact})
    return {
        "source": "deterministic_employability_service",
        "status": "computed",
        "overall": overall,
        "band": band,
        "verdict": verdict,
        "job_ready_threshold": 80,
        "cohort_average": None,
        "percentile": None,
        "cohort_size": None,
        "points_this_week": None,
        "confidence": None,
        "components": components,
        "breakdown": breakdown,
        "drivers": drivers[:6],
        "weights": weights,
    }