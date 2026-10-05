"""Applicant Activity History Screen for EmployaAI."""

from __future__ import annotations

from datetime import datetime
from html import escape as html_escape

import streamlit as st

from components.cards import icon_header, message_banner, panel, section_header
from components.html import render_html
from components.icons import icon
from services.db import get_user_activities
from services.session import current_app_data


def _format_timestamp(iso_str: str) -> str:
    """Format an ISO timestamp into a user-friendly relative or calendar string."""
    try:
        # Normalize trailing Z
        if iso_str.endswith("Z"):
            iso_str = iso_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%b %d, %Y · %I:%M %p")
    except Exception:
        return iso_str


_TYPE_ICONS = {
    "login": "🔐",
    "logout": "🚪",
    "account_created": "🎉",
    "profile_updated": "👤",
    "education_added": "🎓",
    "education_updated": "✏️",
    "education_deleted": "🗑️",
    "assessment_completed": "🎯",
    "report_generated": "📑",
    "general": "📌",
}


def render():
    user_id = st.session_state.get("current_user_id")
    enrollment_id = st.session_state.get("current_enrollment_id") or "Enrolled Student"
    data = current_app_data()

    section_header(
        "Applicant Activity History",
        "Chronological audit trail of your profile changes, completed assessments, and platform milestones.",
    )

    activities = get_user_activities(user_id, limit=60) if user_id else []

    # Filter selector
    f_col1, f_col2, f_col3 = st.columns([1.5, 1, 1])
    with f_col1:
        filter_opt = st.selectbox(
            "Filter activities",
            [
                "All Activities",
                "Assessments",
                "Profile & Education",
                "Reports",
                "Logins",
            ],
            key="activity_filter",
        )

    # Filter logic
    filtered = activities
    if filter_opt == "Assessments":
        filtered = [a for a in activities if "assessment" in a["activity_type"]]
    elif filter_opt == "Profile & Education":
        filtered = [a for a in activities if any(k in a["activity_type"] for k in ("profile", "education", "skill", "cert"))]
    elif filter_opt == "Reports":
        filtered = [a for a in activities if "report" in a["activity_type"]]
    elif filter_opt == "Logins":
        filtered = [a for a in activities if a["activity_type"] in ("login", "logout", "account_created")]

    render_html("<div style='height:12px;'></div>")

    # Activity Summary Stats
    total_acts = len(activities)
    assessment_acts = sum(1 for a in activities if "assessment" in a["activity_type"])
    edu_acts = sum(1 for a in activities if "education" in a["activity_type"])

    with st.container(key="equal-activity-stats"):
        c1, c2, c3 = st.columns(3)
        with c1:
            with panel("stat-total-acts", kind="pcard"):
                render_html(f'<div class="ea-small">Total Tracked Actions</div><div class="ea-section" style="font-size:24px;">{total_acts}</div>')
        with c2:
            with panel("stat-assess-acts", kind="pcard"):
                render_html(f'<div class="ea-small">Assessment Events</div><div class="ea-section" style="font-size:24px;">{assessment_acts}</div>')
        with c3:
            with panel("stat-edu-acts", kind="pcard"):
                render_html(f'<div class="ea-small">Academic Records Tracked</div><div class="ea-section" style="font-size:24px;">{edu_acts}</div>')

    render_html("<div style='height:16px;'></div>")

    if not filtered:
        message_banner(
            "No activity recorded yet",
            "Your activities will automatically be logged as you update your profile, add academic records, take assessments, or download reports.",
            kind="info",
        )
        return

    # Timeline view
    with panel("activity-timeline", "analytics", f"Activity Log ({len(filtered)} items shown)"):
        for item in filtered:
            act_type = item.get("activity_type", "general")
            emoji = _TYPE_ICONS.get(act_type, "📌")
            time_str = _format_timestamp(item.get("timestamp", ""))

            render_html(f"""
            <div class="ea-card" style="margin-bottom:12px;padding:16px;border-left:4px solid var(--color-primary);border-radius:12px;background:#FFFFFF;box-shadow:0 2px 8px rgba(124, 58, 237, 0.04);">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
                    <div style="display:flex;gap:12px;align-items:center;">
                        <span style="font-size:22px;">{emoji}</span>
                        <div>
                            <div style="font-size:15px;font-weight:700;color:var(--color-text-primary);">{html_escape(item.get('title', 'Action'))}</div>
                            <div style="font-size:13.5px;color:var(--color-text-secondary);margin-top:2px;">{html_escape(item.get('description', ''))}</div>
                        </div>
                    </div>
                    <span class="ea-badge ea-badge-neutral" style="font-size:12px;font-weight:600;">{html_escape(time_str)}</span>
                </div>
            </div>
            """)
