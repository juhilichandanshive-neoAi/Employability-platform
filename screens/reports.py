from html import escape as html_escape

import streamlit as st

from components import charts
from components.cards import icon_header, message_banner, panel, progress_bar_card, section_header
from components.html import render_html
from components.icons import icon
from services.db import save_report_db
from services.reporting import generate_development_plan_pdf, generate_session_report
from services.session import current_app_data
from utils.state import go_to


def render():
    data = current_app_data()
    score = data["score"]
    assessment = data["analytics"]["latest_assessment"]
    history = data["analytics"]["attempt_history"]
    user_id = st.session_state.get("current_user_id")

    section_header(
        "Employability & Assessment Reports",
        "Executive summaries, competency breakdowns, and downloadable verified PDF reports.",
    )

    # Empty State Check
    if not assessment and score["overall"] is None:
        message_banner(
            "No assessment data available yet",
            "Complete your first domain assessment and save your profile to generate your personalized employability reports.",
            kind="info",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Take First Assessment →", type="primary", key="rep-go-assessment", width="stretch"):
                go_to("assessment")
                st.rerun()
        with c2:
            if st.button("Complete Profile →", key="rep-go-profile", width="stretch"):
                go_to("profile")
                st.rerun()
        return

    # Score comparison across attempts
    current_score = score["overall"] or (assessment["overall_pct"] if assessment else 0)
    prev_score = history[-2]["overall_pct"] if len(history) >= 2 else None
    score_delta = (current_score - prev_score) if prev_score is not None else 0

    render_html("<div style='height:12px;'></div>")

    # Metrics Summary Row
    with st.container(key="equal-reports-metrics"):
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            with panel("rep-metric-score", kind="pcard"):
                delta_html = (
                    f'<span style="color:#10B981;font-weight:700;font-size:13px;">+{score_delta}%</span>'
                    if score_delta > 0
                    else (
                        f'<span style="color:#EF4444;font-weight:700;font-size:13px;">{score_delta}%</span>'
                        if score_delta < 0
                        else '<span style="color:var(--color-text-secondary);font-size:12px;">Baseline</span>'
                    )
                )
                render_html(f"""
                <div class="ea-small">Employability Score</div>
                <div style="display:flex;align-items:baseline;gap:8px;margin-top:4px;">
                    <span class="ea-section" style="font-size:26px;">{current_score}%</span>
                    {delta_html}
                </div>
                <div class="ea-small" style="margin-top:2px;">Threshold: 80%</div>
                """)
        with m2:
            with panel("rep-metric-assessment", kind="pcard"):
                att_score = assessment["overall_pct"] if assessment else 0
                render_html(f"""
                <div class="ea-small">Latest Assessment</div>
                <div class="ea-section" style="font-size:26px;margin-top:4px;">{att_score}%</div>
                <div class="ea-small" style="margin-top:2px;">{len(history)} attempt{'s' if len(history) != 1 else ''} recorded</div>
                """)
        with m3:
            with panel("rep-metric-gaps", kind="pcard"):
                gap_data = data["skill_gap"]
                render_html(f"""
                <div class="ea-small">Measured Skill Gaps</div>
                <div class="ea-section" style="font-size:26px;margin-top:4px;">{len(gap_data.get('gaps', []))}</div>
                <div class="ea-small" style="margin-top:2px;">{gap_data.get('high_count', 0)} High Priority</div>
                """)
        with m4:
            with panel("rep-metric-fit", kind="pcard"):
                best_match = data["career_matches"][0] if data["career_matches"] else None
                fit_val = f"{best_match['match']}%" if best_match else "N/A"
                role_name = best_match["role"] if best_match else "Target Role"
                render_html(f"""
                <div class="ea-small">Top Role Fit</div>
                <div class="ea-section" style="font-size:26px;margin-top:4px;">{fit_val}</div>
                <div class="ea-small" style="margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{html_escape(role_name)}</div>
                """)

    render_html("<div style='height:20px;'></div>")

    # Detailed Reports Tabs
    tab_overview, tab_assessment, tab_skills, tab_roadmap, tab_downloads = st.tabs([
        "📊 Score & Benchmarks",
        "🎯 Domain Performance",
        "🔍 Skill Gap Analysis",
        "🚀 Action Plan",
        "📑 Generate & Download PDF",
    ])

    with tab_overview:
        c_left, c_right = st.columns([1.2, 1])
        with c_left:
            with panel("rep-breakdown-chart", "analytics", "Employability Score Components"):
                charts.bar(
                    [s["label"] for s in data["score_breakdown"]],
                    [s["value"] for s in data["score_breakdown"]],
                    warn_below=55,
                )
        with c_right:
            with panel("rep-drivers", "trend", "Key Score Drivers"):
                rows = ""
                for d in data["score_drivers"]:
                    pos = d["impact"] > 0
                    sign = "+" if pos else ""
                    width = min(abs(d["impact"]) * 8, 100)
                    cls = "pos" if pos else "neg"
                    rows += f"""
                    <div class="ea-driver {cls}">
                        <span class="ea-driver-label">{d['label']}</span>
                        <span class="ea-driver-track"><span class="ea-driver-fill" style="width:{width}%;"></span></span>
                        <span class="ea-driver-value">{sign}{d['impact']}</span>
                    </div>"""
                if rows:
                    render_html(f'<div class="ea-driver-list">{rows}</div>')
                else:
                    st.caption("All components currently balance evenly.")

    with tab_assessment:
        if assessment and assessment.get("categories"):
            c_cat1, c_cat2 = st.columns(2)
            with c_cat1:
                with panel("rep-assess-strengths", "trend", "Assessment Strengths (≥70%)"):
                    strengths = [c for c in assessment["categories"] if c["pct"] >= 70]
                    if strengths:
                        for s in strengths:
                            progress_bar_card(s["name"], s["pct"])
                    else:
                        st.caption("No categories cleared 70% yet in this attempt.")
            with c_cat2:
                with panel("rep-assess-weakness", "alert", "Areas for Revision (<70%)"):
                    weak = [c for c in assessment["categories"] if c["pct"] < 70]
                    if weak:
                        for w in weak:
                            progress_bar_card(w["name"], w["pct"])
                    else:
                        st.caption("All tested domains cleared 70% proficiency!")
        else:
            st.caption("No category breakdown available.")

    with tab_skills:
        gap_info = data["skill_gap"]
        with panel("rep-skills-table", "skill_gap", f"Role Skill Benchmarks ({gap_info.get('role', 'Target Role')})"):
            if gap_info.get("rows"):
                for r in gap_info["rows"]:
                    st.markdown(
                        f"**{r['skill']}** · Required: `{r['required']}` · Assessed: `{r['have']}` · Priority: **{r['priority']}**"
                    )
                    st.caption(f"Suggested Action: {r['action']}")
                    st.markdown("---")
            else:
                st.caption("Add more skills to your profile to generate detailed gap tables.")

    with tab_roadmap:
        tasks = data["roadmap"]["tasks"]
        with panel("rep-roadmap-steps", "roadmap", "Prescribed Learning Growth Steps"):
            if tasks:
                for idx, t in enumerate(tasks, start=1):
                    render_html(f"""
                    <div class="ea-card" style="margin-bottom:10px;padding:14px;border:1px solid #DDD6FE;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <b>Step {idx}: {html_escape(t['title'])}</b>
                            <span class="ea-badge ea-badge-purple">{html_escape(t['priority'])}</span>
                        </div>
                        <div class="ea-small" style="margin-top:4px;">{html_escape(t['reason'])}</div>
                    </div>
                    """)
            else:
                st.caption("No roadmap actions pending.")

    with tab_downloads:
        with panel("rep-generate-card", "reports", "Generate Official PDF Report"):
            st.markdown("Select sections to include in your verified EmployaAI PDF Report:")

            sec_cols = st.columns(3)
            with sec_cols[0]:
                inc_profile = st.checkbox("Profile & Education Summary", value=True, key="rep_inc_prof")
                inc_score = st.checkbox("Employability Score & Drivers", value=True, key="rep_inc_score")
            with sec_cols[1]:
                inc_gaps = st.checkbox("Industry Skill Gap Analysis", value=True, key="rep_inc_gaps")
                inc_assess = st.checkbox("Assessment Performance Breakdown", value=True, key="rep_inc_assess")
            with sec_cols[2]:
                inc_career = st.checkbox("Role Match & Certifications", value=True, key="rep_inc_career")
                inc_roadmap = st.checkbox("Learning Roadmap Actions", value=True, key="rep_inc_roadmap")

            selected_sections = set()
            if inc_profile:
                selected_sections.add("Profile summary")
            if inc_score:
                selected_sections.add("Employability score")
            if inc_gaps:
                selected_sections.add("Skill gap analysis")
            if inc_assess:
                selected_sections.add("Assessment details")
            if inc_career:
                selected_sections.add("Career recommendations")
                selected_sections.add("Certification recommendations")
            if inc_roadmap:
                selected_sections.add("Learning roadmap")

            render_html("<div style='height:12px;'></div>")

            # Generation action
            gen_col, dl_col = st.columns(2)
            with gen_col:
                if st.button("Generate Report", type="primary", width="stretch", key="generate-session-report"):
                    pdf_bytes, filename = generate_session_report(data, selected_sections)
                    st.session_state.current_report_pdf = pdf_bytes
                    st.session_state.current_report_filename = filename
                    st.session_state.generated_reports.append(
                        {
                            "name": filename,
                            "when": filename.removeprefix("employability-report-").rsplit(".", 1)[0],
                            "size_bytes": len(pdf_bytes),
                            "size": f"{len(pdf_bytes) / 1024:.1f} KB",
                            "score": score["overall"],
                        }
                    )
                    if user_id:
                        try:
                            save_report_db(
                                user_id,
                                filename,
                                score["overall"],
                                len(pdf_bytes),
                                list(selected_sections),
                            )
                        except Exception:
                            pass
                    st.success("New PDF Report compiled and ready for download.")
                    st.rerun()

            with dl_col:
                curr_pdf = st.session_state.get("current_report_pdf")
                curr_fname = st.session_state.get("current_report_filename")
                if curr_pdf and curr_fname:
                    st.download_button(
                        "Download Report",
                        data=curr_pdf,
                        file_name=curr_fname,
                        mime="application/pdf",
                        type="primary",
                        width="stretch",
                        key="dl-full",
                    )
                else:
                    st.caption("Click 'Generate Report' first to create your personalized document.")
