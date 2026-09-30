import streamlit as st
from datetime import datetime, timezone
from components.badges import badge
from components.cards import icon_header, progress_bar_card, message_banner
from components.icons import icon
from components import charts
from components.modals import confirm_dialog
from components.fun import celebration_illustration
from data.dummy_data import ASSESSMENT_DOMAINS, ASSESSMENT_DIFFICULTIES, QUESTION_BANK
from neoai.services.assessment import score_assessment
from utils.state import go_to


def render():
    if st.session_state.get("assessment_submitted"):
        _render_results()
    elif not st.session_state.get("assessment_domain") or not st.session_state.get("assessment_difficulty"):
        _render_domain_picker()
    elif not st.session_state.get("assessment_started"):
        _render_instructions()
    else:
        _render_question_flow()


# ---------------------------------------------------------------- picker --

def _select_card(key, label, selected, body_html, min_height, on_select):
    """A fully clickable selection card. The visible card is markdown; an
    invisible full-size st.button is laid over it by CSS (.st-key-sel-*),
    so a click anywhere on the card selects it, it stays keyboard
    focusable, and there is no separate Select button underneath."""
    # Flatten to unindented lines: markdown would otherwise read the
    # indented snippet as a code block and print the HTML as text.
    body_html = "".join(line.strip() for line in body_html.splitlines())
    with st.container(key=f"sel-{key}"):
        state = " selected" if selected else ""
        st.markdown(
            f'<div class="ea-card ea-select-card{state}" style="min-height:{min_height}px;">'
            f'<span class="ea-radio" aria-hidden="true"></span>{body_html}</div>',
            unsafe_allow_html=True,
        )
        if st.button(label, key=f"btn-{key}"):
            on_select()
            st.rerun()


def _set_pick(state_key, value):
    def _apply():
        st.session_state[state_key] = value
    return _apply


def _render_domain_picker():
    st.session_state.setdefault("_pick_domain", None)
    st.session_state.setdefault("_pick_difficulty", None)

    icon_header("skill_gap", "Select your domain")
    st.markdown(
        '<div class="ea-body" style="color:var(--color-text-secondary);">Pick the track you want to be assessed on. '
        'This decides which questions you get for the rest of the assessment.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    with st.container(key="cards-domains"):
        cols = st.columns(len(ASSESSMENT_DOMAINS))
        for col, d in zip(cols, ASSESSMENT_DOMAINS):
            with col:
                body = f"""
                <div class="ea-icon-badge" style="margin:0 auto 10px auto;">{icon(d['icon'], 'var(--color-primary)')}</div>
                <div class="ea-section" style="font-size:16px;line-height:1.5;">{d['name']}</div>
                <div class="ea-small" style="margin-top:6px;">{d['desc']}</div>
                <div class="ea-small" style="margin-top:8px;">{d['questions']} questions · ~{d['minutes']} min</div>
                """
                _select_card(f"domain-{d['key']}", f"Select {d['name']}", st.session_state._pick_domain == d["key"],
                             body, 190, _set_pick("_pick_domain", d["key"]))

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    icon_header("assessment", "Select difficulty")
    with st.container(key="cards-difficulty"):
        diff_cols = st.columns(len(ASSESSMENT_DIFFICULTIES))
        for col, level in zip(diff_cols, ASSESSMENT_DIFFICULTIES):
            with col:
                body = f"""
                <div class="ea-icon-badge" style="margin-bottom:10px;">{icon('analytics', 'var(--color-primary)')}</div>
                <div class="ea-section" style="font-size:16px;line-height:1.5;">{level['name']}</div>
                <div class="ea-small" style="margin-top:2px;">{level['note']}</div>
                """
                _select_card(f"diff-{level['key']}", f"Select {level['name']} difficulty", st.session_state._pick_difficulty == level["key"],
                             body, 130, _set_pick("_pick_difficulty", level["key"]))

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    domain_ok = st.session_state._pick_domain is not None
    diff_ok = st.session_state._pick_difficulty is not None
    ready = domain_ok and diff_ok
    if not domain_ok:
        st.caption("Pick a domain above to continue.")
    elif not diff_ok:
        st.caption("Pick a difficulty above to continue.")
    if st.button("Continue to assessment →", type="primary", width="stretch", disabled=not ready, key="start-assessment"):
        st.session_state.assessment_domain = st.session_state._pick_domain
        st.session_state.assessment_difficulty = st.session_state._pick_difficulty
        st.rerun()


# ------------------------------------------------------------- instructions --

def _render_instructions():
    domain_key = st.session_state.assessment_domain
    domain = next(d for d in ASSESSMENT_DOMAINS if d["key"] == domain_key)
    difficulty = next(d for d in ASSESSMENT_DIFFICULTIES if d["key"] == st.session_state.assessment_difficulty)
    total_questions = len(QUESTION_BANK[domain_key])

    icon_header(domain["icon"], "Assessment overview")
    st.markdown(
        '<div class="ea-body" style="color:var(--color-text-secondary);">'
        'Here is what to expect before you start - you can change your answers at any '
        'point before you submit.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;">
            <div class="ea-icon-badge" style="width:44px;height:44px;">{icon(domain['icon'], 'var(--color-primary)', 22)}</div>
            <div>
                <div class="ea-section" style="font-size:18px;">{domain['name']}</div>
                <div class="ea-small">{domain['desc']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="ea-small">Difficulty</div><div class="ea-section" style="font-size:18px;">{difficulty["name"]}</div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="ea-small">Questions</div><div class="ea-section" style="font-size:18px;">{total_questions}</div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="ea-small">Estimated time</div><div class="ea-section" style="font-size:18px;">~{domain["minutes"]} min</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    message_banner(
        "Before you begin",
        "Each question shows an explanation as soon as you answer it. You can revisit any "
        "question with Previous, Next, or the question map, and change your answer right up "
        "until you submit.",
        kind="info",
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    b1, b2 = st.columns([1, 2])
    with b1:
        if st.button("← Change domain", width="stretch", key="instructions-back"):
            st.session_state.assessment_domain = None
            st.session_state.assessment_difficulty = None
            st.rerun()
    with b2:
        if st.button("Start Assessment →", type="primary", width="stretch", key="instructions-start"):
            st.session_state.assessment_started = True
            st.session_state.assessment_current_q = 0
            st.session_state.assessment_answers = {}
            st.rerun()


# ---------------------------------------------------------------- questions --

def _render_question_flow():
    domain_key = st.session_state.assessment_domain
    domain = next(d for d in ASSESSMENT_DOMAINS if d["key"] == domain_key)
    questions = QUESTION_BANK[domain_key]
    idx = st.session_state.assessment_current_q
    total = len(questions)
    q = questions[idx]
    answers = st.session_state.assessment_answers
    selected = answers.get(q["id"])

    st.markdown(f'<div class="ea-small" style="letter-spacing:.06em;text-transform:uppercase;">{domain["name"]} certification · {st.session_state.assessment_difficulty.title()}</div>', unsafe_allow_html=True)
    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown('<div class="ea-heading">Assessment</div>', unsafe_allow_html=True)
    with top_r:
        st.markdown(f'<div style="text-align:right;padding-top:10px;color:var(--color-text-secondary);">Question {idx + 1} of {total}</div>', unsafe_allow_html=True)
    st.progress((idx + 1) / total)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    answered_count = sum(1 for qq in questions if qq["id"] in answers)
    st.caption(f"{answered_count} of {total} answered - click a number to jump to that question.")
    with st.container(key="assessment-nav-strip"):
        dot_cols = st.columns(total)
        for i, (dot_col, qq) in enumerate(zip(dot_cols, questions)):
            with dot_col:
                is_current = i == idx
                is_answered = qq["id"] in answers
                if is_answered and not is_current:
                    st.markdown(
                        f"<style>.st-key-navdot-{i} .stButton > button {{ "
                        f"background: var(--color-accent-bg); border-color: var(--color-primary); "
                        f"color: var(--color-primary-dark); }}</style>",
                        unsafe_allow_html=True,
                    )
                with st.container(key=f"navdot-{i}"):
                    if st.button(str(i + 1), key=f"navdot-btn-{i}", type="primary" if is_current else "secondary", width="stretch"):
                        st.session_state.assessment_current_q = i
                        st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if selected:
        st.markdown(
            f"<style>[class*=\"st-key-opt-{q['id']}-{selected}\"] {{ border-color: var(--color-primary) !important; "
            f"background: var(--color-accent-bg); }}</style>",
            unsafe_allow_html=True,
        )
    with st.container(border=True):
        st.markdown(f'<div class="ea-body" style="font-weight:600;font-size:18px;">{q["text"]}</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        for opt in q["options"]:
            is_selected = selected == opt["key"]
            css_key = f"opt-{q['id']}-{opt['key']}"
            with st.container(key=css_key):
                dot_class = "current" if is_selected else "pending"
                oc1, oc2 = st.columns([1, 12], vertical_alignment="center")
                with oc1:
                    st.markdown(f'<div class="ea-step-dot {dot_class}">{opt["key"]}</div>', unsafe_allow_html=True)
                with oc2:
                    if st.button(opt["text"], key=f"btn-{css_key}", width="stretch"):
                        answers[q["id"]] = opt["key"]
                        st.rerun()

        if selected:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            is_correct = selected == q["correct"]
            if is_correct:
                message_banner("Correct", q["explanations"][q["correct"]], kind="success")
            else:
                message_banner(f"Not quite - option {selected} is incorrect", q["explanations"][selected], kind="warning")
                message_banner(f"Why {q['correct']} is the right answer", q["explanations"][q["correct"]], kind="info")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("← Previous", width="stretch", disabled=idx == 0, key="q-prev"):
            st.session_state.assessment_current_q -= 1
            st.rerun()
    with nav2:
        is_last = idx == total - 1
        if is_last:
            if st.button("Submit Assessment →", type="primary", width="stretch", disabled=selected is None, key="q-next"):
                unanswered = total - answered_count
                body = (
                    f"You've answered {answered_count} of {total} questions."
                    + (f" {unanswered} question{'s' if unanswered != 1 else ''} will be marked "
                       "incorrect if you submit now." if unanswered else " You're all set.")
                )
                confirm_dialog(
                    "Submit this assessment?", body, "Submit",
                    on_confirm=_submit_current_assessment,
                )
        else:
            if st.button("Next question →", type="primary", width="stretch", disabled=selected is None, key="q-next"):
                st.session_state.assessment_current_q += 1
                st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if st.button("Exit to domain selection", key="switch-domain"):
        st.session_state.assessment_domain = None
        st.session_state.assessment_difficulty = None
        st.session_state.assessment_started = False
        st.rerun()


# ---------------------------------------------------------------- results --

def _submit_current_assessment():
    domain_key = st.session_state.assessment_domain
    questions = QUESTION_BANK[domain_key]
    result = score_assessment(questions, st.session_state.assessment_answers)
    domain = next(item for item in ASSESSMENT_DOMAINS if item["key"] == domain_key)
    result.update(
        {
            "domain_key": domain_key,
            "domain_name": domain["name"],
            "difficulty": st.session_state.assessment_difficulty.title(),
            "submitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
    )
    st.session_state.assessment_result = result
    st.session_state.assessment_history.append(result)
    st.session_state.assessment_submitted = True
    st.session_state.assessment_celebrated = False

_LEVEL_COPY = [
    (80, "Excellent!", "You've demonstrated a strong grasp of the fundamentals."),
    (60, "Good job!", "Solid overall, with a couple of areas worth another look."),
    (0, "Keep practicing!", "The basics are there - a bit more practice will make a real difference."),
]


def _render_results():
    # One-shot celebration: shown only the moment results first appear
    # after a submission, not on every rerun while the results page stays
    # open (eg. expanding the "review answers" section below would
    # otherwise replay it every time). Deliberately not st.balloons() -
    # its colour set is baked into Streamlit itself and can't be
    # inspected or recoloured, so it can't be grep-verified orange-free
    # the way everything else in this restyle can. The hand-drawn
    # illustration below is confetti in the app's own palette, guaranteed.
    if not st.session_state.get("assessment_celebrated"):
        st.session_state.assessment_celebrated = True
        celebration_illustration(size=96)

    result = st.session_state.get("assessment_result")
    domain_key = result["domain_key"] if result else st.session_state.assessment_domain
    domain = next(d for d in ASSESSMENT_DOMAINS if d["key"] == domain_key)
    questions = QUESTION_BANK[domain_key]
    answers = st.session_state.assessment_answers
    if result is None:
        result = score_assessment(questions, answers)
    total = result["total"]
    correct_count = result["correct_count"]
    overall_pct = result["overall_pct"]
    verdict, verdict_sub = next((v, s) for t, v, s in _LEVEL_COPY if overall_pct >= t)

    cat_scores = result["categories"]
    strengths = sorted([c for c in cat_scores if c["pct"] >= 70], key=lambda c: -c["pct"])
    improvements = sorted([c for c in cat_scores if c["pct"] < 70], key=lambda c: c["pct"])

    icon_header("check-circle", f"{domain['name']} · {st.session_state.assessment_difficulty.title()}")
    top_l, top_r = st.columns([2.4, 1])
    with top_l:
        st.markdown(f'<div class="ea-heading">Assessment completed - {verdict}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ea-body" style="color:#6B6478;">{verdict_sub} Review your detailed breakdown below.</div>', unsafe_allow_html=True)
    with top_r:
        # Stacked full-width rather than side-by-side - two short button
        # pairs squeezed into an already-narrow column is what was causing
        # "Download report" to wrap mid-word at tablet widths.
        if st.button("Open reports", key="dl-assessment-report", width="stretch"):
            go_to("reports")
            st.rerun()
        st.button("Share result", type="primary", key="share-assessment-result", width="stretch", disabled=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1.2])
    with c1:
        with st.container(border=True):
            st.markdown('<div class="ea-small" style="text-align:center;letter-spacing:.06em;text-transform:uppercase;">Overall score</div>', unsafe_allow_html=True)
            charts.score_ring(overall_pct, height=200)
            st.markdown(
                f'<div style="text-align:center;"><b>{correct_count}/{total} correct</b>'
                f'<div class="ea-small">Domain: {domain["name"]}</div></div>',
                unsafe_allow_html=True,
            )

    with c2:
        icon_header("trend", "Strengths")
        with st.container(border=True):
            if strengths:
                for s in strengths:
                    progress_bar_card(s["name"], s["pct"])
            else:
                st.caption("None of the categories cleared 70% this attempt - see improvement areas instead.")

    with c3:
        icon_header("alert", "Improvement areas")
        with st.container(border=True):
            if improvements:
                for w in improvements:
                    progress_bar_card(w["name"], w["pct"])
                weakest = improvements[0]
                weakest_q = next(q for q in questions if q["category"] == weakest["name"] and answers.get(q["id"]) != q["correct"])
                why = weakest_q["explanations"][weakest_q["correct"]].removeprefix("Correct. ")
                st.markdown(f"""
                <div class="ea-card" style="background:var(--color-accent-bg);border:none;margin-top:8px;">
                    <div class="ea-card-kicker">Recommended next step</div>
                    <div class="ea-body" style="font-size:14px;">Revisit <b>{weakest['name']}</b>. Key idea to review: {why}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.caption("No weak spots this attempt - every category cleared 70%.")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1:
        with st.container(border=True):
            rc1, rc2 = st.columns([1, 5])
            rc1.markdown(f'<div class="ea-icon-badge">{icon("assessment", "var(--color-primary)")}</div>', unsafe_allow_html=True)
            rc2.markdown('<b>Review answers</b><br/><span class="ea-small">See detailed explanations.</span>', unsafe_allow_html=True)
            st.session_state.setdefault("_show_review", False)
            if st.button("Review answers", key="toggle-review", width="stretch"):
                st.session_state._show_review = not st.session_state._show_review
                st.rerun()
    with r2:
        with st.container(border=True):
            rc1, rc2 = st.columns([1, 5])
            rc1.markdown(f'<div class="ea-icon-badge">{icon("skill_gap", "var(--color-primary)")}</div>', unsafe_allow_html=True)
            rc2.markdown('<b>View skill gap</b><br/><span class="ea-small">Update your learning path.</span>', unsafe_allow_html=True)
            if st.button("View skill gap", key="goto-skillgap", width="stretch"):
                st.session_state.page = "skill_gap"
                st.rerun()
    with r3:
        with st.container(border=True):
            rc1, rc2 = st.columns([1, 5])
            rc1.markdown(f'<div class="ea-icon-badge">{icon("dashboard", "var(--color-primary)")}</div>', unsafe_allow_html=True)
            rc2.markdown('<b>Back to dashboard</b><br/><span class="ea-small">Return to home screen.</span>', unsafe_allow_html=True)
            if st.button("Back to dashboard", key="goto-dashboard", width="stretch"):
                st.session_state.page = "dashboard"
                st.rerun()

    if st.session_state.get("_show_review"):
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        icon_header("assessment", "Answer review")
        for i, q in enumerate(questions, start=1):
            sel = answers.get(q["id"])
            correct = sel == q["correct"]
            with st.expander(f"Q{i}. {q['text']}", expanded=False):
                st.markdown(f"Your answer: **{sel or 'No answer'}** · Correct answer: **{q['correct']}**")
                if correct:
                    message_banner("Correct", q["explanations"][q["correct"]], kind="success")
                elif sel is None:
                    message_banner("No answer recorded", "This unanswered question counted as incorrect.", kind="warning")
                    message_banner(f"Correct answer: {q['correct']}", q["explanations"][q["correct"]], kind="info")
                else:
                    message_banner(f"You chose {sel} - incorrect", q["explanations"][sel], kind="warning")
                    message_banner(f"Correct answer: {q['correct']}", q["explanations"][q["correct"]], kind="info")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.button("Retake this assessment", key="retake-assessment"):
        st.session_state.assessment_submitted = False
        st.session_state.assessment_domain = None
        st.session_state.assessment_difficulty = None
        st.session_state.assessment_started = False
        st.session_state.assessment_current_q = 0
        st.session_state.assessment_answers = {}
        st.session_state.assessment_result = None
        st.session_state._show_review = False
        st.rerun()
