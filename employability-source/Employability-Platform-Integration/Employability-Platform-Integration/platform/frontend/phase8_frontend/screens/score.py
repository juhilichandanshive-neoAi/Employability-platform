import streamlit as st
from components import charts
from components.cards import score_hero_card, icon_header, section_header, panel, message_banner
from services.session import current_app_data, refresh_app_data
from utils.state import go_to


def render():
    data = current_app_data()
    score = data["score"]
    right = section_header(
        "Employability Score",
        "A deterministic indicator calculated from your saved profile, latest assessment, and configured weights.",
        with_right_col=True,
    )
    with right:
        if st.button("Recalculate", width="stretch"):
            refresh_app_data()
            st.rerun()

    if score["overall"] is None:
        message_banner(
            "Score not calculated",
            "Save profile information and complete an assessment in this session. Cohort comparisons and historical changes are not available.",
            kind="info",
        )
        first, second = st.columns(2)
        with first:
            if st.button("Complete profile", key="score-go-profile", width="stretch"):
                go_to("profile")
                st.rerun()
        with second:
            if st.button("Take assessment", key="score-go-assessment", width="stretch"):
                go_to("assessment")
                st.rerun()
        return

    # "Why you got this score" used to sit stacked in the right column
    # together with the bar chart below it, while the left column (hero
    # card + stats) is much shorter - the right column ran on well past
    # where the left one stopped, leaving a dead gap under the left column
    # and an awkward L-shaped page. Keeping only the driver breakdown next
    # to the hero card, and moving the bar chart to its own full-width row
    # below (same pattern as the dashboard's "Score over time"), gives the
    # page one consistent row rhythm instead of two mismatched column
    # heights.
    with st.container(key="score-top-row"):
        left, right = st.columns([1, 2])
        with left:
            score_hero_card(
                score["overall"],
                f"{score['band']} · {score['verdict']}",
                "Cohort comparison unavailable",
                data["points_to_ready"],
            )
            st.markdown(f"""
            <div class="ea-card ea-kv-card">
                <div class="ea-kv"><span>Cohort average</span><b>Unavailable</b></div>
                <div class="ea-kv"><span>Job-ready threshold</span><b>{score['job_ready_threshold']}</b></div>
                <div class="ea-kv"><span>Percentile</span><b>Unavailable</b></div>
            </div>
            """, unsafe_allow_html=True)
        with right:
            with st.container(key="score-drivers-card"):
                icon_header("trend", "Why you got this score")
                st.caption("Weighted component differences versus your overall score; these are not cohort comparisons.")
                rows = ""
                for d in data["score_drivers"]:
                    positive = d["impact"] > 0
                    sign = "+" if positive else ""
                    width = min(abs(d["impact"]) * 8, 100)
                    cls = "pos" if positive else "neg"
                    rows += f"""
                    <div class="ea-driver {cls}">
                        <span class="ea-driver-label">{d['label']}</span>
                        <span class="ea-driver-track"><span class="ea-driver-fill" style="width:{width}%;"></span></span>
                        <span class="ea-driver-value">{sign}{d['impact']}</span>
                    </div>"""
                if rows:
                    st.markdown(f'<div class="ea-driver-list">{rows}</div>', unsafe_allow_html=True)
                else:
                    st.caption("No component differs from the overall score.")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    with panel("score-breakdown", "analytics", "What makes up your score", "Each component is normalized to 0–100 and combined using the configured weights"):
        charts.bar([s["label"] for s in data["score_breakdown"]], [s["value"] for s in data["score_breakdown"]], warn_below=55)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    gap = data["skill_gap"]
    assessment = data["analytics"]["latest_assessment"]
    stats = [
        ("Readiness verdict", score["verdict"], f"Threshold: {score['job_ready_threshold']}/100"),
        ("Compared skill levels", f"{gap['compared_count']} of {gap['total_requirement_count']}", f"{len(gap['gaps'])} recorded gaps · {gap['high_count']} high"),
        ("Roles compared", str(len(data["career_matches"])), "Fit uses recorded skills and dataset requirements"),
        ("Latest assessment", f"{assessment['overall_pct']}%" if assessment else "Unavailable", "Current session only"),
    ]
    with st.container(key="cards-score-stats"):
        for col, (label, value, hint) in zip(st.columns(4), stats):
            with col:
                st.markdown(f"""
                <div class="ea-card ea-tile ea-stat-tile">
                    <div class="ea-small">{label}</div>
                    <div class="ea-section" style="margin-top:4px;">{value}</div>
                    <div class="ea-small" style="margin-top:4px;">{hint}</div>
                </div>
                """, unsafe_allow_html=True)
