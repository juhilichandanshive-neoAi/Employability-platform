import streamlit as st
from html import escape as html_escape
from utils.state import NAV_ITEMS, LIVE_SCREENS, go_to
from components.html import render_html
from components.icons import icon
from services.session import current_app_data


def render_sidebar(current_page: str):
    student = current_app_data()["student"]
    with st.sidebar:
        render_html(
            '<div style="display:flex;align-items:center;gap:8px;padding:8px 4px 16px 4px;">'
            '<div style="width:28px;height:28px;border-radius:8px;background:#7C3AED;'
            'display:flex;align-items:center;justify-content:center;font-weight:700;color:#fff;">E</div>'
            '<span class="ea-sidebar-wordmark-text" style="font-weight:600;color:var(--color-sidebar-text-strong);">EmployAI</span>'
            '</div>'
        )

        # st.container(key=...) is the only reliable way to get a real
        # wrapping element around icon+button in Streamlit - raw <div> tags
        # opened/closed across separate st.markdown calls each land in
        # their own isolated container and never actually nest.
        st.markdown(
            f"<style>.st-key-nav-row-{current_page} {{ background: var(--color-sidebar-active-bg); "
            f"border-left-color: var(--color-primary) !important; "
            f"box-shadow: 0 4px 14px rgba(124, 58, 237, 0.25); }} "
            f".st-key-nav-row-{current_page} .stButton > button "
            f"{{ color: #FFFFFF !important; font-weight: 600 !important; }} "
            f".st-key-nav-row-{current_page} .ea-nav-icon "
            f"{{ background: rgba(255, 255, 255, 0.18); }}</style>",
            unsafe_allow_html=True,
        )

        for group_label, items in NAV_ITEMS:
            render_html(f'<div class="ea-nav-group-label">{group_label}</div>')
            for key, label, count in items:
                active = key == current_page
                icon_color = "#A78BFA" if active else "#8A82A6"
                with st.container(key=f"nav-row-{key}"):
                    render_html(f'<div class="ea-nav-icon">{icon(key, icon_color)}</div>')
                    display_label = f"{label}  ·  {count}" if count else label
                    if st.button(display_label, key=f"nav-{key}", width="stretch"):
                        go_to(key)
                        st.rerun()

        render_html('<div style="flex-grow:1;"></div>')
        render_html(
            f"""
            <div style="display:flex;align-items:center;gap:8px;margin-top:24px;padding:8px 4px;border-top:1px solid var(--color-sidebar-border);">
                <div style="width:32px;height:32px;border-radius:999px;background:#7C3AED;
                display:flex;align-items:center;justify-content:center;font-weight:600;color:#fff;font-size:13px;">{html_escape(student['initials'])}</div>
                <div class="ea-sidebar-footer-text">
                    <div style="font-size:13px;font-weight:600;color:var(--color-sidebar-text-strong);">{html_escape(student['name'] or 'Your profile')}</div>
                    <div style="font-size:12px;color:var(--color-sidebar-text-muted);">{html_escape(student['target_role'])} · {html_escape(student['semester'] or 'Semester not provided')}</div>
                </div>
            </div>
            """
        )


_ALL_MOBILE_BOTTOM_ITEMS = [
    ("dashboard", "Home"),
    ("score", "Score"),
    ("skill_gap", "Gaps"),
    ("roadmap", "Learn"),
    ("profile", "More"),
]
MOBILE_BOTTOM_ITEMS = [item for item in _ALL_MOBILE_BOTTOM_ITEMS if item[0] in LIVE_SCREENS]


def render_mobile_bottom_nav(current_page: str):
    with st.container(key="mobile-bottom-nav"):
        cols = st.columns(len(MOBILE_BOTTOM_ITEMS))
        for col, (key, label) in zip(cols, MOBILE_BOTTOM_ITEMS):
            with col:
                active = key == current_page
                color = "#7C3AED" if active else "#8A82A6"
                render_html(
                    f'<div style="text-align:center;color:{color};">{icon(key, color)}</div>'
                )
                if st.button(label, key=f"mnav-{key}", width="stretch"):
                    go_to(key)
                    st.rerun()
