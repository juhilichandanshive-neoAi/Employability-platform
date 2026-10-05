import os
import sys

import streamlit as st

from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from utils.state import init_state
from components.navigation import render_sidebar, render_mobile_bottom_nav
from screens import (
    dashboard, assessment, score, skill_gap,
    certifications, careers, jobs, analytics, reports, settings, activity,
)
from screens import login_session, profile_session, roadmap_session

st.set_page_config(page_title="EmployAI", page_icon=":material/school:", layout="wide", initial_sidebar_state="expanded")

with open(os.path.join(APP_DIR, "assets", "styles.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_state()

if not st.session_state.authenticated:
    login_session.render()
    st.stop()

page = st.session_state.page
render_sidebar(page)

SCREENS = {
    "dashboard": dashboard.render,
    "profile": profile_session.render,
    "assessment": assessment.render,
    "score": score.render,
    "skill_gap": skill_gap.render,
    "roadmap": roadmap_session.render,
    "certifications": certifications.render,
    "careers": careers.render,
    "jobs": jobs.render,
    "analytics": analytics.render,
    "activity": activity.render,
    "reports": reports.render,
    "settings": settings.render,
}

from components.footer import render_footer

if page in SCREENS:
    SCREENS[page]()
else:
    SCREENS["dashboard"]()
render_footer("app")

render_mobile_bottom_nav(page)
