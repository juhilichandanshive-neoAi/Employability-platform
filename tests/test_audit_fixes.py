"""Comprehensive audit, regression, and end-to-end tests for EmployaAI."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from streamlit.testing.v1 import AppTest

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components import charts  # noqa: E402
from components.html import flatten_html  # noqa: E402
from services import auth  # noqa: E402
from services.integration import calculate_score, empty_profile, calculate_skill_gaps  # noqa: E402
from tests.session_helpers import authenticated_app, start_app  # noqa: E402
from services.reporting import generate_session_report  # noqa: E402
from utils import state  # noqa: E402


class PlotlyChartRegressionTest(unittest.TestCase):
    """Test Plotly chart edge cases, scalar/list normalizations, and empty values."""

    def test_as_target_normalization(self):
        """Regression test for TypeError: unsupported operand type(s) for +: 'int' and 'list'."""
        self.assertIsNone(charts.as_target(None))
        self.assertIsNone(charts.as_target([]))
        self.assertIsNone(charts.as_target("invalid"))
        self.assertEqual(charts.as_target(0), 0.0)
        self.assertEqual(charts.as_target(50), 50.0)
        self.assertEqual(charts.as_target(100), 100.0)
        self.assertEqual(charts.as_target([75.5]), 75.5)
        self.assertEqual(charts.as_target(["80"]), 80.0)

    def test_as_series_normalization(self):
        self.assertEqual(charts.as_series(None), [])
        self.assertEqual(charts.as_series([]), [])
        self.assertEqual(charts.as_series(50), [50.0])
        self.assertEqual(charts.as_series([10, "20", None, 30]), [10.0, 20.0, 0.0, 30.0])

    def test_build_line_fig_chart_edge_cases(self):
        """Test build_line_fig with every combination of scalar and list targets/cohorts."""
        x = ["Attempt 1", "Attempt 2"]
        student = [70, 85]

        # target = None
        fig = charts.build_line_fig(x, student, cohort=None, target=None)
        self.assertIsNotNone(fig)

        # target = [] (the exact bug that caused the crash)
        fig = charts.build_line_fig(x, student, cohort=[], target=[])
        self.assertIsNotNone(fig)

        # target = 0
        fig = charts.build_line_fig(x, student, cohort=None, target=0)
        self.assertIsNotNone(fig)

        # target = 50
        fig = charts.build_line_fig(x, student, cohort=50, target=50)
        self.assertIsNotNone(fig)

        # target = 100
        fig = charts.build_line_fig(x, student, cohort=[60, 75], target=100)
        self.assertIsNotNone(fig)

        # empty student series returns None
        fig = charts.build_line_fig([], [], cohort=None, target=None)
        self.assertIsNone(fig)

        # single point
        fig = charts.build_line_fig(["Attempt 1"], [80], cohort=None, target=[])
        self.assertIsNotNone(fig)


class HtmlRenderingTest(unittest.TestCase):
    """Test HTML flattening and indentation cleanup to prevent markdown code blocks."""

    def test_flatten_html_removes_multiline_indentation(self):
        raw_snippet = """
        <div class="ea-card">
            <span class="ea-badge ea-badge-neutral">Not started</span>
        </div>
        """
        flattened = flatten_html(raw_snippet)
        self.assertFalse(flattened.startswith("    "))
        self.assertIn('<div class="ea-card">', flattened)
        self.assertIn('<span class="ea-badge ea-badge-neutral">Not started</span>', flattened)
        self.assertIn("</div>", flattened)
        # Verify non-empty lines are separated by space
        self.assertIn('"> <span', flattened)


class AuthServicesTest(unittest.TestCase):
    """Test Google OIDC auth detection, profile extraction, and logout behavior."""

    def test_google_auth_configured_with_placeholders(self):
        with patch.object(auth, "auth_secrets", return_value={"client_id": "xxx"}):
            self.assertFalse(auth.google_auth_configured())

    def test_google_auth_configured_with_valid_config(self):
        valid = {
            "client_id": "real-client-id.apps.googleusercontent.com",
            "client_secret": "real-client-secret-12345",
            "cookie_secret": "a-long-random-cookie-secret-32-chars",
            "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
            "redirect_uri": "http://localhost:8501/oauth2callback",
        }
        with patch.object(auth, "auth_secrets", return_value=valid):
            self.assertTrue(auth.google_auth_configured())

    def test_display_name_from_oidc(self):
        self.assertEqual(auth.display_name_from_oidc({"name": "Mandar Student"}), "Mandar Student")
        self.assertEqual(
            auth.display_name_from_oidc({"given_name": "Mandar", "family_name": "S"}),
            "Mandar S",
        )
        self.assertEqual(auth.display_name_from_oidc({"email": "student@example.com"}), "student")
        self.assertEqual(auth.display_name_from_oidc({}), "")


class EndToEndAppFlowTest(unittest.TestCase):
    """Test full session flow, profile editing, empty states, and PDF generation."""

    def test_app_starts_and_renders_login(self):
        app = start_app()
        self.assertEqual(len(app.exception), 0)
        self.assertFalse(app.session_state.authenticated)
        self.assertEqual(app.session_state.auth_page, "landing")

    def test_navigation_and_empty_states(self):
        """Test navigating all 11 live screens without assessment (empty states)."""
        app, _user = authenticated_app()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(app.session_state.authenticated)
        self.assertEqual(app.session_state.page, "dashboard")

        # Test each live destination in an unassessed state
        for destination in (
            "profile",
            "assessment",
            "score",
            "skill_gap",
            "roadmap",
            "certifications",
            "careers",
            "analytics",
            "reports",
            "settings",
            "dashboard",
        ):
            app.button(key=f"nav-{destination}").click().run()
            self.assertEqual(
                len(app.exception),
                0,
                f"Exception navigating to {destination}: {[e.message for e in app.exception]}",
            )
            self.assertEqual(app.session_state.page, destination)

    def test_profile_subitem_lifecycle_without_state_clobber(self):
        """Verify adding and removing skills/projects doesn't crash Streamlit state lifecycle."""
        app, _user = authenticated_app()
        app.button(key="nav-profile").click().run()

        # Type in full name
        app.text_input(key="profile_name").set_value("Testing Lifecycle")
        app.run()

        # Add a skill
        app.text_input(key="new_skill_name").set_value("Python")
        app.slider(key="new_skill_level").set_value(4)
        app.button(key="FormSubmitter:add-skill-form-Add or update skill").click().run()
        self.assertEqual(len(app.exception), 0)

        # Verify name is preserved
        self.assertEqual(app.session_state.profile["skills"][0]["name"], "Python")
        self.assertEqual(app.text_input(key="profile_name").value, "Testing Lifecycle")

        # Remove the skill
        app.button(key="remove-skill-0").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.session_state.profile["skills"]), 0)

    def test_settings_logout_flow(self):
        """Test sign-out in settings clears authentication and returns to login."""
        app, _user = authenticated_app()
        self.assertTrue(app.session_state.authenticated)

        app.button(key="nav-settings").click().run()
        self.assertEqual(app.session_state.page, "settings")

        app.button(key="settings_sign_out").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertFalse(app.session_state.authenticated)
        self.assertTrue(app.session_state.get("_user_signed_out"))


class AssessmentAndReportingRegressionTest(unittest.TestCase):
    """Test assessment scoring, attempt deduplication, and PDF generation."""

    def test_score_assessment_all_correct(self):
        from data.dummy_data import QUESTION_BANK
        from neoai.services.assessment import score_assessment
        questions = QUESTION_BANK["cloud"]
        answers = {q["id"]: q["correct"] for q in questions}
        result = score_assessment(questions, answers)
        self.assertEqual(result["correct_count"], len(questions))
        self.assertEqual(result["overall_pct"], 100)
        self.assertTrue(all(c["pct"] == 100 for c in result["categories"]))

    def test_score_assessment_all_incorrect(self):
        from data.dummy_data import QUESTION_BANK
        from neoai.services.assessment import score_assessment
        questions = QUESTION_BANK["cloud"]
        wrong_answers = {}
        for q in questions:
            for opt in q["options"]:
                if opt["key"] != q["correct"]:
                    wrong_answers[q["id"]] = opt["key"]
                    break
        result = score_assessment(questions, wrong_answers)
        self.assertEqual(result["correct_count"], 0)
        self.assertEqual(result["overall_pct"], 0)
        self.assertTrue(all(c["pct"] == 0 for c in result["categories"]))

    def test_score_assessment_mixed(self):
        from data.dummy_data import QUESTION_BANK
        from neoai.services.assessment import score_assessment
        questions = QUESTION_BANK["cloud"]
        half = len(questions) // 2
        answers = {}
        for i, q in enumerate(questions):
            if i < half:
                answers[q["id"]] = q["correct"]
            else:
                for opt in q["options"]:
                    if opt["key"] != q["correct"]:
                        answers[q["id"]] = opt["key"]
                        break
        result = score_assessment(questions, answers)
        self.assertEqual(result["correct_count"], half)
        expected_pct = round(half / len(questions) * 100)
        self.assertEqual(result["overall_pct"], expected_pct)

    def test_generate_development_plan_pdf(self):
        from services.integration import build_app_data
        from services.reporting import generate_development_plan_pdf
        app_data = build_app_data(
            profile={
                "name": "Mandar Student",
                "email": "student@example.test",
                "degree": "B.Tech Computer Science",
                "semester": "Semester 6",
                "cgpa": 8.5,
                "target_role": "Cloud / DevOps Engineer",
                "skills": [
                    {"name": "Python", "level": 4},
                    {"name": "Linux", "level": 3},
                ],
                "projects": [{"title": "Cloud Infra Automation"}],
                "certifications": [{"name": "AWS Certified Cloud Practitioner"}],
            },
            assessment=None,
        )
        pdf_bytes, filename = generate_development_plan_pdf(app_data)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertTrue(b"%%EOF" in pdf_bytes or len(pdf_bytes) > 1000)
        self.assertTrue(filename.endswith(".pdf"))
    def test_assessment_history_deduplication(self):
        from services.integration import build_app_data, empty_profile
        attempt = {
            "attempt_id": "att_cloud_12345",
            "domain_key": "cloud",
            "domain_name": "Cloud Computing",
            "submitted_at": "2026-10-01 12:00 UTC",
            "overall_pct": 80,
            "categories": [{"name": "Core", "pct": 80}],
        }
        # Simulate multiple repeated runs appending the same attempt
        history = [attempt, dict(attempt), dict(attempt)]
        app_data = build_app_data(
            profile=empty_profile(),
            assessment=None,
            assessment_history=history,
        )
        self.assertEqual(len(app_data["analytics"]["attempt_history"]), 1)
        self.assertEqual(app_data["analytics"]["attempt_history"][0]["score"], "80%")


if __name__ == "__main__":
    unittest.main()
