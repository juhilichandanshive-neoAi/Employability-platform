"""End-to-end regression coverage for the session-backed Streamlit flow."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from tests.session_helpers import authenticated_app  # noqa: E402

from data.dummy_data import (  # noqa: E402
    ASSESSMENT_DIFFICULTIES,
    ASSESSMENT_DOMAINS,
    QUESTION_BANK,
)
from services.integration import calculate_score  # noqa: E402


class EmployabilityAppFlowTest(unittest.TestCase):
    """Exercise the existing successful profile-to-report user journey."""

    def assert_no_app_exceptions(self, app: AppTest, step: str) -> None:
        messages = [getattr(item, "message", str(item)) for item in app.exception]
        self.assertEqual(
            len(app.exception),
            0,
            f"Expected zero Streamlit app exceptions after {step}; got {messages}",
        )

    def click(self, app: AppTest, key: str, step: str) -> None:
        matches = [button for button in app.button if button.key == key]
        self.assertEqual(
            len(matches),
            1,
            f"Expected one button with key {key!r} during {step}",
        )
        matches[0].click().run()
        self.assert_no_app_exceptions(app, step)

    def test_profile_assessment_recommendations_analytics_and_pdf(self) -> None:
        app, _user = authenticated_app()
        self.assert_no_app_exceptions(app, "session entry")
        self.assertTrue(app.session_state.authenticated)
        self.assertEqual(app.session_state.page, "dashboard")

        self.click(app, "nav-profile", "open profile")
        for key, value in {
            "profile_name": "AppTest Student",
            "profile_email": "apptest@example.test",
            "profile_degree": "Computer Science",
            "profile_semester": "Semester 6",
        }.items():
            app.text_input(key=key).set_value(value)
        app.number_input(key="profile_cgpa").set_value(8.0)
        app.run()
        self.assert_no_app_exceptions(app, "enter profile details")

        for skill in ("Python", "Linux", "AWS core"):
            app.text_input(key="new_skill_name").set_value(skill)
            app.slider(key="new_skill_level").set_value(1)
            self.click(
                app,
                "FormSubmitter:add-skill-form-Add or update skill",
                f"add profile skill {skill}",
            )

        self.click(app, "save-changes-bottom", "save profile")
        self.assertTrue(app.session_state.profile_saved)
        self.assertEqual(len(app.session_state.profile["skills"]), 3)

        # Select and complete one configured assessment.
        self.click(app, "nav-assessment", "open assessment")
        domain = ASSESSMENT_DOMAINS[0]
        difficulty = ASSESSMENT_DIFFICULTIES[0]
        self.click(app, f"btn-domain-{domain['key']}", "select assessment domain")
        self.assertEqual(app.session_state._pick_domain, domain["key"])
        self.click(
            app,
            f"btn-diff-{difficulty['key']}",
            "select assessment difficulty",
        )
        self.assertEqual(app.session_state._pick_difficulty, difficulty["key"])
        self.click(app, "start-assessment", "confirm assessment selection")
        self.assertEqual(app.session_state.assessment_domain, domain["key"])
        self.assertEqual(app.session_state.assessment_difficulty, difficulty["key"])
        self.click(app, "instructions-start", "start assessment")

        questions = app.session_state.assessment_questions
        for index, question in enumerate(questions):
            option = question["options"][0]
            self.click(
                app,
                f"btn-opt-{question['id']}-{option['key']}",
                f"answer assessment question {index + 1}",
            )
            if index < len(questions) - 1:
                self.click(app, "q-next", f"advance from question {index + 1}")

        self.click(app, "q-next", "open assessment submission confirmation")
        dialog_buttons = [
            button
            for button in app.get("dialog")[0].button
            if button.key == "confirm-dialog-submit"
        ]
        self.assertEqual(len(dialog_buttons), 1)
        dialog_buttons[0].click().run()
        self.assert_no_app_exceptions(app, "submit assessment")

        self.assertTrue(app.session_state.assessment_submitted)
        self.assertEqual(len(app.session_state.assessment_history), 1)
        assessment = app.session_state.assessment_result
        data = app.session_state.app_data
        self.assertEqual(assessment["status"], "completed")
        self.assertEqual(assessment["total"], len(questions))

        # The app's displayed score must come from the existing scoring service.
        expected_score = calculate_score(app.session_state.profile, assessment)
        self.assertEqual(data["score"]["overall"], expected_score["overall"])
        self.assertAlmostEqual(sum(data["score"]["weights"].values()), 1.0)

        # Navigate each requested result area and assert its session data exists.
        for page in (
            "score",
            "skill_gap",
            "careers",
            "certifications",
            "roadmap",
            "analytics",
            "settings",
        ):
            self.click(app, f"nav-{page}", f"open {page}")
            self.assertEqual(app.session_state.page, page)

            if page == "score":
                rendered = "\n".join(str(item.value) for item in app.markdown)
                self.assertIn(str(expected_score["overall"]), rendered)
            elif page == "skill_gap":
                self.assertGreater(data["skill_gap"]["compared_count"], 0)
            elif page == "careers":
                self.assertTrue(data["career_matches"])
            elif page == "certifications":
                self.assertTrue(data["certification_recommendations"])
            elif page == "roadmap":
                self.assertTrue(data["roadmap"]["tasks"])
            elif page == "analytics":
                self.assertEqual(data["analytics"]["assessment_count"], 1)
                self.assertEqual(len(data["analytics"]["attempt_history"]), 1)

        # Generate and verify a real, downloadable PDF report.
        self.click(app, "nav-reports", "open reports")
        self.click(app, "generate-session-report", "generate session PDF")
        pdf = app.session_state.current_report_pdf
        self.assertIsInstance(pdf, bytes)
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertIn(b"%%EOF", pdf[-32:])
        self.assertTrue(app.session_state.current_report_filename.endswith(".pdf"))
        self.assertEqual(len(app.session_state.generated_reports), 1)
        self.assertTrue(
            any(button.key == "dl-full" for button in app.get("download_button"))
        )
        self.assert_no_app_exceptions(app, "finish PDF report flow")


if __name__ == "__main__":
    unittest.main()
