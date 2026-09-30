import streamlit as st
from components.badges import badge
from components.cards import icon_header, section_header, panel
from data.dummy_data import (
    STUDENT, PROJECTS_TARGET, CERTS_HELD_COUNT, PROFILE_STEPS, EDUCATION, SKILLS, CERTIFICATIONS_HELD, PROJECTS, RESUME,
)


def render():
    section_header("Student Profile", "All of this feeds into your score. Three sections still need a bit of attention.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-profile-header"):
        hc1, hc2 = st.columns([3, 1])
        with hc1:
            with panel("profile-identity", kind="pcard"):
                st.markdown(f"""
                <div style="display:flex;gap:16px;align-items:center;">
                    <div style="width:56px;height:56px;border-radius:999px;background:#7C3AED;color:#fff;flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;font-weight:700;font-size:18px;">{STUDENT['initials']}</div>
                    <div>
                        <div class="ea-section">{STUDENT['name']}</div>
                        <div class="ea-small">{STUDENT['degree']} · {STUDENT['semester']} · CGPA {STUDENT['cgpa']} · {STUDENT['enrolment_id']}</div>
                        <div class="ea-small">{STUDENT['github']} &nbsp;·&nbsp; {STUDENT['linkedin']} &nbsp;·&nbsp; {STUDENT['languages']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        with hc2:
            with panel("profile-completion", kind="pcard"):
                st.markdown(f"""
                <div style="text-align:center;">
                    <div class="ea-small">Profile completion</div>
                    <div class="ea-big-number" style="font-size:28px;">{STUDENT['profile_completion']}%</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    step_html = ""
    for i, step in enumerate(PROFILE_STEPS, start=1):
        dot_class = {"done": "done", "current": "current"}.get(step["status"], "pending")
        dot_content = "✓" if step["status"] == "done" else str(i)
        label_color = "var(--color-text-primary)" if step["status"] != "pending" else "#8A82A6"
        step_html += (
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px;min-width:90px;">'
            f'<div class="ea-step-dot {dot_class}">{dot_content}</div>'
            f'<span style="font-size:12px;color:{label_color};text-align:center;">{step["label"]}</span></div>'
        )
        if i < len(PROFILE_STEPS):
            line_color = "var(--color-success)" if step["status"] == "done" else "var(--color-border)"
            step_html += f'<div style="flex:1;height:2px;background:{line_color};margin-top:11px;"></div>'
    # Seven steps at a 90px minimum each are wider than a phone viewport -
    # scroll horizontally within the card instead of forcing the whole
    # page wider (the same fix as the assessment question-nav strip).
    st.markdown(
        f'<div class="ea-card" style="overflow-x:auto;">'
        f'<div style="display:flex;align-items:flex-start;gap:4px;width:max-content;min-width:100%;">{step_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-profile-row-1"):
        c1, c2 = st.columns(2)
        with c1:
            with panel("personal", "profile", "Personal information"):
                f1, f2 = st.columns(2)
                f1.text_input("Full name", value=STUDENT["name"])
                f2.text_input("Enrolment ID", value=STUDENT["enrolment_id"])
                f3, f4 = st.columns(2)
                f3.text_input("Email", value=STUDENT["email"])
                f4.text_input("Phone", value=STUDENT["phone"])
        with c2:
            with panel("skills", "skill_gap", "Skills"):
                tag_html = ""
                for s in SKILLS:
                    kind = "ea-badge-error" if s.get("warning") else "ea-badge-purple"
                    tag_html += f'<span class="ea-badge {kind}" style="margin:3px;">{s["name"]} {s["level"]}</span> '
                st.markdown(tag_html, unsafe_allow_html=True)
                st.button("+ Add skill", key="add_skill")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-profile-row-2"):
        c1, c2 = st.columns(2)
        with c1:
            with panel("education", "book", "Education"):
                for edu in EDUCATION:
                    e1, e2 = st.columns([3, 1])
                    e1.markdown(f'<b>{edu["level"]}</b><br/><span class="ea-small">{edu["meta"]}</span>', unsafe_allow_html=True)
                    e2.markdown(f'<div style="text-align:right;padding-top:6px;font-weight:600;">{edu["score"]}</div>', unsafe_allow_html=True)
        with c2:
            with panel("certifications", "certifications", f"Certifications ({CERTS_HELD_COUNT} held)"):
                for c in CERTIFICATIONS_HELD:
                    cc1, cc2 = st.columns([3, 1])
                    cc1.markdown(f'<b>{c["badge"]}</b> &nbsp; {c["name"]}<br/><span class="ea-small">{c["meta"]}</span>', unsafe_allow_html=True)
                    with cc2:
                        badge(c["status"], "success")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-profile-row-3"):
        c1, c2 = st.columns(2)
        with c1:
            with panel("projects", "folder", f"Projects ({len(PROJECTS)} of {PROJECTS_TARGET})", kind="pcard"):
                for p in PROJECTS:
                    st.markdown(f'<b>{p["title"]}</b> <span class="ea-small">· {p["meta"]}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="ea-body">{p["desc"]}</div>', unsafe_allow_html=True)
                    st.markdown(" ".join(f'<span class="ea-badge ea-badge-neutral">{t}</span>' for t in p["tags"]), unsafe_allow_html=True)
                st.button("+ Add a project", width="stretch")
        with c2:
            with panel("resume", "reports", "Resume", kind="pcard"):
                rc1, rc2 = st.columns([3, 1])
                rc1.markdown(f'<b>{RESUME["filename"]}</b><br/><span class="ea-small">{RESUME["meta"]}</span>', unsafe_allow_html=True)
                with rc2:
                    badge(f"Score {RESUME['score']}", "warning")
                st.button("Upload a new resume", width="stretch", key="upload-resume")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with panel("internships", "careers", "Internships", kind="pcard"):
        badge("Empty", "error")
        st.caption("Even a two-week stint counts. 41 of the 74 postings we track ask for one.")
        st.button("Add internship", type="primary", width="stretch")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid var(--color-border);margin:0 0 16px 0;">', unsafe_allow_html=True)
    st.markdown(
        '<div class="ea-small" style="text-align:center;margin-bottom:12px;">'
        'Changes save to your profile and feed straight into your employability score.</div>',
        unsafe_allow_html=True,
    )
    save_l, save_mid, save_r = st.columns([1, 1, 1])
    with save_mid:
        st.button("Save changes", type="primary", key="save-changes-bottom", width="stretch")
