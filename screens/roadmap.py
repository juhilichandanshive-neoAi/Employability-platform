"""[LEGACY / UNUSED]
This module is a static prototype implementation of the learning roadmap using fixed dummy data.
The canonical live application uses `screens.roadmap_session` which generates a dynamic,
evidence-based learning roadmap from current profile skills and assessment results.
Preserved for backwards compatibility; do not use in the live routing pipeline.
"""

import streamlit as st
from components.cards import progress_bar_card, icon_header, section_header, panel
from components.icons import icon
from data.dummy_data import SCORE, PROJECTED_SCORE, ROADMAP_TOTAL_WEEKS, ROADMAP_CURRENT_WEEK, ROADMAP_PROGRESS_PCT, ROADMAP_PHASES, ROADMAP_TIMELINE, THIS_WEEK, RECOMMENDATIONS


def render():
    right = section_header("Your 12-week roadmap", "Six hours a week, in the order that actually makes sense to learn things.", with_right_col=True)
    with right:
        with st.container(key="roadmap-header-actions"):
            st.markdown('<div class="ea-small" style="text-align:right;">Projected score</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ea-section" style="text-align:right;color:var(--color-primary);">{SCORE["overall"]} → {PROJECTED_SCORE}</div>', unsafe_allow_html=True)

    progress_bar_card("Overall progress", ROADMAP_PROGRESS_PCT, right_label=f"Week {ROADMAP_CURRENT_WEEK} of {ROADMAP_TOTAL_WEEKS} · {ROADMAP_PROGRESS_PCT}% done")

    with st.container(key="equal-roadmap-phases"):
        cols = st.columns(3)
        for i, (col, phase) in enumerate(zip(cols, ROADMAP_PHASES), start=1):
            with col:
                active = phase["status"] == "In progress"
                if active:
                    dot_class, dot_content = "current", str(i)
                elif phase["progress"] >= 100:
                    dot_class, dot_content = "done", "✓"
                else:
                    dot_class, dot_content = "pending", str(i)
                with panel(f"roadmap-phase-{i}", kind="pcard"):
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <div class="ea-step-dot {dot_class}">{dot_content}</div>
                            <div class="ea-small">{phase['weeks']}</div>
                        </div>
                        <span class="ea-badge {'ea-badge-purple' if active else 'ea-badge-neutral'}">{phase['status']}</span>
                    </div>
                    <div class="ea-section" style="margin-top:8px;">{phase['title']}</div>
                    <div class="ea-body" style="color:#6B6478;margin-top:4px;font-size:14px;">{phase['desc']}</div>
                    """, unsafe_allow_html=True)
                    progress_bar_card("", phase["progress"], right_label=f"{phase['progress']}%")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with panel("roadmap-timeline", "roadmap", "Your twelve weeks", "Nothing starts before the skill it builds on is done"):
        total_weeks = 12
        for track in ROADMAP_TIMELINE:
            color = {"done": "var(--color-primary-dark)", "now": "var(--color-primary)", "upcoming": "#E5E1F0"}[track["status"]]
            left_pct = (track["start_week"] - 1) / total_weeks * 100
            width_pct = (track["end_week"] - track["start_week"]) / total_weeks * 100
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <div style="width:140px;font-size:13px;">{track['track']}</div>
                <div style="flex:1;background:#F1EFF7;border-radius:6px;height:14px;position:relative;">
                    <div style="position:absolute;left:{left_pct}%;width:{width_pct}%;background:{color};height:100%;border-radius:6px;"></div>
                </div>
                <div style="width:70px;font-size:12px;color:#6B6478;">W{track['start_week']}-{track['end_week']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-roadmap-bottom"):
        left, right = st.columns(2)
        with left:
            with panel("roadmap-week", "assessment", "What you are on this week"):
                for item in THIS_WEEK:
                    if item["status"] == "done":
                        st.markdown(
                            f'<div style="display:flex;gap:8px;align-items:center;">'
                            f'<span style="color:var(--color-primary);">{icon("check-circle")}</span>{item["title"]}</div>',
                            unsafe_allow_html=True,
                        )
                    elif item["status"] == "active":
                        st.markdown(f"""
                        <div style="border:1px solid var(--color-primary);border-radius:var(--radius);padding:14px 16px;">
                            <b>{item['title']}</b><br/><span class="ea-small">{item['meta']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.button("Resume lesson", type="primary", key="resume_lesson")
                    else:
                        st.markdown(f'<div style="color:#8A82A6;">{item["title"]}</div>', unsafe_allow_html=True)
        with right:
            with panel("roadmap-courses", "book", "Courses that would help"):
                for c in RECOMMENDATIONS:
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div><b>{c['title']}</b><br/><span class="ea-small">{c['meta']}</span></div>
                        <span class="ea-badge ea-badge-purple">{c['tag']}</span>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    _, download_col, _ = st.columns([1, 1, 1])
    with download_col:
        st.button("Download plan", type="primary", key="download-plan-bottom", width="stretch")
