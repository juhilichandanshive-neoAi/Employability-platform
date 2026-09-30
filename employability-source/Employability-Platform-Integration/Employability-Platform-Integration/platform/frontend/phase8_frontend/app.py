import os
import sys

import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)
BACKEND_SOURCE = os.path.abspath(
    os.path.join(APP_DIR, "..", "..", "backend", "NeoAI1stPipeline", "src")
)
if BACKEND_SOURCE not in sys.path:
    sys.path.insert(0, BACKEND_SOURCE)

from utils.state import init_state
from components.navigation import render_sidebar, render_mobile_bottom_nav
from screens import (
    dashboard, assessment, score, skill_gap,
    certifications, careers, analytics, reports, settings,
)
from screens import login_session, profile_session, roadmap_session

st.set_page_config(page_title="EmployaAI", page_icon=":material/school:", layout="wide", initial_sidebar_state="expanded")

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
    "analytics": analytics.render,
    "reports": reports.render,
    "settings": settings.render,
}

SCREENS[page]()

render_mobile_bottom_nav(page)
