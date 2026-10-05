import streamlit as st

from services.auth import apply_oidc_user_to_session, logout_identity, oidc_user_logged_in
from services.integration import empty_profile
from services.session import refresh_app_data

# Screens actually wired into the running app. Nav only ever shows entries
# for screens in this set - no dead links, no "coming soon" pages.
LIVE_SCREENS = {
    "dashboard", "profile", "assessment", "score", "skill_gap", "roadmap",
    "certifications", "careers", "jobs", "analytics", "activity", "reports", "settings",
}

_ALL_NAV_ITEMS = [
    ("MAIN", [
        ("dashboard", "Dashboard", None),
        ("profile", "Profile", None),
        ("assessment", "Assessment", None),
    ]),
    ("INSIGHTS", [
        ("score", "Employability Score", None),
        ("skill_gap", "Skill Gap", None),
        ("roadmap", "Learning Roadmap", None),
        ("certifications", "Certifications", None),
        ("careers", "Career Suggestions", None),
        ("jobs", "Job Opportunities", None),
    ]),
    ("OUTPUT", [
        ("analytics", "Analytics", None),
        ("activity", "Activity Log", None),
        ("reports", "Reports", None),
        ("settings", "Settings", None),
    ]),
]

NAV_ITEMS = [
    (group, [item for item in items if item[0] in LIVE_SCREENS])
    for group, items in _ALL_NAV_ITEMS
]
NAV_ITEMS = [(group, items) for group, items in NAV_ITEMS if items]


def init_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "page" not in st.session_state:
        query_page = st.query_params.get("page") if hasattr(st, "query_params") else None
        if query_page and query_page in LIVE_SCREENS:
            st.session_state.page = query_page
        else:
            st.session_state.page = "dashboard"
    if "profile" not in st.session_state:
        st.session_state.profile = empty_profile()
    st.session_state.setdefault("auth_provider", "local")
    st.session_state.setdefault("profile_saved", False)
    st.session_state.setdefault("assessment_result", None)
    st.session_state.setdefault("assessment_history", [])
    st.session_state.setdefault("generated_reports", [])
    st.session_state.setdefault("current_report_pdf", None)
    st.session_state.setdefault("current_report_filename", None)
    reset_assessment_state()
    if oidc_user_logged_in() and not st.session_state.get("_user_signed_out"):
        first_google_entry = not st.session_state.authenticated
        apply_oidc_user_to_session()
        if first_google_entry:
            query_page = st.query_params.get("page") if hasattr(st, "query_params") else None
            if query_page and query_page in LIVE_SCREENS:
                st.session_state.page = query_page
            else:
                st.session_state.page = "dashboard"
    refresh_app_data()


def reset_assessment_state():
    if "assessment_domain" not in st.session_state:
        st.session_state.assessment_domain = None
    if "assessment_difficulty" not in st.session_state:
        st.session_state.assessment_difficulty = None
    if "assessment_started" not in st.session_state:
        st.session_state.assessment_started = False
    if "assessment_submitted" not in st.session_state:
        st.session_state.assessment_submitted = False
    if "assessment_current_q" not in st.session_state:
        st.session_state.assessment_current_q = 0
    if "assessment_answers" not in st.session_state:
        st.session_state.assessment_answers = {}
    if "assessment_result" not in st.session_state:
        st.session_state.assessment_result = None


def go_to(page: str):
    st.session_state.page = page
    if hasattr(st, "query_params"):
        st.query_params["page"] = page


def logout():
    google_session = oidc_user_logged_in()
    user_id = st.session_state.get("current_user_id")
    if user_id:
        try:
            from services.db import log_activity
            log_activity(user_id, "logout", "Logged out", "User securely signed out of EmployaAI.")
        except Exception:
            pass
    st.session_state.clear()
    st.session_state["_user_signed_out"] = True
    st.session_state.authenticated = False
    st.session_state["current_user_id"] = None
    st.session_state["current_enrollment_id"] = None
    st.session_state.auth_provider = "local"
    st.session_state.page = "dashboard"
    st.session_state.profile = empty_profile()
    st.session_state.profile_saved = False
    st.session_state.assessment_result = None
    st.session_state.assessment_history = []
    st.session_state.generated_reports = []
    st.session_state.current_report_pdf = None
    st.session_state.current_report_filename = None
    reset_assessment_state()
    refresh_app_data()
    if google_session:
        logout_identity()
