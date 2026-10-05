"""Assessment scoring and attempt management service interface for EmployaAI."""

from __future__ import annotations

from collections import defaultdict
from typing import Any
from services.db import (
    record_assessment_attempt,
    get_user_assessment_history,
    record_question_history,
    get_recent_question_ids,
)


def score_assessment(questions: list[dict[str, Any]], answers: dict[str, str]) -> dict[str, Any]:
    """Deterministic assessment scoring."""
    total = len(questions)
    correct = sum(1 for question in questions if answers.get(question["id"]) == question["correct"])
    categories: dict[str, dict[str, int]] = defaultdict(lambda: {"correct": 0, "total": 0})
    for question in questions:
        category = question["category"]
        categories[category]["total"] += 1
        if answers.get(question["id"]) == question["correct"]:
            categories[category]["correct"] += 1

    category_scores = [
        {
            "name": category,
            "pct": round(values["correct"] / values["total"] * 100)
            if values["total"]
            else 0,
        }
        for category, values in categories.items()
    ]
    category_scores.sort(key=lambda item: item["pct"], reverse=True)
    overall = round(correct / total * 100) if total else 0
    return {
        "source": "deterministic_assessment_service",
        "status": "completed",
        "correct_count": correct,
        "total": total,
        "overall_pct": overall,
        "categories": category_scores,
        "strengths": [item for item in category_scores if item["pct"] >= 70],
        "improvements": sorted(
            [item for item in category_scores if item["pct"] < 70],
            key=lambda item: item["pct"],
        ),
    }


__all__ = [
    "score_assessment",
    "record_assessment_attempt",
    "get_user_assessment_history",
    "record_question_history",
    "get_recent_question_ids",
]
