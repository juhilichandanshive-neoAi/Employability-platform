from copy import deepcopy
from html import escape as html_escape

import streamlit as st

from components.cards import panel, section_header
from services.integration import SUPPORTED_ROLES
from services.session import current_app_data


PERSONAL_FIELDS = {
    "profile_name": "name",
    "profile_enrolment_id": "enrolment_id",
    "profile_email": "email",
    "profile_phone": "phone",
    "profile_degree": "degree",
    "profile_semester": "semester",
    "profile_github": "github",
    "profile_linkedin": "linkedin",
    "profile_languages": "languages",
}


def _save(profile: dict):
    st.session_state.profile = profile
    st.session_state.profile_saved = True
    st.session_state["_profile_saved_notice"] = True
    st.rerun()


def _remove_item(field: str, index: int, profile: dict):
    updated = deepcopy(profile)
    updated[field].pop(index)
    _save(updated)


def render():
    data = current_app_data()
    profile = data["profile"]
    for widget_key, profile_key in PERSONAL_FIELDS.items():
        st.session_state.setdefault(widget_key, profile.get(profile_key) or "")
    st.session_state.setdefault("profile_target_role", profile.get("target_role", SUPPORTED_ROLES[0]))
    st.session_state.setdefault("profile_cgpa", float(profile.get("cgpa") or 0))

    section_header(
        "Student Profile",
        "Enter information used for your score and recommendations. Profile data stays in this session.",
    )
    if st.session_state.pop("_profile_saved_notice", False):
        st.success("Profile changes saved for this session.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-profile-header"):
        hc1, hc2 = st.columns([3, 1])
        with hc1:
            with panel("profile-identity", kind="pcard"):
                student = data["student"]
                cgpa = f"CGPA {profile['cgpa']}" if profile.get("cgpa") is not None else "CGPA not provided"
                st.markdown(f"""
                <div style="display:flex;gap:16px;align-items:center;">
                    <div style="width:56px;height:56px;border-radius:999px;background:#7C3AED;color:#fff;flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;font-weight:700;font-size:18px;">{html_escape(student['initials'])}</div>
                    <div>
                        <div class="ea-section">{html_escape(student['name'] or 'Your profile')}</div>
                        <div class="ea-small">{html_escape(profile.get('degree') or 'Education not provided')} · {html_escape(profile.get('semester') or 'Semester not provided')} · {html_escape(cgpa)}</div>
                        <div class="ea-small">{html_escape(profile.get('email') or 'Email not provided')} · {html_escape(profile['target_role'])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        with hc2:
            with panel("profile-completion", kind="pcard"):
                st.markdown(f"""
                <div style="text-align:center;">
                    <div class="ea-small">Profile completion</div>
                    <div class="ea-big-number" style="font-size:28px;">{data['profile_completion']}%</div>
                </div>
                """, unsafe_allow_html=True)

    step_html = ""
    steps = data["profile_steps"]
    for index, step in enumerate(steps, start=1):
        dot_class = {"done": "done", "current": "current"}.get(step["status"], "pending")
        dot_content = "✓" if step["status"] == "done" else str(index)
        label_color = "var(--color-text-primary)" if step["status"] != "pending" else "#8A82A6"
        step_html += (
            '<div style="display:flex;flex-direction:column;align-items:center;gap:4px;min-width:90px;">'
            f'<div class="ea-step-dot {dot_class}">{dot_content}</div>'
            f'<span style="font-size:12px;color:{label_color};text-align:center;">{step["label"]}</span></div>'
        )
        if index < len(steps):
            line_color = "var(--color-success)" if step["status"] == "done" else "var(--color-border)"
            step_html += f'<div style="flex:1;height:2px;background:{line_color};margin-top:11px;"></div>'
    st.markdown(
        f'<div class="ea-card" style="overflow-x:auto;"><div style="display:flex;align-items:flex-start;gap:4px;width:max-content;min-width:100%;">{step_html}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-profile-row-1"):
        left, right = st.columns(2)
        with left:
            with panel("personal", "profile", "Personal information"):
                a, b = st.columns(2)
                a.text_input("Full name", key="profile_name")
                b.text_input("Enrolment ID", key="profile_enrolment_id")
                a, b = st.columns(2)
                a.text_input("Email", key="profile_email")
                b.text_input("Phone", key="profile_phone")
                a, b = st.columns(2)
                a.text_input("Degree", key="profile_degree")
                b.text_input("Semester", key="profile_semester")
                st.number_input("CGPA (0–10)", min_value=0.0, max_value=10.0, step=0.1, key="profile_cgpa")
                st.selectbox("Target role", SUPPORTED_ROLES, key="profile_target_role")
                st.text_input("GitHub profile", key="profile_github")
                st.text_input("LinkedIn profile", key="profile_linkedin")
                st.text_input("Languages", key="profile_languages")
        with right:
            with panel("skills", "skill_gap", "Skills"):
                for index, skill in enumerate(profile["skills"]):
                    item, remove = st.columns([4, 1])
                    item.markdown(
                        f'<span class="ea-badge ea-badge-purple" style="margin:3px;">{html_escape(skill["name"])} · {html_escape(str(skill["level"]))}/5</span>',
                        unsafe_allow_html=True,
                    )
                    if remove.button("Remove", key=f"remove-skill-{index}"):
                        _remove_item("skills", index, profile)
                if not profile["skills"]:
                    st.caption("No skill levels recorded.")
                with st.form("add-skill-form", clear_on_submit=True):
                    st.text_input("Skill name", key="new_skill_name", placeholder="e.g. Python")
                    st.slider("Proficiency (0–5)", 0, 5, 0, key="new_skill_level")
                    add_skill = st.form_submit_button("Add or update skill")
                if add_skill:
                    name = st.session_state.new_skill_name.strip()
                    if name:
                        updated = deepcopy(profile)
                        current = next(
                            (item for item in updated["skills"] if item["name"].casefold() == name.casefold()),
                            None,
                        )
                        if current:
                            current["level"] = st.session_state.new_skill_level
                        else:
                            updated["skills"].append(
                                {"name": name, "level": st.session_state.new_skill_level}
                            )
                        _save(updated)
                    else:
                        st.warning("Enter a skill name before adding it.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-profile-row-2"):
        left, right = st.columns(2)
        with left:
            with panel("education", "book", "Education"):
                if data["education"]:
                    for education in data["education"]:
                        a, b = st.columns([3, 1])
                        a.markdown(
                            f'<b>{html_escape(education["level"])}</b><br/><span class="ea-small">{html_escape(education["meta"])}</span>',
                            unsafe_allow_html=True,
                        )
                        b.markdown(
                            f'<div style="text-align:right;padding-top:6px;font-weight:600;">{html_escape(education["score"])}</div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("Add education details above.")
        with right:
            with panel("certifications", "certifications", f"Certifications ({len(profile['certifications'])} held)"):
                for index, cert in enumerate(profile["certifications"]):
                    item, remove = st.columns([3, 1])
                    item.markdown(
                        f'<b>{html_escape(cert["name"])}</b><br/><span class="ea-small">{html_escape(cert.get("provider") or "Provider not provided")}</span>',
                        unsafe_allow_html=True,
                    )
                    if remove.button("Remove", key=f"remove-cert-{index}"):
                        _remove_item("certifications", index, profile)
                with st.form("add-certification-form", clear_on_submit=True):
                    cert_name = st.text_input("Certification name", key="new_cert_name")
                    cert_provider = st.text_input("Provider", key="new_cert_provider")
                    add_cert = st.form_submit_button("Add certification")
                if add_cert and cert_name.strip():
                    updated = deepcopy(profile)
                    updated["certifications"].append(
                        {"name": cert_name.strip(), "provider": cert_provider.strip()}
                    )
                    _save(updated)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with st.container(key="equal-profile-row-3"):
        left, right = st.columns(2)
        with left:
            with panel("projects", "folder", f"Projects ({len(profile['projects'])})", kind="pcard"):
                for index, project in enumerate(profile["projects"]):
                    st.markdown(f'<b>{html_escape(project["title"])}</b>', unsafe_allow_html=True)
                    if project.get("description"):
                        st.markdown(f'<div class="ea-body">{html_escape(project["description"])}</div>', unsafe_allow_html=True)
                    if project.get("tags"):
                        st.markdown(" ".join(f'<span class="ea-badge ea-badge-neutral">{html_escape(tag)}</span>' for tag in project["tags"]), unsafe_allow_html=True)
                    if st.button("Remove project", key=f"remove-project-{index}"):
                        _remove_item("projects", index, profile)
                with st.form("add-project-form", clear_on_submit=True):
                    title = st.text_input("Project title", key="new_project_title")
                    description = st.text_area("Description", key="new_project_description")
                    tags = st.text_input("Technologies (comma-separated)", key="new_project_tags")
                    add_project = st.form_submit_button("Add a project")
                if add_project and title.strip():
                    updated = deepcopy(profile)
                    updated["projects"].append(
                        {
                            "title": title.strip(),
                            "description": description.strip(),
                            "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                        }
                    )
                    _save(updated)
        with right:
            with panel("resume", "reports", "Resume", kind="pcard"):
                uploaded = st.file_uploader("Upload a PDF resume", type=["pdf"], key="profile_resume_upload")
                if profile.get("resume"):
                    st.markdown(
                        f'<b>{html_escape(profile["resume"]["filename"])}</b><br/><span class="ea-small">Session only · not parsed or used in the score</span>',
                        unsafe_allow_html=True,
                    )
                elif uploaded:
                    st.caption(f"Selected: {uploaded.name}. Save changes to keep its name in this session.")
                else:
                    st.caption("No resume selected.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    with panel("internships", "careers", "Internships", kind="pcard"):
        for index, internship in enumerate(profile["internships"]):
            item, remove = st.columns([4, 1])
            item.markdown(
                f'<b>{html_escape(internship["role"])}</b><br/><span class="ea-small">{html_escape(internship.get("organization") or "Organization not provided")}</span>',
                unsafe_allow_html=True,
            )
            if remove.button("Remove", key=f"remove-internship-{index}"):
                _remove_item("internships", index, profile)
        with st.form("add-internship-form", clear_on_submit=True):
            internship_role = st.text_input("Role", key="new_internship_role")
            organization = st.text_input("Organization", key="new_internship_org")
            add_internship = st.form_submit_button("Add internship")
        if add_internship and internship_role.strip():
            updated = deepcopy(profile)
            updated["internships"].append(
                {"role": internship_role.strip(), "organization": organization.strip()}
            )
            _save(updated)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid var(--color-border);margin:0 0 16px 0;">', unsafe_allow_html=True)
    st.markdown(
        '<div class="ea-small" style="text-align:center;margin-bottom:12px;">'
        'Save changes to update your session profile. Scores are calculated only after an assessment is completed.</div>',
        unsafe_allow_html=True,
    )
    _, save_col, _ = st.columns([1, 1, 1])
    with save_col:
        if st.button("Save changes", type="primary", key="save-changes-bottom", width="stretch"):
            updated = deepcopy(profile)
            for widget_key, profile_key in PERSONAL_FIELDS.items():
                updated[profile_key] = st.session_state.get(widget_key, "").strip()
            updated["target_role"] = st.session_state.profile_target_role
            updated["track"] = updated["target_role"]
            cgpa = st.session_state.profile_cgpa
            updated["cgpa"] = float(cgpa) if cgpa > 0 else None
            if st.session_state.get("profile_resume_upload") is not None:
                resume = st.session_state.profile_resume_upload
                updated["resume"] = {"filename": resume.name, "size_bytes": resume.size}
            _save(updated)