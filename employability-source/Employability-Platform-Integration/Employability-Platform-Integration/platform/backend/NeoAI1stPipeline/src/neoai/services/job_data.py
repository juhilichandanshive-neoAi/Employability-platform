"""Read-only adapters over the static jobs snapshot used by the ML pipeline.

This module does not alter or retrain the salary model. It only aggregates
job-requirement evidence for role matching and skill-gap views.
"""

from __future__ import annotations

import csv
import os
import re
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = Path(
    os.getenv(
        "NEOAI_JOBS_DATA_PATH",
        PROJECT_ROOT / "data" / "raw" / "Merged_industry_jobs_industry_jobs.csv",
    )
)

SKILL_COLUMNS = {
    "Python": "PythonRequired",
    "Linux": "LinuxRequired",
    "Networking": "NetworkingRequired",
    "AWS core": "AWSRequired",
    "Azure": "AzureRequired",
    "Docker": "DockerRequired",
    "Kubernetes": "KubernetesRequired",
    "Terraform": "TerraformRequired",
    "Cybersecurity": "CyberSecurityRequired",
    "Communication": "CommunicationRequired",
}

ROLE_TERMS = {
    "Cloud Support Associate": ("cloud", "support", "associate", "aws"),
    "Cloud Ops / DevOps Trainee": ("devops", "sre", "cloud ops", "cloud engineer"),
    "SOC Analyst L1": ("soc", "security", "cyber", "incident", "analyst"),
}


def load_rows() -> list[dict[str, str]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _clean_role(role: str) -> str:
    return " ".join((role or "").strip().split()).lower()


def rows_for_role(role: str, rows: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    rows = rows if rows is not None else load_rows()
    terms = ROLE_TERMS.get(role, ())
    if not terms:
        return []
    matching = [
        row
        for row in rows
        if any(term in _clean_role(row.get("Role", "")) for term in terms)
    ]
    return matching


def _number(value: str) -> float | None:
    matches = re.findall(r"\d+(?:\.\d+)?", value or "")
    return float(matches[0]) if matches else None


def salary_snapshot(role: str, rows: list[dict[str, str]] | None = None) -> dict[str, Any]:
    role_rows = rows_for_role(role, rows)
    values: list[float] = []
    for row in role_rows:
        raw = row.get("SalaryLPA", "")
        numbers = re.findall(r"\d+(?:\.\d+)?", raw or "")
        if len(numbers) >= 2:
            values.extend([float(numbers[0]), float(numbers[-1])])
        elif numbers:
            values.append(float(numbers[0]))
    if not values:
        return {
            "source": "jobs_dataset_snapshot",
            "status": "unavailable",
            "range": None,
            "row_count": len(role_rows),
        }
    return {
        "source": "jobs_dataset_snapshot",
        "status": "available",
        "range": (round(min(values), 2), round(max(values), 2)),
        "row_count": len(role_rows),
    }


def role_requirements(role: str, rows: list[dict[str, str]] | None = None) -> dict[str, Any]:
    role_rows = rows_for_role(role, rows)
    requirements: dict[str, int] = {}
    for label, column in SKILL_COLUMNS.items():
        values = []
        for row in role_rows:
            try:
                values.append(max(1, min(10, int(float(row.get(column, "1"))))))
            except (TypeError, ValueError):
                continue
        requirements[label] = round(mean(values)) if values else 1
    companies = Counter((row.get("Company") or "").strip() for row in role_rows)
    companies.pop("", None)
    return {
        "role": role,
        "source": "jobs_dataset_snapshot",
        "row_count": len(role_rows),
        "requirements_1_to_10": requirements,
        "companies": [name for name, _ in companies.most_common(3)],
        "salary": salary_snapshot(role, role_rows),
    }


def role_evidence(role: str, rows: list[dict[str, str]] | None = None) -> dict[str, Any]:
    snapshot = role_requirements(role, rows)
    return {
        **snapshot,
        "asked_label": f"{snapshot['row_count']} dataset rows",
    }