"""Streamlit session state and output refresh helpers with database integration."""

from __future__ import annotations

from typing import Any

import streamlit as st

from services.db import (
    get_user_assessment_history,
    get_user_profile,
    get_user_question_history_db,
    get_user_reports_db,
)
from services.integration import build_app_data, empty_profile


def initialize_session() -> None:
    st.session_state.setdefault("profile", empty_profile())
    st.session_state.setdefault("profile_saved", False)
    st.session_state.setdefault("assessment_result", None)
    st.session_state.setdefault("assessment_history", [])
    st.session_state.setdefault("generated_reports", [])
    st.session_state.setdefault("current_report_pdf", None)
    st.session_state.setdefault("current_report_filename", None)
    st.session_state.setdefault("question_history", [])
    st.session_state.setdefault("current_user_id", None)
    st.session_state.setdefault("current_enrollment_id", None)


def load_user_session(user_id: str, enrollment_id: str | None = None) -> None:
    """Load authenticated user's isolated data from database into session state."""
    st.session_state.current_user_id = user_id
    profile = get_user_profile(user_id)
    if enrollment_id:
        profile["enrolment_id"] = enrollment_id
        st.session_state.current_enrollment_id = enrollment_id
    elif profile.get("enrolment_id"):
        st.session_state.current_enrollment_id = profile["enrolment_id"]

    st.session_state.profile = profile
    st.session_state.profile_saved = True

    # Assessment history
    attempts = get_user_assessment_history(user_id)
    st.session_state.assessment_history = attempts
    if attempts:
        st.session_state.assessment_result = attempts[-1]

    # Question history for non-repetition
    st.session_state.question_history = get_user_question_history_db(user_id)

    # Generated reports
    st.session_state.generated_reports = get_user_reports_db(user_id)

    refresh_app_data()


def refresh_app_data() -> dict[str, Any]:
    initialize_session()
    result = build_app_data(
        st.session_state.profile,
        st.session_state.assessment_result,
        st.session_state.assessment_history,
        st.session_state.generated_reports,
    )
    st.session_state["app_data"] = result
    return result


def current_app_data() -> dict[str, Any]:
    return st.session_state.get("app_data") or refresh_app_data()