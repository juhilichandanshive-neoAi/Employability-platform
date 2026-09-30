import streamlit as st
from html import escape as html_escape

from components.cards import icon_header, message_banner, panel, section_header
from services.session import current_app_data
from utils.state import go_to


def render():
    data = current_app_data()
    roadmap = data["roadmap"]
    section_header(
        f"Learning roadmap · {roadmap['role']}",
        "Ordered actions generated from measured profile gaps and your latest assessment. Time estimates and completion history are not available.",
    )

    tasks = roadmap["tasks"]
    if not tasks:
        message_banner(
            "No roadmap actions yet",
            "Add proficiency levels or complete an assessment. The roadmap will use only evidence recorded in this session.",
            kind="info",
        )
        left, right = st.columns(2)
        with left:
            if st.button("Edit profile", key="roadmap-to-profile", width="stretch"):
                go_to("profile")
                st.rerun()
        with right:
            if st.button("Take assessment", key="roadmap-to-assessment", width="stretch"):
                go_to("assessment")
                st.rerun()
        return

    gaps_count = sum(task["priority"] in ("High", "Medium") for task in tasks)
    assessment_count = sum(task["priority"] == "Assessment review" for task in tasks)
    with st.container(key="equal-roadmap-summary"):
        first, second, third = st.columns(3)
        with first:
            with panel("roadmap-count", kind="pcard"):
                st.markdown(f'<div class="ea-small">Generated actions</div><div class="ea-section">{len(tasks)}</div>', unsafe_allow_html=True)
        with second:
            with panel("roadmap-gap-count", kind="pcard"):
                st.markdown(f'<div class="ea-small">Measured skill gaps</div><div class="ea-section">{gaps_count}</div>', unsafe_allow_html=True)
        with third:
            with panel("roadmap-assessment-count", kind="pcard"):
                st.markdown(f'<div class="ea-small">Assessment review areas</div><div class="ea-section">{assessment_count}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with panel("roadmap-actions", "roadmap", "Recommended next steps", "Priority follows the measured gap; no completion is assumed"):
        for index, task in enumerate(tasks, start=1):
            st.markdown(
                f"""
                <div class="ea-card" style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">
                        <div>
                            <div class="ea-card-kicker">Step {index} · {task['priority']}</div>
                            <div class="ea-section" style="margin-top:4px;">{html_escape(task['title'])}</div>
                            <div class="ea-body" style="margin-top:4px;">{html_escape(task['reason'])}</div>
                            {f'<div class="ea-small" style="margin-top:6px;">Suggested certification: {html_escape(task["certification"])}</div>' if task.get("certification") else ''}
                        </div>
                        <span class="ea-badge ea-badge-neutral">Not started</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-roadmap-bottom"):
        left, right = st.columns(2)
        with left:
            with panel("roadmap-evidence", "assessment", "Why these actions appear"):
                st.markdown(
                    f'<div class="ea-small">Target role: {html_escape(roadmap["role"])}<br/>'
                    f'Job requirement evidence: {data["skill_gap"]["row_count"]} bundled dataset rows<br/>'
                    'Assessment actions, if shown, come from the latest completed question-bank assessment.</div>',
                    unsafe_allow_html=True,
                )
        with right:
            with panel("roadmap-limitations", "settings", "Plan limitations"):
                message_banner(
                    "No fixed schedule or projected score",
                    "The app does not estimate study duration, completion dates, or score increases for unfinished actions.",
                    kind="info",
                )

    _, download_col, _ = st.columns([1, 1, 1])
    with download_col:
        plan_lines = [
            f"Learning roadmap for {roadmap['role']}",
            f"Requirement evidence: {data['skill_gap']['row_count']} bundled dataset rows",
            "",
        ] + [
            f"{index}. {task['title']} — {task['reason']}"
            for index, task in enumerate(tasks, start=1)
        ]
        st.download_button(
            "Download plan",
            data="\n".join(plan_lines),
            file_name="learning-roadmap.txt",
            mime="text/plain",
            key="download-roadmap-session",
            width="stretch",
        )