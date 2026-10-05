"""
Question selection engine for the assessment system.

Handles:
- Random selection of N questions from the expanded pool
- Avoidance of recently-used questions
- Stable question sets during Streamlit reruns (stored in session state)
- History tracking per user for non-repetition across attempts
- Graceful fallback when the unused pool is smaller than required
"""

from __future__ import annotations

import copy
import random
from typing import Any

from data.question_bank import EXPANDED_QUESTION_BANK, get_questions_for_domain


# Number of questions per assessment attempt
QUESTIONS_PER_ASSESSMENT = 15

# How many past attempts to exclude questions from (before allowing reuse)
MAX_HISTORY_DEPTH = 5


def select_questions(
    domain: str,
    difficulty: str,
    count: int = QUESTIONS_PER_ASSESSMENT,
    exclude_ids: set[str] | None = None,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """Select `count` questions from the pool, avoiding `exclude_ids`.

    If the available pool (after exclusions) is smaller than `count`,
    gradually allow older excluded questions back in until we have enough.

    The returned questions have their option order randomized (where safe)
    and are in a randomized order.

    Parameters
    ----------
    domain : str
        Assessment domain key (e.g. "cloud", "cyber").
    difficulty : str
        Difficulty level ("easy", "moderate", "hard").
    count : int
        Number of questions to select.
    exclude_ids : set[str] | None
        Question IDs to avoid (from recent history).
    seed : int | None
        Random seed for deterministic selection within an attempt.

    Returns
    -------
    list[dict]
        Selected questions with randomized option order.
    """
    pool = get_questions_for_domain(domain, difficulty)
    if not pool:
        # Fall back to all difficulties if specific difficulty has no questions
        pool = get_questions_for_domain(domain)

    if not pool:
        return []

    exclude = set(exclude_ids or ())
    rng = random.Random(seed)

    # Filter out recently used questions
    available = [q for q in pool if q["id"] not in exclude]

    # If not enough unused questions, gradually allow older ones back
    if len(available) < count:
        # Add back excluded questions to fill the gap
        excluded_questions = [q for q in pool if q["id"] in exclude]
        rng.shuffle(excluded_questions)
        available.extend(excluded_questions[: count - len(available)])

    # If pool is still too small, use what we have
    actual_count = min(count, len(available))

    # Select questions randomly
    selected = rng.sample(available, actual_count)

    # Randomize question order
    rng.shuffle(selected)

    # Deep-copy and randomize option order for each question
    result = []
    keys = ["A", "B", "C", "D"]
    for q in selected:
        q_copy = copy.deepcopy(q)
        
        shuffled_options = list(q_copy["options"])
        rng.shuffle(shuffled_options)
        
        new_options = []
        new_explanations = {}
        new_correct = ""
        
        for i, opt in enumerate(shuffled_options):
            old_key = opt["key"]
            # We assume there are exactly 4 options per question, but just in case
            new_key = keys[i] if i < len(keys) else str(i)
            
            new_options.append({"key": new_key, "text": opt["text"]})
            new_explanations[new_key] = q_copy["explanations"][old_key]
            
            if q_copy["correct"] == old_key:
                new_correct = new_key
                
        q_copy["options"] = new_options
        q_copy["explanations"] = new_explanations
        q_copy["correct"] = new_correct
        
        result.append(q_copy)

    return result


def get_recently_used_question_ids(
    question_history: list[dict[str, Any]],
    domain: str,
    difficulty: str,
    max_depth: int = MAX_HISTORY_DEPTH,
) -> set[str]:
    """Get question IDs from recent attempts for a given domain/difficulty.

    Parameters
    ----------
    question_history : list[dict]
        List of past attempt records, each containing:
        - domain_key: str
        - difficulty: str
        - question_ids: list[str]
    domain : str
        The domain to filter by.
    difficulty : str
        The difficulty to filter by.
    max_depth : int
        How many recent attempts to look back.

    Returns
    -------
    set[str]
        Set of recently used question IDs.
    """
    relevant = [
        entry for entry in question_history
        if entry.get("domain_key") == domain
        and entry.get("difficulty", "").lower() == difficulty.lower()
    ]

    # Sort by timestamp descending (newest first)
    relevant.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)

    # Collect IDs from the most recent N attempts
    used_ids: set[str] = set()
    for entry in relevant[:max_depth]:
        for qid in entry.get("question_ids", []):
            used_ids.add(qid)

    return used_ids


def create_assessment_attempt(
    domain: str,
    difficulty: str,
    question_history: list[dict[str, Any]] | None = None,
    count: int = QUESTIONS_PER_ASSESSMENT,
) -> dict[str, Any]:
    """Create a new assessment attempt with a fresh set of questions.

    This should be called ONCE when the user starts a new assessment.
    The result is stored in session state and reused during reruns.

    Returns
    -------
    dict containing:
        - questions: list[dict] – the selected questions
        - question_ids: list[str] – IDs for history tracking
        - domain: str
        - difficulty: str
        - seed: int – the random seed used (for reproducibility)
    """
    history = question_history or []
    exclude_ids = get_recently_used_question_ids(history, domain, difficulty)

    # Use a random seed for this attempt (deterministic once set)
    seed = random.randint(0, 2**31 - 1)

    questions = select_questions(
        domain=domain,
        difficulty=difficulty,
        count=count,
        exclude_ids=exclude_ids,
        seed=seed,
    )

    return {
        "questions": questions,
        "question_ids": [q["id"] for q in questions],
        "domain": domain,
        "difficulty": difficulty,
        "seed": seed,
        "count": len(questions),
    }


def save_attempt_to_history(
    question_history: list[dict[str, Any]],
    attempt_record: dict[str, Any],
) -> list[dict[str, Any]]:
    """Add a completed attempt to the question history.

    The history is used by subsequent attempts to avoid repeating
    recently used questions.
    """
    entry = {
        "domain_key": attempt_record.get("domain_key") or attempt_record.get("domain", ""),
        "difficulty": attempt_record.get("difficulty", ""),
        "question_ids": attempt_record.get("question_ids", []),
        "submitted_at": attempt_record.get("submitted_at", ""),
        "attempt_id": attempt_record.get("attempt_id", ""),
    }

    updated = list(question_history)
    updated.append(entry)
    return updated
