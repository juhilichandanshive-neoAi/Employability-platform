import streamlit as st
from components.icons import icon


def confirm_dialog(title: str, body: str, confirm_label: str, on_confirm=None):
    def _action():
        if on_confirm:
            on_confirm()
        st.rerun()

    def _dismiss():
        st.rerun()

    @st.dialog(title)
    def _inner():
        st.write(body)
        c1, c2 = st.columns(2)
        c1.button(
            "Keep going",
            width="stretch",
            key="confirm-dialog-cancel",
            on_click=_dismiss,
        )
        c2.button(
            confirm_label,
            type="primary",
            width="stretch",
            key="confirm-dialog-submit",
            on_click=_action,
        )
    _inner()


def success_dialog(title: str, body: str, action_label: str):
    @st.dialog(title)
    def _inner():
        st.markdown(
            f'<div style="display:flex;gap:8px;align-items:center;">'
            f'<span style="color:var(--color-primary);">{icon("check-circle", size=24)}</span>'
            f'<span style="font-size:24px;font-weight:700;">{title}</span></div>',
            unsafe_allow_html=True,
        )
        st.write(body)
        if st.button(action_label, type="primary", width="stretch"):
            st.rerun()
    _inner()
