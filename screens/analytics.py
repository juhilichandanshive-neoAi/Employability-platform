import streamlit as st
from components import charts
from components.cards import progress_bar_card, icon_header, message_banner, section_header, panel
from components.html import render_html
from services.session import current_app_data


def render():
    data = current_app_data()
    analytics = data["analytics"]
    attempts = analytics["attempt_history"]
    latest = analytics["latest_assessment"]
    score_value = data["score"]["overall"]
    section_header(
        "Analytics",
        "Current-session assessment results and profile evidence only. Historical practice time and cohort data are not available.",
    )

    summary = [
        {"label": "Assessments completed", "value": str(analytics["assessment_count"])},
        {"label": "Latest assessment", "value": f"{latest['overall_pct']}%" if latest else "—"},
        {"label": "Employability score", "value": f"{score_value}/100" if score_value is not None else "Not calculated"},
        {"label": "Reports generated", "value": str(len(data["reports"]))},
    ]
    with st.container(key="cards-analytics-summary"):
        for col, item in zip(st.columns(4), summary):
            with col:
                render_html(f"""
                <div class="ea-card ea-tile ea-stat-tile">
                    <div class="ea-small">{item['label']}</div>
                    <div class="ea-big-number" style="font-size:28px;">{item['value']}</div>
                </div>
                """)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-analytics-charts"):
        left, right = st.columns(2)
        with left:
            with panel("analytics-score", "trend", "Assessment results in this session", "No historical or cohort values are added"):
                if attempts:
                    charts.line(
                        [item["when"] for item in attempts],
                        [item["overall_pct"] for item in attempts],
                    )
                else:
                    st.caption("No assessment results have been recorded in this session.")
        with right:
            with panel("analytics-sections", "analytics", "Latest assessment by category", "Percent correct in the most recent completed attempt"):
                if latest and latest["categories"]:
                    charts.bar(
                        [item["name"] for item in latest["categories"]],
                        [item["pct"] for item in latest["categories"]],
                        warn_below=55,
                    )
                else:
                    st.caption("Complete an assessment to see category results.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-analytics-lower"):
        left, right = st.columns([1, 1.4])
        with left:
            with panel("analytics-practice", "score", "Practice activity", "Tracked data only"):
                message_banner(
                    "Practice time is not tracked",
                    "The current application does not record hours, study sessions, or practice history.",
                    kind="info",
                )
        with right:
            with panel("analytics-attempts", "reports", "Assessment attempts", "Completed in this session, newest first"):
                if attempts:
                    rev_attempts = list(reversed(attempts))
                    for item in rev_attempts[:5]:
                        badge_cls = "ea-badge-success" if item["kind"] == "success" else "ea-badge-warning"
                        render_html(f"""
                        <div class="ea-attempt-row">
                            <div><b>{item['name']}</b><br/><span class="ea-small">{item['when']}</span></div>
                            <span class="ea-badge {badge_cls}">{item['score']}</span>
                        </div>
                        """)
                    if len(rev_attempts) > 5:
                        with st.expander(f"View all ({len(rev_attempts)}) attempts"):
                            for item in rev_attempts[5:]:
                                badge_cls = "ea-badge-success" if item["kind"] == "success" else "ea-badge-warning"
                                render_html(f"""
                                <div class="ea-attempt-row">
                                    <div><b>{item['name']}</b><br/><span class="ea-small">{item['when']}</span></div>
                                    <span class="ea-badge {badge_cls}">{item['score']}</span>
                                </div>
                                """)
                else:
                    st.caption("No completed assessment attempts are available.")

