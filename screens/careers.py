import streamlit as st
from components.cards import progress_bar_card, icon_header, message_banner, section_header, panel
from components.badges import badge
from components.html import render_html
from services.session import current_app_data
from utils.state import go_to


def render():
    data = current_app_data()
    career_matches = data["career_matches"]
    section_header(
        "Career suggestions",
        "Role fit is calculated from your recorded skills and the bundled job-requirements snapshot. No live openings are shown.",
    )

    if not career_matches:
        message_banner(
            "Add skill levels to calculate role fit",
            "The app does not assume unreported skills are zero. Add proficiency levels in your profile to compare supported roles.",
            kind="info",
        )
        if st.button("Edit profile", key="careers-edit-profile"):
            go_to("profile")
            st.rerun()
        return

    right = st.container()
    with right:
        st.caption(f"Roles assessed: {len(career_matches)} · dataset rows are shown on each role card.")

    with st.container(key="equal-career-top"):
        cols = st.columns(3)
        for idx, (col, role) in enumerate(zip(cols, career_matches)):
            with col:
                skills_html = " ".join(f'<span class="ea-badge ea-badge-success">{s} ✓</span>' for s in role["skills_ok"])
                skills_html += " " + " ".join(f'<span class="ea-badge ea-badge-error">{s}</span>' for s in role["skills_gap"])
                if role["skills_not_provided"]:
                    skills_html += " " + " ".join(
                        f'<span class="ea-badge ea-badge-neutral">{s}: not provided</span>'
                        for s in role["skills_not_provided"]
                    )
                with panel(f"career-{idx}", kind="pcard"):
                    render_html(f"""
                    <span class="ea-badge ea-badge-neutral">{role['status']}</span>
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:6px;">
                        <div class="ea-section" style="font-size:20px;line-height:1.4;min-width:0;">{role['role']}</div>
                        <div class="ea-big-number" style="font-size:24px;color:#7C3AED;flex-shrink:0;">{role['match']}%</div>
                    </div>
                    <div style="margin-top:6px;">{skills_html}</div>
                    <div class="ea-small" style="margin-top:8px;">Dataset salary range <b>{role['salary']}</b></div>
                    <div class="ea-small">Benchmark evidence from {role['row_count']} verified industry job postings</div>
                    """)
                    b_c1, b_c2 = st.columns(2)
                    with b_c1:
                        if st.button("Compare Role", key=f"role-{role['role']}", width="stretch"):
                            st.session_state.profile["target_role"] = role["role"]
                            st.session_state["profile_target_role"] = role["role"]
                            go_to("skill_gap")
                            st.rerun()
                    with b_c2:
                        if st.button("View Jobs →", key=f"view-jobs-{role['role']}", width="stretch", type="primary"):
                            go_to("jobs")
                            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-career-bottom"):
        left, right = st.columns(2)
        with left:
            target_role = next(
                (item for item in career_matches if item["role"] == data["profile"]["target_role"]),
                career_matches[0],
            )
            with panel("career-fit", "skill_gap", "Recorded-skill match", target_role["role"]):
                progress_bar_card(
                    "Calculated fit",
                    target_role["match"],
                    right_label=f"{target_role['match']}%",
                )
                message_banner(
                    "How to read this",
                    "This percentage measures recorded skill levels against all requirements in the dataset snapshot. Skills not provided contribute no match evidence; it is not a hiring probability.",
                    kind="info",
                )
        with right:
            requirements = data["role_requirements"]
            with panel("career-asks", "assessment", "Compared requirements", f"Based on {data['skill_gap']['row_count']} bundled dataset rows"):
                if not requirements:
                    st.caption("No recorded profile skills are available for this role comparison.")
                for req in requirements:
                    kind = {"Met": "success", "Medium": "warning", "High": "error"}.get(req["status"], "neutral")
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f'{req["item"]}<br/><span class="ea-small">Asked for in {req["asked"]}</span>', unsafe_allow_html=True)
                    with c2:
                        badge(req["status"], kind)
