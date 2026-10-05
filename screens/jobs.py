"""Job Opportunities screen displaying verified industry openings from the admin CSV dataset.

Source of truth: data/Merged_industry_jobs_industry_jobs.csv
"""

from __future__ import annotations

import streamlit as st

from components.cards import panel
from components.badges import badge
from components.html import render_html
from components.icons import icon
from services.job_service import (
    load_admin_jobs,
    filter_jobs,
    calculate_job_match,
    get_saved_jobs_for_user,
    save_user_job,
    unsave_user_job,
    is_job_saved,
    get_user_saved_job_ids,
    get_csv_metadata,
)
from utils.state import go_to


def render():
    user_id = st.session_state.get("current_user_id") or st.session_state.get("user_id", "")
    profile = st.session_state.get("profile", {})

    # Top Header Banner
    header_html = (
        '<div class="ea-page-header">'
        '  <div class="ea-page-title" style="display:flex;align-items:center;gap:12px;">'
        f'   <span style="color:var(--color-primary);">{icon("briefcase", size=28)}</span>'
        '    <span>Job Opportunities</span>'
        '  </div>'
        '  <div class="ea-page-subtitle">'
        '    Explore verified industry job openings loaded directly from the admin industry dataset. '
        '    Review skill benchmarks, analyze your profile match, and apply directly.'
        '  </div>'
        '</div>'
    )
    render_html(header_html)

    # Load all jobs from admin CSV
    all_jobs = load_admin_jobs()
    if not all_jobs:
        st.warning("No job postings found in the admin dataset (`data/Merged_industry_jobs_industry_jobs.csv`).")
        return

    # User saved job IDs
    saved_job_ids = get_user_saved_job_ids(user_id) if user_id else set()

    # Metrics Overview Row
    unique_companies = len({j["company"] for j in all_jobs if j.get("company")})
    unique_roles = len({j["role"] for j in all_jobs if j.get("role")})
    fresher_count = sum(1 for j in all_jobs if "fresher" in j["experience"].lower() or "0" in j["experience"])

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with panel("stat-total", None, None):
            render_html(f'<div class="ea-metric-label">Total Verified Openings</div>'
                        f'<div class="ea-metric-value" style="color:var(--color-primary);">{len(all_jobs)}</div>'
                        f'<div class="ea-small" style="color:var(--color-text-muted);">Admin Dataset Records</div>')
    with m2:
        with panel("stat-companies", None, None):
            render_html(f'<div class="ea-metric-label">Hiring Companies</div>'
                        f'<div class="ea-metric-value">{unique_companies}</div>'
                        f'<div class="ea-small" style="color:var(--color-text-muted);">Top tech & enterprise firms</div>')
    with m3:
        with panel("stat-freshers", None, None):
            render_html(f'<div class="ea-metric-label">Entry & Fresher Roles</div>'
                        f'<div class="ea-metric-value" style="color:#059669;">{fresher_count}</div>'
                        f'<div class="ea-small" style="color:var(--color-text-muted);">Suitable for recent graduates</div>')
    with m4:
        with panel("stat-saved", None, None):
            render_html(f'<div class="ea-metric-label">My Saved Opportunities</div>'
                        f'<div class="ea-metric-value" style="color:#7C3AED;">{len(saved_job_ids)}</div>'
                        f'<div class="ea-small" style="color:var(--color-text-muted);">Bookmarked for application</div>')

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Main Tabs
    tab_all, tab_matched, tab_saved = st.tabs([
        f"💼 All Opportunities ({len(all_jobs)})",
        "🎯 Matches for You",
        f"🔖 Saved Jobs ({len(saved_job_ids)})",
    ])

    # ----------------------------------------------------------- TAB 1: ALL JOBS --
    with tab_all:
        _render_jobs_browser(all_jobs, profile, user_id, saved_job_ids, tab_key="all")

    # ------------------------------------------------------- TAB 2: MATCHED JOBS --
    with tab_matched:
        has_skills = bool(profile.get("skills"))
        if not has_skills:
            render_html(
                '<div class="ea-card" style="padding:24px;text-align:center;background:var(--color-accent-bg);border:1px solid #DDD6FE;border-radius:12px;margin:12px 0;">'
                '  <h4 style="margin:0 0 8px 0;color:var(--color-primary);">Complete Your Profile for Real-Time Matching</h4>'
                '  <p style="color:var(--color-text-muted);max-width:550px;margin:0 auto 16px auto;">'
                '    Personalized matching requires your actual skill ratings from your profile. '
                '    Once added, EmployaAI compares your skill proficiencies against each opening’s 10 skill benchmarks.'
                '  </p>'
                '</div>'
            )
            col_act1, col_act2, _ = st.columns([1.5, 1.5, 4])
            with col_act1:
                if st.button("Go to Profile →", key="btn-goto-profile-from-matched", type="primary"):
                    go_to("profile")
            with col_act2:
                if st.button("Take Assessment →", key="btn-goto-assess-from-matched"):
                    go_to("assessment")
        else:
            # Calculate match for all jobs and sort descending
            scored_jobs = []
            for j in all_jobs:
                match_res = calculate_job_match(j, profile)
                scored_jobs.append((j, match_res))
            scored_jobs.sort(key=lambda item: item[1].get("score") or 0, reverse=True)

            high_matches = [item for item in scored_jobs if (item[1].get("score") or 0) >= 60]
            render_html(
                f'<div class="ea-small" style="color:var(--color-text-muted);margin-bottom:12px;">'
                f'  Showing <b>{len(high_matches)}</b> job postings with 60%+ skill alignment to your profile.'
                f'</div>'
            )
            _render_job_card_list([j for j, _ in high_matches], profile, user_id, saved_job_ids, tab_key="matched")

    # --------------------------------------------------------- TAB 3: SAVED JOBS --
    with tab_saved:
        if not saved_job_ids:
            render_html(
                '<div class="ea-card" style="padding:32px;text-align:center;background:#F8FAFC;border:1px dashed #CBD5E1;border-radius:12px;margin:16px 0;">'
                '  <div style="font-size:2rem;margin-bottom:8px;">🔖</div>'
                '  <h4 style="margin:0 0 6px 0;">No Saved Jobs Yet</h4>'
                '  <p style="color:var(--color-text-muted);font-size:0.9rem;">'
                '    Bookmark interesting roles from the All Opportunities tab to track and apply to them later.'
                '  </p>'
                '</div>'
            )
        else:
            saved_jobs = [j for j in all_jobs if j["id"] in saved_job_ids]
            _render_job_card_list(saved_jobs, profile, user_id, saved_job_ids, tab_key="saved")


def _render_jobs_browser(
    all_jobs: list[dict],
    profile: dict,
    user_id: str,
    saved_job_ids: set[int],
    tab_key: str,
):
    """Render search, filter controls, and the list of jobs."""
    # Filter UI
    f_c1, f_c2, f_c3, f_c4 = st.columns([2.5, 1.8, 1.5, 1.2])

    with f_c1:
        search_query = st.text_input(
            "Search postings",
            placeholder="Search by role, company, or skill (e.g. AWS, DevOps, Capgemini)...",
            key=f"jobs-search-{tab_key}",
            label_visibility="collapsed",
        )

    # Distinct roles for dropdown
    unique_roles = sorted({j["role"] for j in all_jobs if j.get("role")})
    with f_c2:
        role_filter = st.selectbox(
            "Role",
            options=["All"] + unique_roles,
            key=f"jobs-role-filter-{tab_key}",
            label_visibility="collapsed",
        )

    # Distinct experience options
    exp_options = ["All", "Fresher", "0-1", "0-2", "Entry Level"]
    with f_c3:
        exp_filter = st.selectbox(
            "Experience",
            options=exp_options,
            key=f"jobs-exp-filter-{tab_key}",
            label_visibility="collapsed",
        )

    with f_c4:
        salary_only = st.checkbox("Disclosed Salary Only", key=f"jobs-sal-filter-{tab_key}")

    # Skill filter dropdown
    skill_options = ["All", "Python", "Linux", "Networking", "AWS", "Azure", "Docker", "Kubernetes", "Terraform", "Cybersecurity"]
    sub_c1, sub_c2 = st.columns([2, 5])
    with sub_c1:
        skill_filter = st.selectbox(
            "Filter by High Skill Requirement (>= 5/10)",
            options=skill_options,
            key=f"jobs-skill-filter-{tab_key}",
        )

    # Apply filters
    filtered = filter_jobs(
        all_jobs,
        search_query=search_query,
        role_filter=role_filter,
        experience_filter=exp_filter,
        skill_filter=skill_filter,
        salary_only=salary_only,
    )

    # Result count & data refresh control
    info_c1, info_c2 = st.columns([4, 1], vertical_alignment="center")
    with info_c1:
        render_html(
            f'<div class="ea-small" style="color:var(--color-text-muted);margin:8px 0;">'
            f'  Displaying <b>{len(filtered)}</b> of {len(all_jobs)} verified postings'
            f'</div>'
        )
    with info_c2:
        if st.button("🔄 Refresh Data", key=f"btn-reload-csv-{tab_key}", help="Reload the admin CSV from disk"):
            load_admin_jobs(force_reload=True)
            st.rerun()

    if not filtered:
        render_html(
            '<div class="ea-card" style="padding:28px;text-align:center;background:#F8FAFC;border:1px dashed #CBD5E1;border-radius:12px;margin:16px 0;">'
            '  <h4>No matching job postings found</h4>'
            '  <p style="color:var(--color-text-muted);font-size:0.9rem;">'
            '    Try clearing filters or adjusting your search keyword.'
            '  </p>'
            '</div>'
        )
        return

    _render_job_card_list(filtered, profile, user_id, saved_job_ids, tab_key=tab_key)


def _render_job_card_list(
    jobs: list[dict],
    profile: dict,
    user_id: str,
    saved_job_ids: set[int],
    tab_key: str,
):
    """Render cards for a list of job postings with pagination."""
    # Pagination
    PAGE_SIZE = 15
    page_key = f"_jobs_page_idx_{tab_key}"
    curr_page = st.session_state.get(page_key, 0)
    total_pages = max(1, (len(jobs) + PAGE_SIZE - 1) // PAGE_SIZE)
    curr_page = min(curr_page, total_pages - 1)

    start_idx = curr_page * PAGE_SIZE
    page_jobs = jobs[start_idx : start_idx + PAGE_SIZE]

    for job in page_jobs:
        _render_single_job_card(job, profile, user_id, saved_job_ids, tab_key)

    # Pagination controls
    if total_pages > 1:
        render_html("<div style='height:12px;'></div>")
        p_c1, p_c2, p_c3 = st.columns([2, 3, 2], vertical_alignment="center")
        with p_c1:
            if curr_page > 0:
                if st.button("← Previous", key=f"btn-prev-{tab_key}-{curr_page}"):
                    st.session_state[page_key] = curr_page - 1
                    st.rerun()
        with p_c2:
            render_html(
                f'<div style="text-align:center;font-size:0.85rem;color:var(--color-text-muted);">'
                f'  Page <b>{curr_page + 1}</b> of <b>{total_pages}</b> ({len(jobs)} total jobs)'
                f'</div>'
            )
        with p_c3:
            if curr_page < total_pages - 1:
                if st.button("Next →", key=f"btn-next-{tab_key}-{curr_page}"):
                    st.session_state[page_key] = curr_page + 1
                    st.rerun()


def _render_single_job_card(
    job: dict,
    profile: dict,
    user_id: str,
    saved_job_ids: set[int],
    tab_key: str,
):
    """Render a single job opportunity card matching EmployaAI design."""
    jid = job["id"]
    is_saved = jid in saved_job_ids
    match_info = calculate_job_match(job, profile)

    with st.container(key=f"job-card-{tab_key}-{jid}"):
        # Match badge HTML
        if match_info.get("has_data") and match_info.get("score") is not None:
            score = match_info["score"]
            score_bg = "#ECFDF5" if score >= 70 else ("#FEF3C7" if score >= 50 else "#F3F4F6")
            score_color = "#059669" if score >= 70 else ("#D97706" if score >= 50 else "#4B5563")
            match_badge_html = (
                f'<span style="background:{score_bg};color:{score_color};padding:3px 8px;'
                f'border-radius:12px;font-size:0.75rem;font-weight:600;">'
                f'{score}% Match'
                f'</span>'
            )
        else:
            match_badge_html = ""

        # Top skills chips HTML
        top_chips_html = "".join([
            f'<span style="background:#F3E8FF;color:#6B21A8;padding:2px 7px;border-radius:6px;font-size:0.75rem;margin-right:6px;font-weight:500;">'
            f'{s["name"]}: {s["level"]}/10</span>'
            for s in job["top_skills"][:4]
        ])

        # Card HTML markup
        card_markup = (
            f'<div class="ea-card" style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:16px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
            f'  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">'
            f'    <div>'
            f'      <div style="font-weight:700;font-size:1.05rem;color:var(--color-text);">{job["title"]}</div>'
            f'      <div style="font-size:0.88rem;color:var(--color-primary);font-weight:600;margin-top:2px;">{job["company"]}</div>'
            f'    </div>'
            f'    <div style="display:flex;align-items:center;gap:8px;">'
            f'      {match_badge_html}'
            f'      <span style="background:#EEF2FF;color:#4338CA;padding:3px 8px;border-radius:6px;font-size:0.75rem;font-weight:600;">{job["experience"]}</span>'
            f'      <span style="background:#F0FDF4;color:#15803D;padding:3px 8px;border-radius:6px;font-size:0.75rem;font-weight:600;">{job["salary_display"]}</span>'
            f'    </div>'
            f'  </div>'
            f'  <div style="margin-top:10px;display:flex;align-items:center;gap:6px;flex-wrap:wrap;">'
            f'    <span style="font-size:0.78rem;color:var(--color-text-muted);margin-right:4px;">Key Skill Benchmarks:</span>'
            f'    {top_chips_html}'
            f'  </div>'
            f'</div>'
        )
        render_html(card_markup)

        # Action bar row
        btn_c1, btn_c2, btn_c3, btn_c4 = st.columns([1.5, 1.2, 1.2, 3], vertical_alignment="center")

        # 1. Apply Now Button
        with btn_c1:
            if job.get("has_url"):
                st.link_button("Apply Now ↗", url=job["url"], type="primary", use_container_width=True)
            else:
                st.button("Apply (Link Unavailable)", key=f"btn-no-url-{tab_key}-{jid}", disabled=True, use_container_width=True)

        # 2. Save / Bookmark toggle button
        with btn_c2:
            if is_saved:
                if st.button("⭐ Saved", key=f"btn-unsave-{tab_key}-{jid}", use_container_width=True, help="Click to remove from saved"):
                    unsave_user_job(user_id, jid)
                    st.rerun()
            else:
                if st.button("🔖 Save", key=f"btn-save-{tab_key}-{jid}", use_container_width=True, help="Save to my jobs"):
                    if not user_id:
                        st.warning("Please sign in to save jobs.")
                    else:
                        save_user_job(user_id, jid)
                        st.rerun()

        # 3. View Details expander toggle
        with btn_c3:
            show_details = st.toggle("Details", key=f"toggle-details-{tab_key}-{jid}")

        # Render full details when toggled
        if show_details:
            with panel(f"details-panel-{tab_key}-{jid}", "grid", f"Job #{jid} - Complete Skill Benchmark Profile"):
                d_c1, d_c2 = st.columns([3, 2])
                with d_c1:
                    render_html("<div class='ea-small' style='font-weight:600;margin-bottom:8px;'>All 10 Required Competencies (1-10 Scale):</div>")
                    # Render progress meters for all 10 skills
                    for skill_name, req_lvl in job["skills"].items():
                        pct = req_lvl * 10
                        bar_html = (
                            f'<div style="margin-bottom:6px;">'
                            f'  <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:2px;">'
                            f'    <span>{skill_name}</span>'
                            f'    <b>{req_lvl}/10</b>'
                            f'  </div>'
                            f'  <div style="background:#E2E8F0;height:6px;border-radius:3px;overflow:hidden;">'
                            f'    <div style="background:var(--color-primary);width:{pct}%;height:100%;"></div>'
                            f'  </div>'
                            f'</div>'
                        )
                        render_html(bar_html)

                with d_c2:
                    render_html("<div class='ea-small' style='font-weight:600;margin-bottom:8px;'>Posting Metadata:</div>")
                    meta_html = (
                        f'<div style="font-size:0.83rem;color:var(--color-text-muted);line-height:1.7;">'
                        f'  <div><b>Company:</b> {job["company"]}</div>'
                        f'  <div><b>Role:</b> {job["role"]}</div>'
                        f'  <div><b>Experience:</b> {job["experience"]}</div>'
                        f'  <div><b>Salary LPA:</b> {job["salary_display"]}</div>'
                        f'  <div><b>Location:</b> {job["location"]}</div>'
                        f'  <div><b>Dataset Record ID:</b> #{job["id"]}</div>'
                        f'</div>'
                    )
                    render_html(meta_html)

                    if match_info.get("has_data") and match_info.get("score") is not None:
                        render_html("<div style='height:8px;'></div>")
                        render_html(f"<div class='ea-small' style='font-weight:600;color:var(--color-primary);'>Your Skills Match Analysis:</div>")
                        if match_info.get("matched_skills"):
                            render_html(f"<div style='font-size:0.78rem;color:#059669;'>✓ Strengths: {', '.join(match_info['matched_skills'])}</div>")
                        if match_info.get("gap_skills"):
                            render_html(f"<div style='font-size:0.78rem;color:#DC2626;'>⚠ Gaps to Bridge: {', '.join(match_info['gap_skills'][:3])}</div>")

        render_html("<div style='height:4px;'></div>")
