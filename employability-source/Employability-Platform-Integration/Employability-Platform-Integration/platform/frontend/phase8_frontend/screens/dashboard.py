import streamlit as st
from components import charts
from components.cards import score_hero_card, progress_bar_card, progress_label, icon_header, section_header, panel
from components.icons import icon
from utils.state import go_to
from components.fun import mascot
from services.session import current_app_data


def render():
    data = current_app_data()
    student = data["student"]
    score = data["score"]
    assessment = data["analytics"]["latest_assessment"]
    attempt_history = data["analytics"]["attempt_history"]

    greet_col, mascot_col = st.columns([5, 1], vertical_alignment="center")
    with greet_col:
        first_name = student["name"].split()[0] if student["name"].strip() else ""
        heading = f"Welcome, {first_name}." if first_name else "Your employability dashboard"
        subheading = (
            f"Your latest assessment result is {assessment['overall_pct']}%. "
            "Other insights below use your saved profile and the bundled dataset snapshot."
            if assessment
            else "Save your profile and complete an assessment to calculate your score. "
            "No historical activity is carried into this session."
        )
        section_header(
            heading,
            subheading,
        )
    with mascot_col:
        mascot(size=56)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="dashboard-quick-actions"):
        actions = [
            ("Profile", "Edit details and skills", "profile", "profile"),
            ("Assessment", "Take a question-bank assessment", "assessment", "assessment"),
            ("Skill gaps", "Compare recorded skills to the dataset", "skill_gap", "skill_gap"),
            ("Learning plan", "Review evidence-based next steps", "roadmap", "roadmap"),
        ]
        qa_cols = st.columns(len(actions))
        for col, (label, hint, icon_name, page) in zip(qa_cols, actions):
            with col:
                st.markdown(f"""
                <div class="ea-card ea-tile ea-action-tile">
                    <div class="ea-icon-badge">{icon(icon_name, 'var(--color-primary)')}</div>
                    <div class="ea-tile-row">
                        <div class="ea-tile-text">
                            <div class="ea-tile-title">{label}</div>
                            <div class="ea-tile-sub">{hint}</div>
                        </div>
                        <span class="ea-tile-chevron">{icon('chevron-right', 'var(--color-text-secondary)', size=16)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Open {label}", key=f"dashboard-open-{page}", width="stretch"):
                    go_to(page)
                    st.rerun()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    icon_header("certifications", "Profile evidence")
    evidence = (
        [item.get("name", "Certification") for item in data["certifications_held"]]
        + [item.get("title", "Project") for item in data["projects"]]
    )
    if evidence:
        for item in evidence:
            st.markdown(f'<span class="ea-badge ea-badge-purple" style="margin:3px;">{item}</span>', unsafe_allow_html=True)
    else:
        st.caption("No projects or certifications have been added to this profile yet.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="dashboard-score-row"):
        c1, c2, c3 = st.columns([1.1, 1, 1])
        with c1:
            if score["overall"] is None:
                with panel("dashboard-score-not-ready", "analytics", "Employability score", kind="pcard"):
                    st.markdown('<div class="ea-big-number">Not calculated</div>', unsafe_allow_html=True)
                    st.caption("A saved profile and completed assessment are required.")
            else:
                score_hero_card(
                    score["overall"],
                    score["band"],
                    "No cohort comparison available",
                    data["points_to_ready"],
                )
        with c2:
            completed_steps = sum(item["status"] == "done" for item in data["profile_steps"])
            st.markdown(f"""
            <div class="ea-card">
                <div class="ea-card-kicker">Your profile</div>
                <div class="ea-big-number">{data['profile_completion']}%</div>
                <div class="ea-small" style="color:var(--color-fun-teal-text);font-weight:700;">{progress_label(data['profile_completion'])}</div>
                <div class="ea-small" style="margin-top:8px;">{completed_steps} of {len(data['profile_steps'])} profile and assessment sections have recorded data.</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            with st.container(key="dashboard-goal-card"):
                next_task = data["roadmap"]["tasks"][0] if data["roadmap"]["tasks"] else None
                goal_title = next_task["title"] if next_task else "Add a skill level or complete an assessment"
                goal_hint = next_task["reason"] if next_task else "Next steps appear from recorded profile and assessment evidence."
                st.markdown(f"""
                <div>
                    <div class="ea-card-kicker" style="display:flex;align-items:center;gap:5px;">
                        <span style="color:var(--color-primary);">{icon('zap', size=13)}</span>Today's goal
                    </div>
                    <div class="ea-body" style="font-weight:600;margin-top:6px;">{goal_title}</div>
                    <div class="ea-small" style="margin-top:4px;">{goal_hint}</div>
                    <div class="ea-small" style="margin-top:14px;">Task completion is not tracked in this session.</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View learning path", type="primary", key="goal-view-path", width="stretch"):
                    go_to("roadmap")
                    st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-dashboard-charts"):
        left, right = st.columns([1.4, 1])
        with left:
            with panel("score-over-time", "analytics", "Assessment results in this session", "No cohort or historical data is included"):
                if attempt_history:
                    charts.line(
                        [item["when"] for item in attempt_history],
                        [item["overall_pct"] for item in attempt_history],
                        [],
                        [],
                    )
                else:
                    st.caption("Complete an assessment to add the first result.")
        with right:
            with panel("skill-overview", "skill_gap", "Recorded skill levels", "Self-reported proficiency on the 0–5 profile scale"):
                if data["skills"]:
                    for skill in data["skills"]:
                        level = max(0, min(5, float(skill.get("level", 0))))
                        progress_bar_card(skill["name"], round(level / 5 * 100), right_label=f"{level:g}/5")
                else:
                    st.caption("Add skills and proficiency levels in your profile.")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-dashboard-activity"):
        left, right = st.columns([1.4, 1])
        with left:
            with panel("job-match", "careers", "Role fit from recorded skills", "Compared with requirements in the bundled dataset snapshot"):
                if data["career_matches"]:
                    for role in data["career_matches"]:
                        progress_bar_card(
                            role["role"],
                            role["match"],
                            right_label=f"{role['match']}% calculated fit",
                        )
                else:
                    st.caption("Add skill levels to calculate role fit.")
        with right:
            with panel("recent-activity", "bell", "Assessment activity", "Completed attempts from this session only"):
                if attempt_history:
                    for item in reversed(attempt_history):
                        st.markdown(
                            f'<div class="ea-body" style="margin-bottom:4px;">{item["name"]}: '
                            f'{item["score"]}<br/><span class="ea-small">{item["when"]}</span></div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("No assessment activity recorded yet.")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    with st.container(key="dashboard-cta"):
        text_col, btn_col = st.columns([3, 1], vertical_alignment="center")
        with text_col:
            if st.session_state.get("assessment_started") and not st.session_state.get("assessment_submitted"):
                progress_text = (
                    f"Assessment in progress · question "
                    f"{st.session_state.get('assessment_current_q', 0) + 1}."
                )
            elif assessment:
                progress_text = f"Latest assessment completed · {assessment['overall_pct']}%."
            else:
                progress_text = "No assessment has been completed in this session."
            st.markdown(
                '<div class="ea-section" style="color:#fff;">Continue your assessment</div>'
                f'<div class="ea-small">{progress_text}</div>',
                unsafe_allow_html=True,
            )
        with btn_col:
            if st.button("Open assessment →", type="primary", key="continue-assessment-bottom", width="stretch"):
                go_to("assessment")
                st.rerun()
