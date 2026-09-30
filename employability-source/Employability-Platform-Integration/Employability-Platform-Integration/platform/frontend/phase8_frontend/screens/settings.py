import streamlit as st
from components.cards import icon_header, section_header, panel
from services.session import current_app_data
from utils.state import logout


def render():
    profile = current_app_data()["profile"]
    section_header("Settings", "Account and notification preferences.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with panel("settings-account", "profile", "Account"):
        st.text_input("Email", value=profile.get("email") or "", disabled=True)
        st.text_input("Phone", value=profile.get("phone") or "", disabled=True)
        st.caption("Edit contact details in Profile. Account information is session-only.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with panel("settings-notifications", "bell", "Notifications"):
        st.checkbox("Weekly score summary email", key="setting_weekly_summary")
        st.checkbox("Reminders before an assessment opens", key="setting_assessment_reminders")
        st.checkbox("New job matches", key="setting_job_matches")
        st.caption("Notification preferences are local to this session; no email delivery is connected.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.button("Sign out", type="secondary", on_click=logout)
