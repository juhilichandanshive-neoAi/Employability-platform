"""Comprehensive tests for Authentication, Enrollment ID, Data Isolation, Education CRUD, Activity Logging, and Security."""

import os
import unittest
import uuid
from pathlib import Path
from streamlit.testing.v1 import AppTest

from tests.session_helpers import authenticated_app, open_login, start_app
from services.db import (
    add_education_entry,
    authenticate_user,
    delete_education_entry,
    generate_enrollment_id,
    get_user_activities,
    get_user_assessment_history,
    get_user_profile,
    get_user_reports_db,
    hash_password,
    init_db,
    log_activity,
    register_user,
    save_assessment_attempt_db,
    save_report_db,
    update_education_entry,
    verify_password,
)
from services.integration import empty_profile, build_app_data

APP_DIR = Path(__file__).resolve().parents[1]


class TestAuthAndEnrollmentSecurity(unittest.TestCase):
    def setUp(self):
        init_db()

    def _rand(self) -> str:
        return uuid.uuid4().hex[:6]

    def test_01_user_registration(self):
        """1. User registration creates account with unique ID and Enrollment ID."""
        r = self._rand()
        user = register_user(f"student1_{r}@example.com", f"studentone_{r}", "SecurePass123!", "Student One")
        self.assertIn("user_id", user)
        self.assertEqual(user["email"], f"student1_{r}@example.com")
        self.assertEqual(user["username"], f"studentone_{r}")
        self.assertTrue(user["enrollment_id"].startswith("EA-2026-"))

    def test_02_duplicate_email_rejection(self):
        """2. Duplicate email registration is rejected with friendly error."""
        r = self._rand()
        email = f"dupe_{r}@example.com"
        register_user(email, f"dupeuser1_{r}", "Pass123456")
        with self.assertRaises(ValueError) as ctx:
            register_user(email, f"dupeuser2_{r}", "Pass123456")
        self.assertIn("email address already exists", str(ctx.exception))

    def test_03_duplicate_username_rejection(self):
        """3. Duplicate username registration is rejected."""
        r = self._rand()
        uname = f"sameusername_{r}"
        register_user(f"unique1_{r}@example.com", uname, "Pass123456")
        with self.assertRaises(ValueError) as ctx:
            register_user(f"unique2_{r}@example.com", uname, "Pass123456")
        self.assertIn("username is already taken", str(ctx.exception))

    def test_04_password_hashing(self):
        """4. Password is never stored in plaintext and is properly hashed."""
        plain = "MySecretPassword99"
        hashed = hash_password(plain)
        self.assertNotEqual(plain, hashed)
        self.assertTrue(hashed.startswith("bcrypt$") or hashed.startswith("pbkdf2_sha256$"))

    def test_05_password_verification(self):
        """5. Password verification accepts correct password and rejects wrong."""
        plain = "ValidPassword123"
        hashed = hash_password(plain)
        self.assertTrue(verify_password(plain, hashed))
        self.assertFalse(verify_password("WrongPassword!", hashed))

    def test_06_invalid_login_rejection(self):
        """6. Invalid login fails without crashing or leaking details."""
        r = self._rand()
        register_user(f"login_test_{r}@example.com", f"logintest_{r}", "CorrectPassword123")
        self.assertIsNone(authenticate_user(f"login_test_{r}@example.com", "IncorrectPassword"))
        self.assertIsNone(authenticate_user("nonexistent@example.com", "AnyPassword"))

    def test_07_successful_login(self):
        """7. Successful login returns authenticated user dict."""
        r = self._rand()
        email = f"login_ok_{r}@example.com"
        uname = f"loginok_{r}"
        register_user(email, uname, "ValidPass456")

        auth_by_email = authenticate_user(email, "ValidPass456")
        self.assertIsNotNone(auth_by_email)
        self.assertEqual(auth_by_email["email"], email)

        auth_by_user = authenticate_user(uname, "ValidPass456")
        self.assertIsNotNone(auth_by_user)
        self.assertEqual(auth_by_user["username"], uname)

    def test_08_enrollment_id_generation(self):
        """8. Generated Enrollment ID adheres to EA-2026-XXXXXX format."""
        eid = generate_enrollment_id(2026)
        self.assertTrue(eid.startswith("EA-2026-"))
        self.assertEqual(len(eid), 14)  # EA-2026- (8) + 6 chars = 14

    def test_09_enrollment_id_uniqueness(self):
        """9. Multiple generated Enrollment IDs are distinct and unique."""
        eids = {generate_enrollment_id() for _ in range(50)}
        self.assertEqual(len(eids), 50)

    def test_10_existing_user_keeps_same_enrollment_id(self):
        """10. Existing user keeps their permanent Enrollment ID across logins."""
        r = self._rand()
        user = register_user(f"persistent_{r}@example.com", f"persistent_{r}", "Pass123456")
        initial_eid = user["enrollment_id"]

        # First login
        auth1 = authenticate_user(f"persistent_{r}", "Pass123456")
        self.assertEqual(auth1["enrollment_id"], initial_eid)

        # Second login
        auth2 = authenticate_user(f"persistent_{r}", "Pass123456")
        self.assertEqual(auth2["enrollment_id"], initial_eid)

    def test_11_logout_clears_authentication(self):
        """11. Logout clears session state and resets authenticated flag."""
        app, _user = authenticated_app()
        self.assertTrue(app.session_state.authenticated)

        # Perform sign out via settings screen
        app.button(key="nav-settings").click().run()
        app.button(key="settings_sign_out").click().run()
        self.assertFalse(app.session_state.authenticated)

    def test_12_unauthorized_page_access_blocked(self):
        """12. Unauthenticated user cannot open protected dashboard directly."""
        app = AppTest.from_file(str(APP_DIR / "app.py"), default_timeout=30).run()
        self.assertFalse(app.session_state.authenticated)
        # Verify protected sidebar buttons are never rendered
        self.assertEqual(len(app.sidebar.button), 0)

    def test_13_user_data_isolation(self):
        """13. User A never sees User B's profile, education, or records."""
        r1, r2 = self._rand(), self._rand()
        user_a = register_user(f"user_a_{r1}@example.com", f"user_a_{r1}", "Pass123456")
        user_b = register_user(f"user_b_{r2}@example.com", f"user_b_{r2}", "Pass123456")

        add_education_entry(user_a["user_id"], {"degree": "B.Tech CS User A", "institution": "College A"})
        add_education_entry(user_b["user_id"], {"degree": "B.Com User B", "institution": "College B"})

        profile_a = get_user_profile(user_a["user_id"])
        profile_b = get_user_profile(user_b["user_id"])

        self.assertEqual(len(profile_a["education_entries"]), 1)
        self.assertEqual(profile_a["education_entries"][0]["degree"], "B.Tech CS User A")

        self.assertEqual(len(profile_b["education_entries"]), 1)
        self.assertEqual(profile_b["education_entries"][0]["degree"], "B.Com User B")

    def test_14_education_add(self):
        """14. Education add stores all specified fields."""
        r = self._rand()
        user = register_user(f"edu_user_{r}@example.com", f"eduuser_{r}", "Pass123456")
        edu_id = add_education_entry(
            user["user_id"],
            {
                "degree": "B.Sc Information Technology",
                "field_of_study": "Information Security",
                "institution": "Tech Institute",
                "start_year": "2020",
                "grad_year": "2024",
                "score": "8.9 CGPA",
                "description": "Graduated with Dean's Honor Roll",
            },
        )
        self.assertTrue(edu_id.startswith("edu_"))
        profile = get_user_profile(user["user_id"])
        entry = profile["education_entries"][0]
        self.assertEqual(entry["degree"], "B.Sc Information Technology")
        self.assertEqual(entry["field_of_study"], "Information Security")
        self.assertEqual(entry["institution"], "Tech Institute")
        self.assertEqual(entry["score"], "8.9 CGPA")

    def test_15_education_edit(self):
        """15. Education edit updates existing entry."""
        r = self._rand()
        user = register_user(f"edu_edit_{r}@example.com", f"eduedit_{r}", "Pass123456")
        edu_id = add_education_entry(user["user_id"], {"degree": "B.Sc", "institution": "Old College"})
        updated = update_education_entry(
            user["user_id"],
            edu_id,
            {"degree": "M.Sc Computer Science", "institution": "New University", "score": "9.2 CGPA"},
        )
        self.assertTrue(updated)
        profile = get_user_profile(user["user_id"])
        self.assertEqual(profile["education_entries"][0]["degree"], "M.Sc Computer Science")
        self.assertEqual(profile["education_entries"][0]["institution"], "New University")

    def test_16_education_delete(self):
        """16. Education delete removes entry cleanly."""
        r = self._rand()
        user = register_user(f"edu_del_{r}@example.com", f"edudel_{r}", "Pass123456")
        edu_id = add_education_entry(user["user_id"], {"degree": "Diploma", "institution": "Polytechnic"})
        self.assertEqual(len(get_user_profile(user["user_id"])["education_entries"]), 1)

        deleted = delete_education_entry(user["user_id"], edu_id)
        self.assertTrue(deleted)
        self.assertEqual(len(get_user_profile(user["user_id"])["education_entries"]), 0)

    def test_17_education_persistence_in_app_data(self):
        """17. Education entries persist and build correctly in app_data."""
        profile = empty_profile()
        profile["education_entries"] = [
            {"degree": "B.E. Computer Science", "institution": "Pune University", "score": "8.5 CGPA"}
        ]
        app_data = build_app_data(profile, None)
        self.assertGreaterEqual(len(app_data["education"]), 1)
        self.assertEqual(app_data["education"][0]["level"], "B.E. Computer Science")

    def test_18_activity_logging(self):
        """18. Applicant activity tracking logs events and timestamps."""
        r = self._rand()
        user = register_user(f"act_user_{r}@example.com", f"actuser_{r}", "Pass123456")
        log_activity(user["user_id"], "test_action", "Profile updated", "Added new skills.")
        activities = get_user_activities(user["user_id"])
        self.assertGreaterEqual(len(activities), 2)  # Account creation + test_action
        titles = [a["title"] for a in activities]
        self.assertIn("Profile updated", titles)

    def test_19_assessment_history_persistence(self):
        """19. Assessment attempts persist in database without data corruption."""
        r = self._rand()
        user = register_user(f"assess_user_{r}@example.com", f"assessuser_{r}", "Pass123456")
        attempt_data = {
            "attempt_id": f"att_test_{r}",
            "domain_key": "cloud",
            "domain_name": "Cloud Computing",
            "difficulty": "Easy",
            "overall_pct": 86.6,
            "correct_count": 13,
            "total": 15,
            "submitted_at": "2026-10-03 10:00 UTC",
            "question_ids": ["ce01", "ce02"],
        }
        save_assessment_attempt_db(user["user_id"], attempt_data)
        history = get_user_assessment_history(user["user_id"])
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["attempt_id"], f"att_test_{r}")
        self.assertEqual(history[0]["overall_pct"], 86.6)

    def test_20_report_generation_persistence(self):
        """20. Report generation records are safely persisted for user."""
        r = self._rand()
        user = register_user(f"rep_user_{r}@example.com", f"repuser_{r}", "Pass123456")
        rep_id = save_report_db(
            user["user_id"],
            f"employability-report-{r}.pdf",
            82.5,
            104800,
            ["Profile summary", "Employability score"],
        )
        self.assertTrue(rep_id.startswith("rep_"))
        reports = get_user_reports_db(user["user_id"])
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["filename"], f"employability-report-{r}.pdf")

    def test_21_no_duplicate_assessment_attempts(self):
        """21. Saving identical attempt_id updates rather than creating duplicate row."""
        r = self._rand()
        user = register_user(f"dupe_att_{r}@example.com", f"dupeatt_{r}", "Pass123456")
        attempt = {
            "attempt_id": f"att_unique_{r}",
            "domain_key": "cyber",
            "domain_name": "Cybersecurity",
            "difficulty": "Moderate",
            "overall_pct": 80.0,
            "correct_count": 12,
            "total": 15,
            "submitted_at": "2026-10-03 11:00 UTC",
        }
        save_assessment_attempt_db(user["user_id"], attempt)
        save_assessment_attempt_db(user["user_id"], attempt)
        history = get_user_assessment_history(user["user_id"])
        self.assertEqual(len(history), 1)

    def test_22_enrollment_id_required_authentication(self):
        """22. Authentication validates Enrollment ID if provided; rejects if mismatch."""
        r = self._rand()
        user = register_user(f"eid_user_{r}@example.com", f"eiduser_{r}", "SecPass123!", "EID User")
        correct_eid = user["enrollment_id"]
        wrong_eid = "EA-2026-999999"

        # Correct enrollment ID matches
        auth_ok = authenticate_user(f"eiduser_{r}", "SecPass123!", enrollment_id_check=correct_eid)
        self.assertIsNotNone(auth_ok)
        self.assertEqual(auth_ok["user_id"], user["user_id"])

        # Wrong enrollment ID is rejected
        auth_bad_eid = authenticate_user(f"eiduser_{r}", "SecPass123!", enrollment_id_check=wrong_eid)
        self.assertIsNone(auth_bad_eid)

        # Wrong password with correct enrollment ID is rejected
        auth_bad_pwd = authenticate_user(f"eiduser_{r}", "WrongPassword!", enrollment_id_check=correct_eid)
        self.assertIsNone(auth_bad_pwd)

    def test_23_separate_auth_screens_flow(self):
        """23. Login and Registration are strictly separate screens with success step."""
        app = start_app()
        self.assertEqual(app.session_state.auth_page, "landing")
        open_login(app)
        self.assertEqual(app.session_state.auth_page, "login")

        # Verify registration fields are NOT on the login page
        reg_keys = [k for k in app.session_state.keys() if "reg_" in str(k)]
        self.assertEqual(len(reg_keys), 0)

        # Navigate to registration page
        self.assertIn("btn-goto-register", [b.key for b in app.button])
        app.button(key="btn-goto-register").click().run()
        self.assertEqual(app.session_state.auth_page, "register")

        r = self._rand()
        app.text_input(key="reg_name_input").input(f"Test Student {r}")
        app.text_input(key="reg_email_input").input(f"screen_test_{r}@example.com")
        app.text_input(key="reg_username_input").input(f"screentest_{r}")
        app.text_input(key="reg_password_input").input("StrongPass123!")
        app.text_input(key="reg_confirm_password_input").input("StrongPass123!")
        app.button(key="btn-submit-register").click().run()

        # Success page must be active with generated Enrollment ID
        self.assertEqual(app.session_state.auth_page, "success")
        new_eid = app.session_state._registered_enrollment_id
        self.assertTrue(new_eid.startswith("EA-2026-"))

        # Continue to Sign In returns to login with fields prefilled
        app.button(key="btn-continue-to-login").click().run()
        self.assertEqual(app.session_state.auth_page, "login")
        self.assertEqual(app.session_state.login_enrollment_id, new_eid)


if __name__ == "__main__":
    unittest.main()

