"""
Small "delight" components added in the fun restyle (24 Sep): a streak/
level chip, achievement badges, a mascot illustration, and an empty-state
block. These are purely motivational and decorative - they use the two new
fun accent colours (teal, cyan) rather than the success/warning/error
status palette, per the brief's rule that fun colours never carry status
meaning.

Illustrations live in assets/images/ as hand-drawn SVG files (purple/
violet/pink/teal only, no external image hosts) and are read from disk
relative to this file's own location, not the working directory, so they
resolve the same way regardless of where `streamlit run` is launched from.
"""

import os
import streamlit as st
from components.icons import icon

_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images")


def read_svg(filename: str) -> str:
    """Reads one file from assets/images/ as raw SVG text, for the
    (uncommon) case a screen needs to compose it directly into a larger
    markdown block rather than using one of the fixed-wrapper functions
    below (eg. login.py embedding the hero illustration inside its own
    gradient card)."""
    with open(os.path.join(_IMAGES_DIR, filename), encoding="utf-8") as f:
        return f.read()


def streak_chip(days: int):
    st.markdown(
        f'<span class="ea-streak-chip">{icon("zap", "var(--color-fun-teal)", size=15)} {days}-day streak</span>',
        unsafe_allow_html=True,
    )


def level_chip(level: int, title: str):
    st.markdown(
        f'<span class="ea-level-chip">{icon("star", "var(--color-fun-cyan)", size=13)} Level {level} · {title}</span>',
        unsafe_allow_html=True,
    )


def achievement_badges(achievements):
    """One tile per achievement dict ({key, label, icon, unlocked, status})
    in a row of equal columns. Every tile has the identical structure and
    size - icon, name, status line - so only the visual state (teal border
    when unlocked, dimmed when locked) differs between them."""
    with st.container(key="cards-achievements"):
        cols = st.columns(len(achievements))
        for col, a in zip(cols, achievements):
            with col:
                state = "unlocked" if a["unlocked"] else "locked"
                st.markdown(f"""
                <div class="ea-achievement {state}" title="{a['label']} - {a['status']}">
                    <div class="ea-achievement-icon">{icon(a['icon'], 'currentColor', size=20)}</div>
                    <div class="ea-achievement-name">{a['label']}</div>
                    <div class="ea-achievement-status">{a['status']}</div>
                </div>
                """, unsafe_allow_html=True)


def mascot(size: int = 64, alt: str = "EmployaAI mascot"):
    svg = read_svg("mascot.svg")
    st.markdown(
        f'<div class="ea-mascot" role="img" aria-label="{alt}" style="width:{size}px;height:{size}px;">{svg}</div>',
        unsafe_allow_html=True,
    )


def celebration_illustration(size: int = 88):
    svg = read_svg("celebration.svg")
    st.markdown(
        f'<div role="img" aria-label="Celebration graphic" style="width:{size}px;margin:0 auto;">{svg}</div>',
        unsafe_allow_html=True,
    )


def empty_state(title: str, body: str):
    """A friendly "nothing here yet" block - illustration, short title,
    one line of plain-language explanation. Use in place of a bare
    st.info()/blank table wherever a screen has no data to show yet."""
    svg = read_svg("empty_state.svg")
    st.markdown(f"""
    <div class="ea-empty-state">
        {svg}
        <div class="ea-section" style="margin-top:12px;">{title}</div>
        <div class="ea-small" style="margin-top:4px;">{body}</div>
    </div>
    """, unsafe_allow_html=True)
