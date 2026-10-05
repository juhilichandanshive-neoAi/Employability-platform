import streamlit as st
from components import charts
from components.badges import priority_badge_html
from components.cards import icon_header, section_header, panel, message_banner
from components.html import render_html
from components.tables import responsive_table
from services.session import current_app_data
from utils.state import go_to


def render():
    data = current_app_data()
    gap_data = data["skill_gap"]
    role_name = gap_data["role"]
    rows = gap_data["rows"]
    section_header(
        "Skill Gap Analysis",
        f"Recorded 0–5 skill levels are compared with 1–10 requirements from the bundled dataset snapshot for {role_name}.",
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    high = gap_data["high_count"]
    medium = sum(1 for r in gap_data["gaps"] if r["priority"] == "Medium")
    met = gap_data["met_count"]

    summary = [
        ("Target role", role_name, f"{gap_data['compared_count']} of {gap_data['total_requirement_count']} skills compared"),
        ("Must fix", str(high), "High-priority gaps"),
        ("Already met", str(met), f"{medium} medium gaps in recorded skills"),
    ]
    with st.container(key="equal-skill-summary"):
        for col, (label, value, sub) in zip(st.columns(3), summary):
            with col:
                with panel(f"skill-summary-{label.split()[0].lower()}", kind="pcard"):
                    render_html(f"""
                    <div class="ea-small">{label}</div>
                    <div class="ea-section" style="font-size:22px;line-height:1.5;margin-top:4px;">{value}</div>
                    <div class="ea-small" style="margin-top:4px;">{sub}</div>
                    """)

    if data["dataset"]["status"] != "available":
        message_banner(
            "Dataset unavailable",
            "The bundled job-requirements snapshot could not be loaded. No role comparison was calculated.",
            kind="warning",
        )
        return

    if not rows:
        message_banner(
            "No skill levels to compare",
            "Add one or more skills with proficiency levels in your profile. Unreported skills are not treated as zero.",
            kind="info",
        )
        if st.button("Edit profile", key="skill-gap-edit-profile"):
            go_to("profile")
            st.rerun()
        return

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-skill-compare"):
        left, right = st.columns([1, 1.3])
        with left:
            with panel("skill-radar", "skill_gap", "Your profile against the role", "Profile levels are mapped to the 0–5 display scale"):
                radar = gap_data["radar"]
                charts.radar(radar["categories"], radar["you"], radar["role_requires"], "Role requires")
        with right:
            with panel("skill-needs", "trend", "What is needed against what you have", "Only skills with a saved proficiency level are compared"):
                for row in sorted(rows, key=lambda r: (-r["gap_0_to_5"], r["skill"])):
                    pct = min(round(row["student_level_0_to_5"] / row["required_level_0_to_5"] * 100), 100) if row["required_level_0_to_5"] else 100
                    render_html(f"""
                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;font-size:14px;">
                            <span>{row['skill']}</span>{priority_badge_html(row['priority'])}
                        </div>
                        <div class="ea-progress-track"><div class="ea-progress-fill" style="width:{pct}%;"></div></div>
                    </div>
                    """)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    icon_header("assessment", "Every gap, and what to do about it")
    st.caption(
        f"Requirements aggregated from {gap_data['row_count']} rows in the bundled dataset snapshot. "
        "This is not a live job-posting feed."
    )

    headers = ["Skill", "Asked in", "Required", "You have", "Priority", "Suggested improvement"]
    rows = [
        [r["skill"], r["asked"], r["required"], r["have"], priority_badge_html(r["priority"]), r["action"]]
        for r in rows
    ]

    def mobile_row(r_tuple):
        skill, asked, required, have, priority_html, action = r_tuple
        return f"""
        <div class="ea-card" style="margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <b>{skill}</b>{priority_html}
            </div>
            <div class="ea-small">Needed {required} · You have {have}</div>
            <div class="ea-body" style="margin-top:4px;">{action}</div>
        </div>
        """

    responsive_table(headers, rows, mobile_row)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    render_html('<hr style="border:none;border-top:1px solid var(--color-border);margin:0 0 16px 0;">')
    render_html(
        '<div class="ea-small">Download the current skill-gap plan, or open the generated roadmap.</div>'
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    b1, b2 = st.columns([1, 1])
    from services.reporting import generate_development_plan_pdf
    pdf_bytes, pdf_name = generate_development_plan_pdf(data)
    b1.download_button(
        "Download plan (PDF)",
        data=pdf_bytes,
        file_name=pdf_name,
        mime="application/pdf",
        key="download-plan-bottom",
        width="stretch",
    )
    if b2.button("Open my roadmap →", type="primary", key="build-roadmap-bottom", width="stretch"):
        go_to("roadmap")
        st.rerun()
