from contextlib import contextmanager

import streamlit as st
from components.badges import badge_html
from components.icons import icon


def icon_header(icon_key, title, right_html=None):
    """Icon-in-circle + bold title, the header pattern every card section
    uses now instead of a bare heading - keeps every page's section
    headers looking like one design language instead of plain text."""
    right = f'<div style="margin-left:auto;">{right_html}</div>' if right_html else ""
    st.markdown(f"""
    <div class="ea-header-row">
        <div class="ea-icon-badge">{icon(icon_key, 'var(--color-primary)')}</div>
        <div class="ea-section" style="font-size:18px;font-weight:700;">{title}</div>
        {right}
    </div>
    """, unsafe_allow_html=True)


def metric_card(label, value, delta=None, kicker=None):
    delta_html = ""
    if delta:
        delta_html = f'<div style="margin-top:6px;">{badge_html(delta, "success" if str(delta).startswith("+") else "neutral")}</div>'
    kicker_html = f'<div class="ea-card-kicker">{kicker}</div>' if kicker else ""
    st.markdown(f"""
    <div class="ea-card">
        {kicker_html}
        <div class="ea-small">{label}</div>
        <div class="ea-big-number" style="margin-top:4px;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def score_hero_card(score: int, band: str, vs_cohort: str, to_ready_points: int):
    st.markdown(f"""
    <div class="ea-card-hero">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div class="ea-small" style="color:rgba(255,255,255,.8);">Employability score</div>
            {badge_html(band, "neutral")}
        </div>
        <div class="ea-big-number" style="font-size:56px;margin-top:8px;">{score}</div>
        <div class="ea-small" style="color:rgba(255,255,255,.85);">out of 100</div>
        <div class="ea-small" style="color:rgba(255,255,255,.85);margin-top:10px;">
            vs batch average <b style="color:#fff;">{vs_cohort}</b><br/>
            to job-ready · <b style="color:#fff;">{to_ready_points} points</b>
        </div>
    </div>
    """, unsafe_allow_html=True)


def progress_bar_card(label, pct, right_label=None, tone="scale"):
    """Every progress bar in the app fills with the same purple, at a depth
    that scales with the value - strength/completeness reads through shade
    by default. The badge or text next to it still carries any pass/fail
    meaning, same as the design system's rule that colour is never the
    only signal."""
    if tone == "scale":
        if pct >= 75:
            fill = "var(--color-primary)"
        elif pct >= 45:
            fill = "rgba(124, 58, 237, 0.55)"
        else:
            fill = "rgba(124, 58, 237, 0.28)"
    else:
        fill = {
            "success": "var(--color-success)",
            "warning": "var(--color-warning)",
            "error": "var(--color-error)",
            "muted": "#D8D4E0",
        }.get(tone, "var(--color-primary)")
    right = right_label if right_label is not None else f"{pct}%"
    st.markdown(f"""
    <div style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:14px;font-weight:500;margin-bottom:6px;">
            <span>{label}</span><span style="color:#6B6478;">{right}</span>
        </div>
        <div class="ea-progress-track">
            <div class="ea-progress-fill" style="width:{pct}%;background:{fill};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def progress_label(pct: int) -> str:
    """A short, encouraging label for a completion percentage - one of the
    small "delight" touches from the fun restyle brief. Used next to a
    progress bar that represents overall completion (profile, assessment),
    not every mini skill-bar row, so it doesn't turn into noise."""
    if pct >= 100:
        return "All done"
    if pct >= 75:
        return "Almost there!"
    if pct >= 45:
        return "Halfway there!"
    if pct > 0:
        return "Just getting started"
    return "Let's begin!"


def message_banner(title, body, kind="info"):
    """Stands in for st.info/st.warning/st.error, which render in
    Streamlit's own fixed blue/amber/red and ignore the app's theme
    entirely - this keeps every inline message on the app's own status
    palette (green/pink/red/violet) instead."""
    styles = {
        "success": ("#DCFCE7", "#166534", "check-circle"),
        "warning": ("#FDF2F8", "#9D174D", "alert"),
        "error": ("#FEE2E2", "#991B1B", "alert"),
        "info": ("#EDE9FE", "#5B21B6", "bell"),
    }
    bg, text, icon_key = styles.get(kind, styles["info"])
    st.markdown(f"""
    <div style="background:{bg};color:{text};border-radius:var(--radius);padding:14px 16px;margin-bottom:12px;display:flex;gap:10px;align-items:flex-start;">
        <div style="flex-shrink:0;margin-top:1px;">{icon(icon_key, text)}</div>
        <div>
            <div style="font-weight:600;">{title}</div>
            <div style="font-size:14px;margin-top:2px;">{body}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title, subtitle=None, right_html=None, with_right_col=False):
    """The one page-title block every screen should use, instead of each
    page hand-rolling its own heading + subtitle markdown - keeps title
    hierarchy and subtitle colour identical everywhere. Pages that need a
    real widget (a button, a selectbox) in the top-right corner rather
    than static right_html text pass with_right_col=True and get the
    Streamlit column back to render into themselves."""
    subtitle_html = f'<div class="ea-body" style="color:var(--color-text-secondary);margin-top:4px;">{subtitle}</div>' if subtitle else ""
    left, right = st.columns([3, 1], vertical_alignment="center")
    with left:
        st.markdown(f'<div style="padding-bottom:8px;"><div class="ea-heading">{title}</div>{subtitle_html}</div>', unsafe_allow_html=True)
    if with_right_col:
        return right
    with right:
        if right_html:
            st.markdown(f'<div style="text-align:right;padding-top:8px;">{right_html}</div>', unsafe_allow_html=True)
    return None


@contextmanager
def panel(key, icon_key=None, title=None, caption=None, kind="panel"):
    """One card container for every grouped card/panel in the app. Inside a
    row keyed "equal-*" the panels of every column stretch to the same
    height and share top/bottom edges (see styles.css). The header lives
    inside the panel, so a panel with a caption and one without still start
    their content at the same place relative to the card edge.

    kind="pcard" additionally pins the panel's last element (a button or
    button row) to the bottom edge; kind="pcard-hero" is the same on the
    brand gradient."""
    with st.container(key=f"{kind}-{key}"):
        if title:
            icon_header(icon_key, title)
        if caption:
            st.caption(caption)
        yield
