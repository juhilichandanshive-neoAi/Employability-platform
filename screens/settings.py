import streamlit as st
from components.cards import panel, section_header
from components.html import render_html
from services.session import current_app_data
from utils.state import go_to, logout


def render():
    profile = current_app_data()["profile"]
    section_header("Settings", "Account and notification preferences.")

    render_html("<div style='height:16px'></div>")
    with panel("settings-account", "profile", "Account"):
        provider_label = "Google Sign-In" if st.session_state.get("auth_provider") == "google" else "Local session"
        st.text_input("Authentication provider", value=provider_label, disabled=True)
        st.text_input("Email", value=profile.get("email") or "", disabled=True)
        st.text_input("Phone", value=profile.get("phone") or "", disabled=True)
        st.caption("Contact details can be updated in your Profile. Local session information is kept during your browser session.")
        if st.button("Edit profile details", key="settings_go_profile"):
            go_to("profile")
            st.rerun()

    render_html("<div style='height:16px'></div>")
    with panel("settings-notifications", "bell", "Notifications"):
        st.checkbox("Weekly score summary email", key="setting_weekly_summary")
        st.checkbox("Reminders before an assessment opens", key="setting_assessment_reminders")
        st.checkbox("New job matches", key="setting_job_matches")
        st.caption("Notification preferences are local to this session; no external notification service is connected.")

    render_html("<div style='height:16px'></div>")
    if st.button("Sign out", type="secondary", key="settings_sign_out"):
        logout()
        st.rerun()
