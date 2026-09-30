import streamlit as st

_KIND_CLASS = {
    "success": "ea-badge-success",
    "warning": "ea-badge-warning",
    "error": "ea-badge-error",
    "info": "ea-badge-info",
    "purple": "ea-badge-purple",
    "neutral": "ea-badge-neutral",
}

_PRIORITY_KIND = {
    "High": "error",
    "Medium": "warning",
    "Low": "neutral",
    "Met": "success",
    "Gap": "error",
    "Partial": "warning",
}


def badge_html(text: str, kind: str = "neutral") -> str:
    css_class = _KIND_CLASS.get(kind, "ea-badge-neutral")
    return f'<span class="ea-badge {css_class}">{text}</span>'


def badge(text: str, kind: str = "neutral"):
    st.markdown(badge_html(text, kind), unsafe_allow_html=True)


def priority_badge_html(priority: str) -> str:
    return badge_html(priority, _PRIORITY_KIND.get(priority, "neutral"))
