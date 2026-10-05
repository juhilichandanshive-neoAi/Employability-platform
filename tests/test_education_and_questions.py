"""Regression and unit tests for Profile Education enhancement and Assessment Question Selection Engine."""

import unittest
from services.question_service import (
    select_questions,
    get_recently_used_question_ids,
    create_assessment_attempt,
    save_attempt_to_history,
    QUESTIONS_PER_ASSESSMENT,
)
from data.question_bank import get_questions_for_domain, EXPANDED_QUESTION_BANK
from services.integration import empty_profile, build_app_data
from neoai.services.employability import profile_completion


class TestQuestionSelectionService(unittest.TestCase):
    def test_pool_size(self):
        """Verify that each domain has at least 50 questions across difficulties."""
        for domain in ("cloud", "cyber"):
            total_questions = sum(
                len(EXPANDED_QUESTION_BANK[domain][diff])
                for diff in ("easy", "moderate", "hard")
            )
            self.assertGreaterEqual(
                total_questions,
                50,
                f"Domain {domain} should have at least 50 questions in the pool, found {total_questions}",
            )

    def test_select_questions_count(self):
        """Test that exactly 15 questions are selected for an attempt."""
        questions = select_questions("cloud", "easy", count=15)
        self.assertEqual(len(questions), 15)
        ids = [q["id"] for q in questions]
        self.assertEqual(len(set(ids)), 15, "All 15 questions must be unique")

    def test_select_questions_structure(self):
        """Test question schema: id, category, text, options, correct, explanations."""
        questions = select_questions("cyber", "moderate", count=5)
        for q in questions:
            self.assertIn("id", q)
            self.assertIn("category", q)
            self.assertIn("text", q)
            self.assertIn("options", q)
            self.assertIn("correct", q)
            self.assertIn("explanations", q)
            self.assertEqual(len(q["options"]), 4)
            keys = {opt["key"] for opt in q["options"]}
            self.assertEqual(keys, {"A", "B", "C", "D"})
            self.assertIn(q["correct"], q["explanations"])

    def test_history_exclusion_avoids_repetition(self):
        """Test that recently used question IDs are not repeated when pool permits."""
        attempt1 = create_assessment_attempt("cloud", "easy", count=15)
        history = save_attempt_to_history([], {
            "domain_key": "cloud",
            "difficulty": "easy",
            "question_ids": attempt1["question_ids"],
            "submitted_at": "2026-10-03 10:00 UTC",
        })

        recent_ids = get_recently_used_question_ids(history, "cloud", "easy")
        self.assertEqual(recent_ids, set(attempt1["question_ids"]))

        attempt2 = create_assessment_attempt("cloud", "easy", question_history=history, count=15)
        overlap = set(attempt1["question_ids"]).intersection(set(attempt2["question_ids"]))
        # Cloud easy pool has enough questions so that attempt 2 has zero overlap with attempt 1
        self.assertEqual(
            len(overlap),
            0,
            f"Expected 0 repeated questions between attempt 1 and attempt 2, got {len(overlap)}: {overlap}",
        )

    def test_graceful_fallback_when_pool_is_small(self):
        """Test that if count exceeds available pool, it still returns questions without crashing."""
        all_ids = {q["id"] for q in get_questions_for_domain("cloud", "easy")}
        # Exclude ALL questions in the pool
        questions = select_questions("cloud", "easy", count=10, exclude_ids=all_ids)
        self.assertEqual(len(questions), 10, "Should fall back and return 10 questions even if all were excluded")

    def test_deterministic_seed(self):
        """Test that identical seed produces identical question selection and order."""
        q1 = select_questions("cloud", "hard", count=10, seed=42)
        q2 = select_questions("cloud", "hard", count=10, seed=42)
        self.assertEqual([q["id"] for q in q1], [q["id"] for q in q2])


class TestProfileEducationEnhancement(unittest.TestCase):
    def test_empty_profile_has_education_entries(self):
        profile = empty_profile()
        self.assertIn("education_entries", profile)
        self.assertEqual(profile["education_entries"], [])

    def test_education_entries_in_build_app_data(self):
        profile = empty_profile()
        profile["name"] = "Priya Sharma"
        profile["email"] = "priya@example.com"
        profile["degree"] = "B.Tech IT"
        profile["education_entries"] = [
            {
                "level": "HSC / 12th Grade",
                "institution": "National Public School",
                "year": "2020",
                "score": "92%",
            },
            {
                "level": "SSC / 10th Grade",
                "institution": "St. Mary's Convent",
                "year": "2018",
                "score": "95%",
            }
        ]

        app_data = build_app_data(profile, None)
        education_list = app_data["education"]
        self.assertEqual(len(education_list), 3)  # Degree + 2 entries
        self.assertEqual(education_list[0]["level"], "B.Tech IT")
        self.assertEqual(education_list[1]["level"], "HSC / 12th Grade")
        self.assertIn("National Public School", education_list[1]["meta"])
        self.assertEqual(education_list[1]["score"], "92%")

    def test_profile_completion_with_education_entries_without_degree(self):
        """Verify profile completion recognizes education_entries even if legacy degree field is empty."""
        profile = empty_profile()
        profile["name"] = "Test User"
        profile["email"] = "user@test.com"
        profile["education_entries"] = [
            {"level": "B.Sc Computer Science", "institution": "XYZ University"}
        ]
        completion = profile_completion(profile)
        self.assertGreater(completion, 0)
        app_data = build_app_data(profile, None)
        edu_step = next(s for s in app_data["profile_steps"] if s["label"] == "Education")
        self.assertEqual(edu_step["status"], "done")


if __name__ == "__main__":
    unittest.main()
