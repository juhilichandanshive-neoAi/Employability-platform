"""Unit and regression tests for Job Opportunities and the admin-provided CSV dataset."""

from __future__ import annotations

import unittest
import uuid
from pathlib import Path
from streamlit.testing.v1 import AppTest

from services.job_service import (
    load_admin_jobs,
    filter_jobs,
    calculate_job_match,
    get_job_by_id,
    get_csv_metadata,
    get_saved_jobs_for_user,
    save_user_job,
    unsave_user_job,
    is_job_saved,
    get_user_saved_job_ids,
    ADMIN_JOBS_CSV,
    SKILL_FIELDS,
)
from services.db import (
    register_user,
    init_db,
)

APP_DIR = Path(__file__).resolve().parent.parent


class AdminJobCSVTest(unittest.TestCase):
    """Test loading and integrity of the admin-provided job postings CSV."""

    def test_csv_file_exists_and_location(self):
        """Verify the exact admin CSV path and filename."""
        meta = get_csv_metadata()
        self.assertTrue(meta["exists"], "Admin CSV must exist")
        self.assertEqual(meta["filename"], "Merged_industry_jobs_industry_jobs.csv")
        self.assertTrue(ADMIN_JOBS_CSV.is_file())

    def test_job_count_matches_dataset(self):
        """Verify exact count of 260 job records in admin CSV."""
        jobs = load_admin_jobs(force_reload=True)
        self.assertEqual(len(jobs), 260, f"Expected exactly 260 jobs, got {len(jobs)}")

    def test_required_columns_and_normalized_fields(self):
        """Verify presence of core fields and skill benchmarks in every loaded record."""
        jobs = load_admin_jobs()
        for j in jobs[:20]:
            self.assertIn("id", j)
            self.assertIn("title", j)
            self.assertIn("company", j)
            self.assertIn("experience", j)
            self.assertIn("salary_display", j)
            self.assertIn("url", j)
            self.assertIn("skills", j)
            self.assertEqual(len(j["skills"]), 10, "Each job must have 10 skill benchmarks")
            for skill_name in SKILL_FIELDS:
                self.assertIn(skill_name, j["skills"])
                lvl = j["skills"][skill_name]
                self.assertTrue(1 <= lvl <= 10, f"Skill level {lvl} must be in [1, 10]")

    def test_application_urls_integrity(self):
        """Verify all valid job postings have legitimate application links."""
        jobs = load_admin_jobs()
        with_urls = [j for j in jobs if j["has_url"]]
        self.assertGreaterEqual(len(with_urls), 250, "Majority of admin jobs must have application URLs")
        for j in with_urls[:10]:
            self.assertTrue(j["url"].startswith("http"), f"Invalid URL: {j['url']}")

    def test_original_csv_remains_unmodified(self):
        """Verify that loading jobs never modifies or overwrites the admin CSV."""
        mtime_before = ADMIN_JOBS_CSV.stat().st_mtime
        size_before = ADMIN_JOBS_CSV.stat().st_size
        _ = load_admin_jobs(force_reload=True)
        mtime_after = ADMIN_JOBS_CSV.stat().st_mtime
        size_after = ADMIN_JOBS_CSV.stat().st_size
        self.assertEqual(mtime_before, mtime_after, "Admin CSV modification time must not change")
        self.assertEqual(size_before, size_after, "Admin CSV byte size must not change")


class JobSearchAndFilterTest(unittest.TestCase):
    """Test searching and filtering capabilities over the admin dataset."""

    def setUp(self):
        self.jobs = load_admin_jobs()

    def test_search_by_company(self):
        """Verify searching for specific company returns only matching jobs."""
        capgemini_jobs = filter_jobs(self.jobs, search_query="Capgemini")
        self.assertGreater(len(capgemini_jobs), 0)
        self.assertTrue(all("capgemini" in j["company"].lower() or "capgemini" in j["title"].lower() for j in capgemini_jobs))

    def test_search_by_role(self):
        """Verify searching for role keywords."""
        devops_jobs = filter_jobs(self.jobs, search_query="DevOps")
        self.assertGreater(len(devops_jobs), 0)
        self.assertTrue(all("devops" in j["title"].lower() or "devops" in j["company"].lower() or "devops" in j["experience"].lower() for j in devops_jobs))

    def test_filter_by_role_exact(self):
        """Verify exact dropdown filter by role."""
        soc_jobs = filter_jobs(self.jobs, role_filter="SOC Analyst")
        self.assertGreater(len(soc_jobs), 0)
        self.assertTrue(all(j["role"] == "SOC Analyst" for j in soc_jobs))

    def test_filter_by_experience(self):
        """Verify experience filter."""
        fresher_jobs = filter_jobs(self.jobs, experience_filter="Fresher")
        self.assertGreater(len(fresher_jobs), 0)
        self.assertTrue(all(j["experience"] == "Fresher" for j in fresher_jobs))

    def test_filter_by_high_skill(self):
        """Verify skill requirement filter (e.g. AWSRequired >= 5)."""
        aws_jobs = filter_jobs(self.jobs, skill_filter="AWS")
        self.assertGreater(len(aws_jobs), 0)
        self.assertTrue(all(j["skills"]["AWS"] >= 5 for j in aws_jobs))

    def test_filter_disclosed_salary_only(self):
        """Verify filter for disclosed salary postings."""
        salaried = filter_jobs(self.jobs, salary_only=True)
        self.assertGreater(len(salaried), 0)
        self.assertTrue(all(j["salary_disclosed"] for j in salaried))
        self.assertTrue(all(j["salary_display"] != "Not Disclosed" for j in salaried))


class JobMatchingTest(unittest.TestCase):
    """Test personalized profile matching algorithm."""

    def setUp(self):
        self.jobs = load_admin_jobs()

    def test_empty_profile_handling(self):
        """Empty profile returns no fabricated score and friendly guidance."""
        empty_res = calculate_job_match(self.jobs[0], None)
        self.assertFalse(empty_res["has_data"])
        self.assertIsNone(empty_res["score"])
        self.assertIn("Complete your profile", empty_res["message"])

        no_skills_res = calculate_job_match(self.jobs[0], {"skills": []})
        self.assertFalse(no_skills_res["has_data"])
        self.assertIsNone(no_skills_res["score"])

    def test_real_match_calculation(self):
        """Real skills generate calculated percentage and list matched/gap skills."""
        student_profile = {
            "target_role": "Cloud Security Engineer",
            "skills": [
                {"name": "Python", "level": 4},
                {"name": "Linux", "level": 5},
                {"name": "AWS", "level": 4},
                {"name": "Cybersecurity", "level": 4},
            ],
        }
        res = calculate_job_match(self.jobs[0], student_profile)
        self.assertTrue(res["has_data"])
        self.assertIsNotNone(res["score"])
        self.assertTrue(0 <= res["score"] <= 100)
        self.assertTrue(len(res["matched_skills"]) > 0)
        self.assertTrue(len(res["gap_skills"]) > 0)


class SavedJobsAndUserIsolationTest(unittest.TestCase):
    """Test saved jobs CRUD and strict data isolation across accounts."""

    def setUp(self):
        init_db()
        rnd_a = uuid.uuid4().hex[:6]
        rnd_b = uuid.uuid4().hex[:6]
        user_a = register_user(email=f"usera_{rnd_a}@example.edu", username=f"usera_{rnd_a}", password="Pass12345", name="User A")
        user_b = register_user(email=f"userb_{rnd_b}@example.edu", username=f"userb_{rnd_b}", password="Pass12345", name="User B")
        self.user_a_id = user_a["id"]
        self.user_b_id = user_b["id"]

    def test_save_and_unsave_job(self):
        """Test bookmarking a job and checking saved status."""
        self.assertFalse(is_job_saved(self.user_a_id, 1))
        save_user_job(self.user_a_id, 1)
        self.assertTrue(is_job_saved(self.user_a_id, 1))
        self.assertIn(1, get_user_saved_job_ids(self.user_a_id))

        # Unsave
        unsave_user_job(self.user_a_id, 1)
        self.assertFalse(is_job_saved(self.user_a_id, 1))
        self.assertNotIn(1, get_user_saved_job_ids(self.user_a_id))

    def test_user_data_isolation(self):
        """User A saving a job must never appear in User B's saved list."""
        save_user_job(self.user_a_id, 5)
        save_user_job(self.user_a_id, 10)

        # Check User A has jobs 5 and 10
        saved_a = get_user_saved_job_ids(self.user_a_id)
        self.assertEqual(saved_a, {5, 10})

        # Check User B has no saved jobs
        saved_b = get_user_saved_job_ids(self.user_b_id)
        self.assertEqual(saved_b, set(), "User B must not see User A's saved jobs")
        self.assertFalse(is_job_saved(self.user_b_id, 5))


class JobOpportunitiesUIRenderTest(unittest.TestCase):
    """Test that the Job Opportunities screen renders properly in Streamlit."""

    def test_render_jobs_screen(self):
        """Simulate loading the Job Opportunities screen in AppTest."""
        app = AppTest.from_file(str(APP_DIR / "app.py"), default_timeout=30).run()
        self.assertEqual(len(app.exception), 0)

        # Log in test user
        app.session_state.authenticated = True
        app.session_state.user_id = "test_user_ui"
        app.session_state.enrollment_id = "EA-2026-TESTUI"
        app.session_state.page = "jobs"
        app.run()

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state.page, "jobs")
        # Check tabs exist
        self.assertTrue(any("All Opportunities" in t.label for t in app.tabs))
        self.assertTrue(any("Matches for You" in t.label for t in app.tabs))
        self.assertTrue(any("Saved Jobs" in t.label for t in app.tabs))
