"""Streamlit session state and output refresh helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st

from services.integration import build_app_data, empty_profile


def initialize_session() -> None:
    st.session_state.setdefault("profile", empty_profile())
    st.session_state.setdefault("profile_saved", False)
    st.session_state.setdefault("assessment_result", None)
    st.session_state.setdefault("assessment_history", [])
    st.session_state.setdefault("generated_reports", [])
    st.session_state.setdefault("current_report_pdf", None)
    st.session_state.setdefault("current_report_filename", None)


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