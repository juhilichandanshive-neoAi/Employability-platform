"""Render HTML through Streamlit without leaking raw tags as text.

Indented snippets passed to ``st.markdown`` are treated as Markdown code
blocks, so closing tags like ``</div>`` appear on screen. Flatten first,
then render with ``unsafe_allow_html``.
"""

from __future__ import annotations

import streamlit as st


def flatten_html(markup: str) -> str:
    """Collapse indented HTML into a single Markdown-safe fragment."""
    if markup is None:
        return ""
    lines = [line.strip() for line in str(markup).splitlines() if line.strip()]
    return " ".join(lines)


def render_html(markup: str) -> None:
    compact = flatten_html(markup)
    if compact:
        st.markdown(compact, unsafe_allow_html=True)

