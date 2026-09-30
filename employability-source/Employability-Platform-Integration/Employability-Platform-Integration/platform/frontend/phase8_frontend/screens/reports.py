import streamlit as st
from components.cards import icon_header, section_header, panel
from components.cards import message_banner
from services.reporting import generate_session_report
from services.session import current_app_data


def render():
    data = current_app_data()
    sections = [
        ("Profile summary", "report_include_profile"),
        ("Employability score", "report_include_score"),
        ("Skill gap analysis", "report_include_gaps"),
        ("Assessment details", "report_include_assessment"),
        ("Career recommendations", "report_include_careers"),
        ("Certification recommendations", "report_include_certifications"),
        ("Learning roadmap", "report_include_roadmap"),
    ]
    for _, key in sections:
        st.session_state.setdefault(key, True)

    has_session_evidence = bool(
        data["profile_completion"] or data["analytics"]["latest_assessment"]
    )
    right = section_header(
        "Reports",
        "Generate a PDF from information saved in this session. No report is listed until the PDF is actually created.",
        with_right_col=True,
    )
    with right:
        if st.button(
            "Generate new report",
            type="primary",
            width="stretch",
            disabled=not has_session_evidence,
            key="generate-session-report",
        ):
            selected = {
                label for label, key in sections if st.session_state.get(key, False)
            }
            pdf_bytes, filename = generate_session_report(data, selected)
            st.session_state.current_report_pdf = pdf_bytes
            st.session_state.current_report_filename = filename
            st.session_state.generated_reports.append(
                {
                    "name": filename,
                    "when": filename.removeprefix("employability-report-").rsplit(".", 1)[0],
                    "size_bytes": len(pdf_bytes),
                    "size": f"{len(pdf_bytes) / 1024:.1f} KB",
                    "score": data["score"]["overall"],
                }
            )
            st.success("PDF generated from current-session data.")

    with st.container(key="equal-reports-top"):
        c1, c2, c3 = st.columns(3)
        with c1:
            with panel("report-full", kind="pcard"):
                pdf_bytes = st.session_state.get("current_report_pdf")
                filename = st.session_state.get("current_report_filename")
                latest = st.session_state.generated_reports[-1] if st.session_state.generated_reports else None
                if latest:
                    details = (
                        f"{latest['size']} · {latest['when']} UTC"
                        + (
                            f" · score {latest['score']}/100"
                            if latest["score"] is not None
                            else " · score not calculated"
                        )
                    )
                else:
                    details = "No PDF has been generated in this session."
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">
                    <div class="ea-header-row" style="margin-bottom:0;">
                        <div class="ea-section" style="font-size:18px;">Full report</div>
                    </div>
                </div>
                <div class="ea-small" style="margin-top:6px;">Profile, assessment, role fit, measured skill gaps and recommendations that you select.</div>
                <div style="margin-top:10px;background:#FAF9FC;border:1px solid var(--color-border);border-radius:var(--radius);padding:12px 14px;">
                    <b>{'PDF generated' if latest else 'Not generated'}</b><br/>
                    <span class="ea-small">{details}</span>
                </div>
                """, unsafe_allow_html=True)
                with st.container(key="pbtns-report-full"):
                    if pdf_bytes and filename:
                        st.download_button(
                            "Download PDF",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            type="primary",
                            key="dl-full",
                            width="stretch",
                        )
                    else:
                        st.button("Download PDF", type="primary", key="dl-full", width="stretch", disabled=True)

        with c2:
            with panel("report-progress", kind="pcard"):
                st.markdown(f"""
                <div class="ea-header-row">
                    <div class="ea-section" style="font-size:18px;">Progress summary</div>
                </div>
                <div class="ea-small" style="margin-top:6px;">A current-session summary can be included in the full PDF.</div>
                <div class="ea-small" style="margin-top:10px;">No historical progress period is available.</div>
                """, unsafe_allow_html=True)
                st.caption("Select Profile summary, Employability score, and Assessment details in the contents list.")

        with c3:
            with panel("report-link", kind="pcard"):
                st.markdown(f"""
                <div class="ea-header-row">
                    <div class="ea-section" style="font-size:18px;">Sharing</div>
                </div>
                <div class="ea-small" style="margin-top:6px;">Public report links are not connected. Reports remain in this browser session.</div>
                """, unsafe_allow_html=True)
                st.button("Manage sharing", key="manage-sharing", width="stretch", disabled=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-reports-bottom"):
        left, right = st.columns([1.6, 1])
        with left:
            with panel("report-history", "reports", "Reports generated in this session", "Only real PDF files are listed"):
                for r in reversed(st.session_state.generated_reports):
                    st.markdown(f"""
                    <div class="ea-attempt-row">
                        <div>
                            <b>{r['name']}</b><br/>
                            <span class="ea-small">{r['when']} UTC · {'score ' + str(r['score']) + '/100' if r['score'] is not None else 'score not calculated'} · {r['size']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                if not st.session_state.generated_reports:
                    st.caption("No reports have been generated yet.")
        with right:
            with panel("report-contents", "settings", "What goes in it", "Choose which current-session sections to include"):
                for label, key in sections:
                    st.checkbox(label, key=key)
                st.caption("No cohort position, live job listings, or salary-model prediction is included.")
