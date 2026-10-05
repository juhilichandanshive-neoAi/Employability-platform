import streamlit as st
from components.tables import responsive_table
from components.cards import icon_header, section_header, panel
from components.cards import message_banner
from components.html import render_html
from services.session import current_app_data
from utils.state import go_to


def render():
    data = current_app_data()
    recommendations = data["certification_recommendations"]
    section_header(
        "Certification Recommendations",
        "Suggested credentials are mapped to measured skill gaps. Prices, ratings, durations, and score uplift are not estimated.",
    )

    with st.container(key="equal-cert-top"):
        if recommendations:
            cols = st.columns(min(3, len(recommendations)))
            for col, cert in zip(cols, recommendations):
                with col:
                    with panel(f"cert-{cert['rank']}", kind="pcard"):
                        render_html(f"""
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div class="ea-small">{cert['provider']} · PRIORITY {cert['rank']}</div>
                            <span class="ea-badge ea-badge-purple">{cert['level']}</span>
                        </div>
                        <div class="ea-section" style="font-size:20px;line-height:1.4;margin-top:6px;">{cert['name']}</div>
                        <div class="ea-small" style="margin-top:8px;">Addresses <b>{cert['gaps_closed']}</b> for {data['profile']['target_role']}.</div>
                        <div class="ea-small" style="margin-top:6px;">Cost, duration, rating, and score uplift are not available from the current sources.</div>
                        """)
                        if st.button("View learning plan", key=f"cert-roadmap-{cert['rank']}", width="stretch"):
                            go_to("roadmap")
                            st.rerun()
        else:
            message_banner(
                "No certification recommendations yet",
                "Add skill levels and complete a role comparison. Recommendations are only made for measured gaps that have a catalog mapping.",
                kind="info",
            )

    if recommendations:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        icon_header("grid", "Recommendations from measured gaps")
        headers = ["Certification", "Provider", "Level", "Gap addressed", "Evidence"]
        rows = [
            [c["name"], c["provider"], c["level"], c["gaps_closed"], c["asked_in"]]
            for c in recommendations
        ]

        def mobile_row(row):
            name, provider, level, gap, evidence = row
            return f"""
            <div class="ea-card" style="margin-bottom:8px;">
                <b>{name}</b><br/>
                <span class="ea-small">{provider} · {level} · {gap} · {evidence}</span>
            </div>
            """

        with panel("cert-table", "grid", "All current recommendations", "No live price, duration, or rating data is included"):
            responsive_table(headers, rows, mobile_row)
