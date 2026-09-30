import streamlit as st

from components.fun import read_svg
from services.integration import empty_profile


def render():
    st.session_state.setdefault("login_mode", "sign_in")
    left, right = st.columns([1, 1], gap="large")
    with left:
        hero_svg = read_svg("login_hero.svg")
        st.markdown(f"""
        <div class="ea-card-hero" style="min-height:520px;display:flex;flex-direction:column;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:28px;height:28px;border-radius:8px;background:rgba(255,255,255,.2);
                    display:flex;align-items:center;justify-content:center;font-weight:700;">E</div>
                    <span style="font-weight:600;">EmployaAI</span>
                </div>
                <div class="ea-small" style="color:rgba(255,255,255,.75);margin-top:24px;">BUILT FOR STUDENTS</div>
                <div class="ea-heading" style="color:#fff;margin-top:8px;">Build an employability profile</div>
                <div class="ea-body" style="color:rgba(255,255,255,.85);margin-top:12px;">
                    Review your assessment results and compare the skills you record with a bundled job-requirements snapshot.
                </div>
                <div role="img" aria-label="Employability platform illustration" style="max-width:280px;margin:16px auto 0 auto;">{hero_svg}</div>
            </div>
            <div class="ea-small" style="color:rgba(255,255,255,.75);">
                Session-only demo · no live job feed · no persistent account
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        if st.session_state.login_mode == "sign_in":
            _render_session_entry()
        else:
            _render_profile_setup()
        st.caption(
            "Local demo only. It does not verify identity, request a password, or create a persistent account."
        )


def _render_session_entry():
    st.markdown('<div class="ea-subhead">Open a session</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ea-body" style="color:#6B6478;margin-bottom:16px;">Enter your email if you want it saved in your session profile.</div>',
        unsafe_allow_html=True,
    )
    email = st.text_input("Email address", key="login_email")
    st.caption("No password is requested or stored.")
    if st.button("Open session", type="primary", width="stretch", key="open-session"):
        profile = st.session_state.get("profile") or empty_profile()
        if email.strip():
            profile["email"] = email.strip()
        st.session_state.profile = profile
        st.session_state.authenticated = True
        st.session_state.page = "dashboard"
        st.rerun()

    st.markdown('<div style="text-align:center;color:#8A82A6;margin:12px 0;">or</div>', unsafe_allow_html=True)
    st.button("Continue with Google", width="stretch", disabled=True)
    st.caption("Google sign-in is not connected.")
    st.markdown('<div style="text-align:center;margin-top:12px;color:#6B6478;">First time here?</div>', unsafe_allow_html=True)
    if st.button("Create a session profile", key="go-create-account", width="stretch"):
        st.session_state.login_mode = "create_account"
        st.rerun()


def _render_profile_setup():
    st.markdown('<div class="ea-subhead">Create a session profile</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ea-body" style="color:#6B6478;margin-bottom:16px;">Your information remains in this session and is not sent to an account service.</div>',
        unsafe_allow_html=True,
    )
    st.text_input("Full name", key="signup_name")
    st.text_input("Email address", key="signup_email")
    if st.button("Start session", type="primary", width="stretch", key="submit-create-account"):
        profile = st.session_state.get("profile") or empty_profile()
        profile["name"] = st.session_state.get("signup_name", "").strip()
        profile["email"] = st.session_state.get("signup_email", "").strip()
        st.session_state.profile = profile
        st.session_state.profile_saved = True
        st.session_state.authenticated = True
        st.session_state.page = "dashboard"
        st.rerun()

    if st.button("← Back to session entry", key="back-to-signin", width="stretch"):
        st.session_state.login_mode = "sign_in"
        st.rerun()