from html import escape as html_escape

import streamlit as st

from components import charts
from components.cards import icon_header, panel, progress_bar_card, progress_label, score_hero_card, section_header
from components.fun import mascot
from components.html import render_html
from components.icons import icon
from services.db import get_user_activities
from services.session import current_app_data
from utils.state import go_to


def render():
    data = current_app_data()
    student = data["student"]
    score = data["score"]
    assessment = data["analytics"]["latest_assessment"]
    attempt_history = data["analytics"]["attempt_history"]
    user_id = st.session_state.get("current_user_id")
    enrollment_id = (
        st.session_state.get("current_enrollment_id")
        or student.get("enrolment_id")
        or "EA-2026-PENDING"
    )

    greet_col, mascot_col = st.columns([4.5, 1], vertical_alignment="center")
    with greet_col:
        full_name = student.get("name", "").strip()
        first_name = full_name.split()[0] if full_name else "Student"
        heading = f"Welcome back, {first_name}"
        subheading = (
            f"Your latest verified assessment score is {assessment['overall_pct']}%. "
            "Track your competency progress, skill gaps, and learning milestones below."
            if assessment
            else "Complete your student profile and take your first assessment to unlock your Employability Score."
        )
        section_header(heading, subheading)
    with mascot_col:
        mascot(size=56)

    # Enrollment ID & Quick Metrics Strip
    render_html(f"""
    <div class="ea-card" style="margin-bottom:18px;padding:14px 20px;background:linear-gradient(135deg, rgba(245,243,255,0.9) 0%, rgba(237,233,254,0.95) 100%);border:1px solid #DDD6FE;border-radius:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <span class="ea-badge ea-badge-purple" style="font-family:monospace;font-size:13px;font-weight:700;letter-spacing:0.04em;">
                    🆔 Enrollment ID: {html_escape(enrollment_id)}
                </span>
                <span class="ea-badge ea-badge-neutral" style="font-size:12.5px;font-weight:600;">
                    🎯 Target: {html_escape(student.get('target_role', 'Cloud Solutions Architect'))}
                </span>
            </div>
            <div class="ea-small" style="color:var(--color-primary-dark);font-weight:600;">
                Active Session · Verified Student
            </div>
        </div>
    </div>
    """)

    # Quick Action Navigation Tiles
    with st.container(key="equal-dashboard-quick-actions"):
        actions = [
            ("Profile", "Academic records & skills", "profile", "profile"),
            ("Assessment", "Take domain assessment", "assessment", "assessment"),
            ("Skill Gaps", "260+ job requirements", "skill_gap", "skill_gap"),
            ("Learning Plan", "Step-by-step milestones", "roadmap", "roadmap"),
            ("Reports", "Verified PDF generation", "reports", "reports"),
        ]
        qa_cols = st.columns(len(actions))
        for col, (label, hint, icon_name, page) in zip(qa_cols, actions):
            with col:
                render_html(f"""
                <div class="ea-card ea-tile ea-action-tile" style="height:120px;display:flex;flex-direction:column;justify-content:space-between;margin-bottom:8px;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div class="ea-icon-badge" style="flex-shrink:0;">{icon(icon_name, 'var(--color-primary)')}</div>
                        <div class="ea-tile-text">
                            <div class="ea-tile-title">{label}</div>
                            <div class="ea-tile-sub" style="font-size:11.5px;margin-top:2px;">{hint}</div>
                        </div>
                    </div>
                    <div style="display:flex;justify-content:flex-end;">
                        <span class="ea-tile-chevron">{icon('chevron-right', 'var(--color-text-secondary)', size=14)}</span>
                    </div>
                </div>
                """)
                if st.button(f"Open {label}", key=f"dashboard-open-{page}", width="stretch"):
                    go_to(page)
                    st.rerun()

    render_html("<div style='height:16px'></div>")

    # Score, Profile Progress, and Action Target Row
    with st.container(key="equal-dashboard-score-row"):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if score["overall"] is None:
                with panel("dashboard-score-not-ready", "analytics", "Employability Score", kind="pcard"):
                    render_html("""
                    <div style="text-align:center;padding:12px 0;">
                        <div class="ea-big-number" style="font-size:28px;color:var(--color-text-secondary);">Not Calculated</div>
                        <div class="ea-small" style="margin-top:8px;">Take an assessment and save your profile to generate your score.</div>
                    </div>
                    """)
                    if st.button("Start Assessment →", key="dash-start-score", type="primary", width="stretch"):
                        go_to("assessment")
                        st.rerun()
            else:
                score_hero_card(
                    score["overall"],
                    score["band"],
                    "Deterministic score from verified evidence",
                    data["points_to_ready"],
                )
        with c2:
            completed_steps = sum(item["status"] == "done" for item in data["profile_steps"])
            with panel("dashboard-profile-status", "profile", "Profile Progress", kind="pcard"):
                render_html(f"""
                <div style="text-align:center;padding:4px 0;">
                    <div class="ea-big-number" style="font-size:32px;">{data['profile_completion']}%</div>
                    <div class="ea-small" style="color:var(--color-fun-teal-text);font-weight:700;">{progress_label(data['profile_completion'])}</div>
                    <div class="ea-progress-track" style="margin:8px 0;"><div class="ea-progress-fill" style="width:{data['profile_completion']}%;"></div></div>
                    <div class="ea-small" style="margin-top:6px;">{completed_steps} of {len(data['profile_steps'])} profile milestones completed.</div>
                </div>
                """)
                if st.button("Update Profile", key="dash-up-profile", width="stretch"):
                    go_to("profile")
                    st.rerun()
        with c3:
            with st.container(key="dashboard-goal-card"):
                tasks = data["roadmap"]["tasks"]
                if not data["skills"]:
                    goal_title = "Add Skills & Proficiency"
                    goal_hint = "Record your programming languages, tools, and platforms in your profile."
                    btn_target = "profile"
                elif not assessment:
                    goal_title = "Complete Skill Assessment"
                    goal_hint = "Take a 15-question domain test to evaluate your technical competencies."
                    btn_target = "assessment"
                elif tasks:
                    goal_title = tasks[0]["title"]
                    goal_hint = tasks[0]["reason"]
                    btn_target = "roadmap"
                else:
                    goal_title = "Explore Career Matches"
                    goal_hint = "Review industry roles aligned with your verified competencies."
                    btn_target = "careers"

                render_html(f"""
                <div style="display:flex;flex-direction:column;justify-content:space-between;height:100%;">
                    <div>
                        <div class="ea-card-kicker" style="display:flex;align-items:center;gap:5px;">
                            <span style="color:var(--color-primary);">{icon('zap', size=13)}</span>Recommended Next Action
                        </div>
                        <div class="ea-body" style="font-weight:700;margin-top:8px;font-size:16px;">{html_escape(goal_title)}</div>
                        <div class="ea-small" style="margin-top:6px;line-height:1.4;">{html_escape(goal_hint)}</div>
                    </div>
                </div>
                """)
                if st.button("Take Action →", type="primary", key="goal-view-path", width="stretch"):
                    go_to(btn_target)
                    st.rerun()

    render_html("<div style='height:24px'></div>")

    # Assessment History & Skill Proficiency Row
    with st.container(key="equal-dashboard-charts"):
        left, right = st.columns([1.3, 1])
        with left:
            with panel("score-over-time", "analytics", "Assessment History", "Scores from completed attempts"):
                if attempt_history:
                    charts.line(
                        [item["when"] for item in attempt_history],
                        [item["overall_pct"] for item in attempt_history],
                    )
                else:
                    render_html("""
                    <div style="text-align:center;padding:24px 0;">
                        <div class="ea-small" style="margin-bottom:12px;">No assessment attempts on record yet.</div>
                    </div>
                    """)
                    if st.button("Take First Assessment", key="dash-take-first-assess", type="primary"):
                        go_to("assessment")
                        st.rerun()
        with right:
            with panel("skill-overview", "skill_gap", "Recorded Skill Levels", "Proficiency on 0–5 scale"):
                if data["skills"]:
                    for skill in data["skills"][:5]:
                        level = max(0, min(5, float(skill.get("level", 0))))
                        progress_bar_card(skill["name"], round(level / 5 * 100), right_label=f"{level:g}/5")
                else:
                    st.caption("No skills recorded yet. Add them in your Profile.")

    render_html("<div style='height:24px'></div>")

    # Career Fit & Recent Activity Row
    with st.container(key="equal-dashboard-activity"):
        left, right = st.columns([1.3, 1])
        with left:
            with panel("job-match", "careers", "Role Fit from Recorded Skills", "Compared against 260+ industry benchmark job requirements"):
                if data["career_matches"]:
                    for role in data["career_matches"][:4]:
                        progress_bar_card(
                            role["role"],
                            role["match"],
                            right_label=f"{role['match']}% fit",
                        )
                else:
                    st.caption("Add technical skills to calculate your job role matches.")
        with right:
            with panel("recent-activity", "bell", "Recent Activity", "Chronological applicant actions"):
                recent_acts = get_user_activities(user_id, limit=4) if user_id else []
                if recent_acts:
                    for act in recent_acts:
                        render_html(f"""
                        <div style="margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid var(--color-border);">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <b style="font-size:13.5px;">{html_escape(act['title'])}</b>
                                <span class="ea-small" style="font-size:11px;">{html_escape(act['timestamp'][:10])}</span>
                            </div>
                            <div class="ea-small" style="color:var(--color-text-secondary);margin-top:2px;">{html_escape(act['description'])}</div>
                        </div>
                        """)
                elif attempt_history:
                    for item in reversed(attempt_history[-3:]):
                        render_html(f"""
                        <div style="margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid var(--color-border);">
                            <b>{html_escape(item['name'])}</b>: {html_escape(str(item['score']))}<br/>
                            <span class="ea-small">{html_escape(str(item['when']))}</span>
                        </div>
                        """)
                else:
                    st.caption("No recent activity recorded yet.")

                if st.button("View Full Activity Log →", key="dash-view-full-activity", width="stretch"):
                    go_to("activity")
                    st.rerun()

    render_html("<div style='height:16px'></div>")

    # Recommended Job Opportunities Row
    with panel("dash-job-opps", "briefcase", "Recommended Job Opportunities", "Verified industry openings from admin dataset"):
        from services.job_service import load_admin_jobs, calculate_job_match
        all_jobs_dash = load_admin_jobs()
        if all_jobs_dash:
            profile = data.get("profile") or st.session_state.get("profile", {})
            job_matches = []
            for j in all_jobs_dash:
                m = calculate_job_match(j, profile)
                job_matches.append((j, m.get("score") or 0))
            job_matches.sort(key=lambda x: x[1], reverse=True)
            top_jobs = job_matches[:3]
            jc1, jc2, jc3 = st.columns(3)
            for idx, (col, (job, match_pct)) in enumerate(zip([jc1, jc2, jc3], top_jobs)):
                with col:
                    pill_html = f"<span style='background:#ECFDF5;color:#059669;padding:2px 7px;border-radius:10px;font-size:11px;font-weight:700;'>{match_pct}% Match</span>" if match_pct > 0 else ""
                    render_html(f"""
                    <div class="ea-card" style="padding:12px;background:#FFF;border:1px solid #E2E8F0;border-radius:10px;display:flex;flex-direction:column;justify-content:space-between;min-height:90px;">
                        <div>
                            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                                <b style="font-size:13.5px;color:var(--color-text);">{html_escape(job['title'])}</b>
                                {pill_html}
                            </div>
                            <div class="ea-small" style="color:var(--color-primary);font-weight:600;margin-top:2px;">{html_escape(job['company'])}</div>
                            <div class="ea-small" style="color:var(--color-text-muted);margin-top:4px;">{html_escape(job['experience'])} · {html_escape(job['salary_display'])}</div>
                        </div>
                    </div>
                    """)
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("View All 260+ Verified Job Opportunities →", key="dash-btn-view-all-jobs", width="stretch"):
                go_to("jobs")
                st.rerun()

    render_html("<div style='height:24px'></div>")
    with st.container(key="dashboard-cta"):
        text_col, btn_col = st.columns([3, 1], vertical_alignment="center")
        with text_col:
            if assessment:
                progress_text = f"Latest assessment completed · {assessment['overall_pct']}% score."
            else:
                progress_text = "Ready to test your knowledge? Take an assessment today."
            render_html(
                '<div class="ea-section" style="color:#fff;">Ready to evaluate your readiness?</div>'
                f'<div class="ea-small" style="color:rgba(255,255,255,0.85);">{html_escape(progress_text)}</div>'
            )
        with btn_col:
            if st.button("Open Assessment →", type="primary", key="continue-assessment-bottom", width="stretch"):
                go_to("assessment")
                st.rerun()
