import uuid
from copy import deepcopy
from html import escape as html_escape

import streamlit as st

from components.cards import panel, section_header
from components.html import render_html
from services.db import (
    add_education_entry,
    delete_education_entry,
    log_activity,
    save_user_profile,
    update_education_entry,
)
from services.integration import SUPPORTED_ROLES
from services.session import current_app_data, refresh_app_data


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


def _sync_widgets_to_profile(profile: dict) -> dict:
    """Sync current widget values into profile dict to prevent losing user edits."""
    updated = deepcopy(profile)
    for widget_key, profile_key in PERSONAL_FIELDS.items():
        if widget_key in st.session_state:
            val = st.session_state[widget_key]
            updated[profile_key] = val.strip() if isinstance(val, str) else val
    if "profile_target_role" in st.session_state:
        target_role = st.session_state.profile_target_role
        if target_role:
            updated["target_role"] = target_role
            updated["track"] = target_role
    if "profile_cgpa" in st.session_state:
        cgpa = st.session_state.profile_cgpa
        try:
            val = float(cgpa)
            updated["cgpa"] = val if val > 0 else None
        except (ValueError, TypeError):
            pass
    if st.session_state.get("profile_resume_upload") is not None:
        resume = st.session_state.profile_resume_upload
        updated["resume"] = {"filename": resume.name, "size_bytes": resume.size}
    return updated


def _save(profile: dict):
    st.session_state.profile = profile
    st.session_state.profile_saved = True
    st.session_state["_profile_saved_notice"] = True
    st.session_state["_sync_profile_to_widgets"] = True

    # Persist to database if logged-in user exists
    user_id = st.session_state.get("current_user_id")
    if user_id:
        try:
            save_user_profile(user_id, profile)
            log_activity(user_id, "profile_updated", "Profile updated", "Saved updated applicant details.")
        except Exception:
            pass

    refresh_app_data()
    st.rerun()


def _remove_item(field: str, index: int, profile: dict):
    updated = _sync_widgets_to_profile(profile)
    if field in updated and 0 <= index < len(updated[field]):
        removed = updated[field].pop(index)
        user_id = st.session_state.get("current_user_id")
        if field == "education_entries" and user_id and isinstance(removed, dict) and removed.get("id"):
            try:
                delete_education_entry(user_id, removed["id"])
            except Exception:
                pass
        _save(updated)


def render():
    data = current_app_data()
    profile = data["profile"]
    user_id = st.session_state.get("current_user_id")

    if st.session_state.pop("_sync_profile_to_widgets", False):
        for widget_key, profile_key in PERSONAL_FIELDS.items():
            st.session_state[widget_key] = profile.get(profile_key) or ""
        st.session_state["profile_target_role"] = profile.get("target_role", SUPPORTED_ROLES[0])
        st.session_state["profile_cgpa"] = float(profile.get("cgpa") or 0.0)
    else:
        for widget_key, profile_key in PERSONAL_FIELDS.items():
            if widget_key not in st.session_state:
                st.session_state[widget_key] = profile.get(profile_key) or ""
        if "profile_target_role" not in st.session_state:
            st.session_state["profile_target_role"] = profile.get("target_role", SUPPORTED_ROLES[0])
        if "profile_cgpa" not in st.session_state:
            st.session_state["profile_cgpa"] = float(profile.get("cgpa") or 0.0)

    section_header(
        "Student Profile",
        "Manage your academic records, competencies, certifications, and career interests.",
    )
    if st.session_state.pop("_profile_saved_notice", False):
        st.success("Profile changes saved successfully.")

    render_html("<div style='height:16px'></div>")

    # Determine missing profile elements for completion guidance
    missing = []
    if not (profile.get("name") and profile.get("email")):
        missing.append("Name & Email")
    if not (profile.get("degree") or profile.get("education_entries")):
        missing.append("Education entry")
    if not profile.get("skills"):
        missing.append("Skills (with proficiency)")
    if not profile.get("projects"):
        missing.append("1+ Project")
    if not profile.get("certifications"):
        missing.append("Certifications")
    if not profile.get("resume"):
        missing.append("Resume upload")

    # Header Card: Identity + Enrollment ID + Profile Completion
    with st.container(key="equal-row-pheader"):
        hc1, hc2 = st.columns([2.8, 1.2])
        with hc1:
            with panel("profile-identity", kind="pcard"):
                student = data["student"]
                enrollment_id = (
                    st.session_state.get("current_enrollment_id")
                    or profile.get("enrolment_id")
                    or "Not assigned"
                )
                cgpa = f"CGPA {profile['cgpa']}" if profile.get("cgpa") is not None else "CGPA not specified"
                edu_summary = profile.get("degree") or (profile.get("education_entries") and profile["education_entries"][0].get("degree")) or "Education not specified"

                render_html(f"""
                <div style="display:flex;gap:18px;align-items:center;">
                    <div style="width:60px;height:60px;border-radius:999px;background:linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);color:#fff;flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;font-weight:700;font-size:20px;box-shadow:0 4px 12px rgba(124, 58, 237, 0.35);">{html_escape(student['initials'])}</div>
                    <div>
                        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                            <span class="ea-section" style="font-size:20px;font-weight:800;">{html_escape(student['name'] or 'Your Profile')}</span>
                            <span class="ea-badge ea-badge-purple" style="font-family:monospace;font-size:12px;font-weight:700;letter-spacing:0.04em;">🆔 {html_escape(enrollment_id)}</span>
                        </div>
                        <div class="ea-small" style="margin-top:4px;">{html_escape(edu_summary)} · {html_escape(profile.get('semester') or 'Semester not set')} · {html_escape(cgpa)}</div>
                        <div class="ea-small">{html_escape(profile.get('email') or 'Email not provided')} · <b>{html_escape(profile.get('target_role', 'Cloud Solutions Architect'))}</b></div>
                    </div>
                </div>
                """)
        with hc2:
            with panel("profile-completion", kind="pcard"):
                pct = data["profile_completion"]
                missing_str = ", ".join(missing[:3]) if missing else "Profile 100% complete!"
                render_html(f"""
                <div style="text-align:center;">
                    <div class="ea-small" style="font-weight:600;text-transform:uppercase;letter-spacing:.05em;">Profile Completion</div>
                    <div class="ea-big-number" style="font-size:30px;color:var(--color-primary);margin:4px 0;">{pct}%</div>
                    <div class="ea-progress-track" style="margin:6px 0;"><div class="ea-progress-fill" style="width:{pct}%;"></div></div>
                    <div class="ea-small" style="font-size:11.5px;color:var(--color-text-secondary);line-height:1.3;">
                        {f'Missing: <b>{html_escape(missing_str)}</b>' if missing else '<b>All core sections completed</b>'}
                    </div>
                </div>
                """)

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
    render_html(
        f'<div class="ea-card" style="overflow-x:auto;"><div style="display:flex;align-items:flex-start;gap:4px;width:max-content;min-width:100%;">{step_html}</div></div>'
    )

    render_html("<div style='height:16px'></div>")
    with st.container(key="equal-row-p1"):
        left, right = st.columns(2)
        with left:
            with panel("personal", "profile", "Personal information"):
                a, b = st.columns(2)
                a.text_input("Full name", key="profile_name")
                b.text_input("Enrollment ID", key="profile_enrolment_id", disabled=True)
                a, b = st.columns(2)
                a.text_input("Email", key="profile_email")
                b.text_input("Phone", key="profile_phone")
                a, b = st.columns(2)
                a.text_input("Degree / Program", key="profile_degree")
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
                        updated = _sync_widgets_to_profile(profile)
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

    render_html("<div style='height:16px'></div>")

    # =========================================================================
    # ROW 2: FULLY FUNCTIONAL EDUCATION CARD + CERTIFICATIONS
    # =========================================================================
    with st.container(key="equal-row-p2"):
        left, right = st.columns(2)
        with left:
            with panel("education", "book", "Education"):
                st.session_state.setdefault("_show_edu_form", False)
                st.session_state.setdefault("_editing_edu_idx", None)

                edu_entries = profile.get("education_entries", [])

                # Header with visible "+ Add Education" Button
                top_c1, top_c2 = st.columns([2.5, 1.5], vertical_alignment="center")
                with top_c1:
                    render_html(f'<div class="ea-small" style="font-weight:600;">Academic Records ({len(edu_entries)} added)</div>')
                with top_c2:
                    if not st.session_state._show_edu_form and st.session_state._editing_edu_idx is None:
                        if st.button("+ Add Education", key="btn-open-add-edu", width="stretch", type="primary"):
                            st.session_state._show_edu_form = True
                            st.session_state._editing_edu_idx = None
                            st.rerun()

                render_html("<div style='height:8px;'></div>")

                # If Add/Edit Form is currently active
                if st.session_state._show_edu_form or st.session_state._editing_edu_idx is not None:
                    is_edit = st.session_state._editing_edu_idx is not None
                    edit_item = edu_entries[st.session_state._editing_edu_idx] if is_edit and 0 <= st.session_state._editing_edu_idx < len(edu_entries) else {}

                    render_html(f'<div class="ea-card" style="background:var(--color-accent-bg);padding:14px;border:1px solid #DDD6FE;border-radius:12px;margin-bottom:12px;">'
                                f'<b>{"Edit" if is_edit else "Add"} Education Entry</b></div>')

                    with st.form("education-entry-form"):
                        f_degree = st.text_input(
                            "Degree / Qualification *",
                            value=edit_item.get("degree") or edit_item.get("level") or "",
                            placeholder="e.g. Bachelor of Technology / B.Sc / Higher Secondary",
                            key="edu_degree_val",
                        )
                        f_field = st.text_input(
                            "Field of Study / Specialization",
                            value=edit_item.get("field_of_study", ""),
                            placeholder="e.g. Computer Science and Engineering",
                            key="edu_field_val",
                        )
                        f_institution = st.text_input(
                            "College / Institution *",
                            value=edit_item.get("institution", ""),
                            placeholder="e.g. National Institute of Technology",
                            key="edu_inst_val",
                        )
                        y1, y2 = st.columns(2)
                        f_start_year = y1.text_input(
                            "Start Year",
                            value=edit_item.get("start_year", ""),
                            placeholder="e.g. 2021",
                            key="edu_start_val",
                        )
                        f_grad_year = y2.text_input(
                            "Graduation Year / Expected",
                            value=edit_item.get("grad_year") or edit_item.get("year", ""),
                            placeholder="e.g. 2025",
                            key="edu_grad_val",
                        )
                        f_score = st.text_input(
                            "CGPA / Percentage",
                            value=edit_item.get("score", ""),
                            placeholder="e.g. 8.6 CGPA or 86%",
                            key="edu_score_val",
                        )
                        f_desc = st.text_area(
                            "Optional description",
                            value=edit_item.get("description", ""),
                            placeholder="Relevant honors, notable coursework, minor tracks, or projects...",
                            key="edu_desc_val",
                        )

                        fb_save, fb_cancel = st.columns(2)
                        btn_save = fb_save.form_submit_button(
                            "Save Changes" if is_edit else "Add Education",
                            type="primary",
                            width="stretch",
                        )
                        btn_cancel = fb_cancel.form_submit_button("Cancel", width="stretch")

                    if btn_cancel:
                        st.session_state._show_edu_form = False
                        st.session_state._editing_edu_idx = None
                        st.rerun()

                    if btn_save:
                        if not f_degree.strip() or not f_institution.strip():
                            st.error("Degree/Qualification and College/Institution are required.")
                        else:
                            updated = _sync_widgets_to_profile(profile)
                            if "education_entries" not in updated:
                                updated["education_entries"] = []

                            entry_dict = {
                                "id": edit_item.get("id") or f"edu_{uuid.uuid4().hex[:8]}",
                                "degree": f_degree.strip(),
                                "field_of_study": f_field.strip(),
                                "institution": f_institution.strip(),
                                "start_year": f_start_year.strip(),
                                "grad_year": f_grad_year.strip(),
                                "score": f_score.strip(),
                                "description": f_desc.strip(),
                            }

                            if is_edit:
                                updated["education_entries"][st.session_state._editing_edu_idx] = entry_dict
                                if user_id and entry_dict.get("id"):
                                    try:
                                        update_education_entry(user_id, entry_dict["id"], entry_dict)
                                    except Exception:
                                        pass
                            else:
                                updated["education_entries"].append(entry_dict)
                                if user_id:
                                    try:
                                        add_education_entry(user_id, entry_dict)
                                    except Exception:
                                        pass

                            st.session_state._show_edu_form = False
                            st.session_state._editing_edu_idx = None
                            _save(updated)

                else:
                    # Display existing education entries
                    if edu_entries:
                        for idx, edu in enumerate(edu_entries):
                            deg_title = edu.get("degree") or edu.get("level") or "Degree"
                            field_str = f" in {edu['field_of_study']}" if edu.get("field_of_study") else ""
                            inst_str = edu.get("institution") or "Institution not specified"
                            years = f"{edu.get('start_year', '')}–{edu.get('grad_year') or edu.get('year', '')}".strip("–")
                            score_str = edu.get("score")

                            with st.container(border=True):
                                ec1, ec2 = st.columns([3.5, 1.5], vertical_alignment="top")
                                with ec1:
                                    render_html(f"""
                                    <div style="font-weight:700;font-size:15px;color:var(--color-text-primary);">
                                        {html_escape(deg_title)}{html_escape(field_str)}
                                    </div>
                                    <div class="ea-small" style="color:var(--color-primary);font-weight:600;margin-top:2px;">
                                        🏛️ {html_escape(inst_str)}
                                    </div>
                                    <div class="ea-small" style="color:var(--color-text-secondary);margin-top:2px;">
                                        {f'🗓️ {html_escape(years)}' if years else ''}
                                        {f' · <b>Grade:</b> {html_escape(score_str)}' if score_str else ''}
                                    </div>
                                    """)
                                    if edu.get("description"):
                                        render_html(f'<div class="ea-small" style="margin-top:4px;font-style:italic;">{html_escape(edu["description"])}</div>')

                                with ec2:
                                    eb1, eb2 = st.columns(2)
                                    with eb1:
                                        if st.button("✏️", key=f"btn-edit-edu-{idx}", help="Edit this education entry"):
                                            st.session_state._editing_edu_idx = idx
                                            st.session_state._show_edu_form = False
                                            st.rerun()
                                    with eb2:
                                        if st.button("🗑️", key=f"btn-delete-edu-{idx}", help="Remove this education entry"):
                                            _remove_item("education_entries", idx, profile)

                    else:
                        # Professional Empty State
                        render_html("""
                        <div class="ea-card" style="text-align:center;padding:24px 16px;background:var(--color-accent-bg);border:1px dashed #C4B5FD;margin-bottom:12px;">
                            <div style="font-size:24px;margin-bottom:6px;">🎓</div>
                            <div class="ea-section" style="font-size:16px;">No education added yet</div>
                            <div class="ea-small" style="margin-top:4px;margin-bottom:12px;">Add your degrees, certifications, or diplomas to bolster your employability profile.</div>
                        </div>
                        """)

        with right:
            with panel("certifications", "certifications", f"Certifications"):
                st.session_state.setdefault("_show_cert_form", False)
                
                top_c1, top_c2 = st.columns([2.5, 1.5], vertical_alignment="center")
                with top_c1:
                    render_html(f'<div class="ea-small" style="font-weight:600;">Certifications ({len(profile["certifications"])} held)</div>')
                with top_c2:
                    if not st.session_state._show_cert_form:
                        if st.button("+ Add Cert", key="btn-open-add-cert", width="stretch", type="primary"):
                            st.session_state._show_cert_form = True
                            st.rerun()

                render_html("<div style='height:8px;'></div>")

                if st.session_state._show_cert_form:
                    render_html(f'<div class="ea-card" style="background:var(--color-accent-bg);padding:14px;border:1px solid #DDD6FE;border-radius:12px;margin-bottom:12px;">'
                                f'<b>Add Certification Entry</b></div>')
                    with st.form("add-certification-form"):
                        cert_name = st.text_input("Certification name *", key="new_cert_name")
                        cert_provider = st.text_input("Provider", key="new_cert_provider")
                        
                        fb_save, fb_cancel = st.columns(2)
                        add_cert = fb_save.form_submit_button("Save", type="primary", width="stretch")
                        cancel_cert = fb_cancel.form_submit_button("Cancel", width="stretch")

                    if cancel_cert:
                        st.session_state._show_cert_form = False
                        st.rerun()

                    if add_cert:
                        if not cert_name.strip():
                            st.error("Certification name is required.")
                        else:
                            updated = _sync_widgets_to_profile(profile)
                            updated["certifications"].append(
                                {"name": cert_name.strip(), "provider": cert_provider.strip()}
                            )
                            st.session_state._show_cert_form = False
                            _save(updated)
                else:
                    if profile["certifications"]:
                        for index, cert in enumerate(profile["certifications"]):
                            with st.container(border=True):
                                ec1, ec2 = st.columns([3.5, 1.5], vertical_alignment="top")
                                with ec1:
                                    render_html(f"""
                                    <div style="font-weight:700;font-size:15px;color:var(--color-text-primary);">
                                        {html_escape(cert["name"])}
                                    </div>
                                    <div class="ea-small" style="color:var(--color-primary);font-weight:600;margin-top:2px;">
                                        🏢 {html_escape(cert.get("provider") or "Provider not provided")}
                                    </div>
                                    """)
                                with ec2:
                                    if st.button("🗑️", key=f"remove-cert-{index}"):
                                        _remove_item("certifications", index, profile)
                    else:
                        render_html("""
                        <div class="ea-card" style="text-align:center;padding:24px 16px;background:var(--color-accent-bg);border:1px dashed #C4B5FD;margin-bottom:12px;">
                            <div style="font-size:24px;margin-bottom:6px;">🏅</div>
                            <div class="ea-section" style="font-size:16px;">No certifications added</div>
                        </div>
                        """)

    render_html("<div style='height:16px'></div>")
    with st.container(key="equal-row-p3"):
        left, right = st.columns(2)
        with left:
            with panel("projects", "folder", "Projects", kind="pcard"):
                st.session_state.setdefault("_show_proj_form", False)
                
                top_c1, top_c2 = st.columns([2.5, 1.5], vertical_alignment="center")
                with top_c1:
                    render_html(f'<div class="ea-small" style="font-weight:600;">Projects ({len(profile["projects"])} added)</div>')
                with top_c2:
                    if not st.session_state._show_proj_form:
                        if st.button("+ Add Project", key="btn-open-add-proj", width="stretch", type="primary"):
                            st.session_state._show_proj_form = True
                            st.rerun()

                render_html("<div style='height:8px;'></div>")

                if st.session_state._show_proj_form:
                    render_html(f'<div class="ea-card" style="background:var(--color-accent-bg);padding:14px;border:1px solid #DDD6FE;border-radius:12px;margin-bottom:12px;">'
                                f'<b>Add Project Entry</b></div>')
                    with st.form("add-project-form"):
                        title = st.text_input("Project title *", key="new_project_title")
                        description = st.text_area("Description", key="new_project_description")
                        tags = st.text_input("Technologies (comma-separated)", key="new_project_tags")
                        
                        fb_save, fb_cancel = st.columns(2)
                        add_proj = fb_save.form_submit_button("Save", type="primary", width="stretch")
                        cancel_proj = fb_cancel.form_submit_button("Cancel", width="stretch")

                    if cancel_proj:
                        st.session_state._show_proj_form = False
                        st.rerun()
                        
                    if add_proj:
                        if not title.strip():
                            st.error("Project title is required.")
                        else:
                            updated = _sync_widgets_to_profile(profile)
                            updated["projects"].append(
                                {
                                    "title": title.strip(),
                                    "description": description.strip(),
                                    "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                                }
                            )
                            st.session_state._show_proj_form = False
                            _save(updated)
                else:
                    if profile["projects"]:
                        for index, project in enumerate(profile["projects"]):
                            with st.container(border=True):
                                ec1, ec2 = st.columns([3.5, 1.5], vertical_alignment="top")
                                with ec1:
                                    render_html(f'<div style="font-weight:700;font-size:15px;color:var(--color-text-primary);">{html_escape(project["title"])}</div>')
                                    if project.get("description"):
                                        render_html(f'<div class="ea-small" style="color:var(--color-text-secondary);margin-top:2px;">{html_escape(project["description"])}</div>')
                                    if project.get("tags"):
                                        tags_html = " ".join(f'<span class="ea-badge ea-badge-neutral">{html_escape(tag)}</span>' for tag in project["tags"])
                                        render_html(f'<div style="margin-top:6px;">{tags_html}</div>')
                                with ec2:
                                    if st.button("🗑️", key=f"remove-project-{index}"):
                                        _remove_item("projects", index, profile)
                    else:
                        render_html("""
                        <div class="ea-card" style="text-align:center;padding:24px 16px;background:var(--color-accent-bg);border:1px dashed #C4B5FD;margin-bottom:12px;">
                            <div style="font-size:24px;margin-bottom:6px;">💻</div>
                            <div class="ea-section" style="font-size:16px;">No projects added</div>
                        </div>
                        """)
        with right:
            with panel("resume", "reports", "Resume", kind="pcard"):
                uploaded = st.file_uploader("Upload a PDF resume", type=["pdf"], key="profile_resume_upload")
                if profile.get("resume"):
                    render_html(
                        f'<b>{html_escape(profile["resume"]["filename"])}</b><br/><span class="ea-small">Uploaded · Verified attachment</span>'
                    )
                elif uploaded:
                    st.caption(f"Selected: {uploaded.name}. Click Save changes below to persist.")
                else:
                    st.caption("No resume uploaded yet.")

    render_html("<div style='height:16px'></div>")
    with panel("internships", "careers", "Internships", kind="pcard"):
        st.session_state.setdefault("_show_intern_form", False)
        
        top_c1, top_c2 = st.columns([3.5, 1.5], vertical_alignment="center")
        with top_c1:
            render_html(f'<div class="ea-small" style="font-weight:600;">Internships ({len(profile["internships"])} added)</div>')
        with top_c2:
            if not st.session_state._show_intern_form:
                if st.button("+ Add Internship", key="btn-open-add-intern", width="stretch", type="primary"):
                    st.session_state._show_intern_form = True
                    st.rerun()

        render_html("<div style='height:8px;'></div>")

        if st.session_state._show_intern_form:
            render_html(f'<div class="ea-card" style="background:var(--color-accent-bg);padding:14px;border:1px solid #DDD6FE;border-radius:12px;margin-bottom:12px;">'
                        f'<b>Add Internship Entry</b></div>')
            with st.form("add-internship-form"):
                internship_role = st.text_input("Role *", key="new_internship_role")
                organization = st.text_input("Organization", key="new_internship_org")
                
                fb_save, fb_cancel = st.columns(2)
                add_internship = fb_save.form_submit_button("Save", type="primary", width="stretch")
                cancel_intern = fb_cancel.form_submit_button("Cancel", width="stretch")

            if cancel_intern:
                st.session_state._show_intern_form = False
                st.rerun()
                
            if add_internship:
                if not internship_role.strip():
                    st.error("Role is required.")
                else:
                    updated = _sync_widgets_to_profile(profile)
                    updated["internships"].append(
                        {"role": internship_role.strip(), "organization": organization.strip()}
                    )
                    st.session_state._show_intern_form = False
                    _save(updated)
        else:
            if profile["internships"]:
                for index, internship in enumerate(profile["internships"]):
                    with st.container(border=True):
                        ec1, ec2 = st.columns([3.5, 1.5], vertical_alignment="top")
                        with ec1:
                            render_html(f"""
                            <div style="font-weight:700;font-size:15px;color:var(--color-text-primary);">
                                {html_escape(internship["role"])}
                            </div>
                            <div class="ea-small" style="color:var(--color-primary);font-weight:600;margin-top:2px;">
                                🏢 {html_escape(internship.get("organization") or "Organization not provided")}
                            </div>
                            """)
                        with ec2:
                            if st.button("🗑️", key=f"remove-internship-{index}"):
                                _remove_item("internships", index, profile)
            else:
                render_html("""
                <div class="ea-card" style="text-align:center;padding:24px 16px;background:var(--color-accent-bg);border:1px dashed #C4B5FD;margin-bottom:12px;">
                    <div style="font-size:24px;margin-bottom:6px;">💼</div>
                    <div class="ea-section" style="font-size:16px;">No internships added</div>
                </div>
                """)

    render_html("<div style='height:24px'></div>")
    render_html('<hr style="border:none;border-top:1px solid var(--color-border);margin:0 0 16px 0;">')
    render_html(
        '<div class="ea-small" style="text-align:center;margin-bottom:12px;">'
        'Save changes to update your profile across all employability metrics.</div>'
    )
    _, save_col, _ = st.columns([1, 1, 1])
    with save_col:
        if st.button("Save changes", type="primary", key="save-changes-bottom", width="stretch"):
            updated = _sync_widgets_to_profile(profile)
            errors = []

            name = updated.get("name", "").strip()
            if not name:
                errors.append("Full name is required.")

            email = updated.get("email", "").strip()
            if email and ("@" not in email or "." not in email.split("@")[-1]):
                errors.append("Please enter a valid email address.")

            cgpa_val = st.session_state.get("profile_cgpa", 0.0)
            if cgpa_val is not None:
                try:
                    cgpa_f = float(cgpa_val)
                    if cgpa_f < 0.0 or cgpa_f > 10.0:
                        errors.append("CGPA must be between 0.0 and 10.0.")
                except (ValueError, TypeError):
                    errors.append("CGPA must be a valid number between 0.0 and 10.0.")

            gh = updated.get("github", "").strip()
            if gh:
                if any(c in gh for c in " \t\r\n"):
                    errors.append("GitHub profile cannot contain spaces.")
                elif not (gh.startswith("http://") or gh.startswith("https://") or "github.com" in gh):
                    updated["github"] = f"https://github.com/{gh.lstrip('@')}"

            li = updated.get("linkedin", "").strip()
            if li:
                if any(c in li for c in " \t\r\n"):
                    errors.append("LinkedIn profile cannot contain spaces.")
                elif not (li.startswith("http://") or li.startswith("https://") or "linkedin.com" in li):
                    updated["linkedin"] = f"https://linkedin.com/in/{li.lstrip('@')}"

            if errors:
                for err in errors:
                    st.error(err)
            else:
                _save(updated)