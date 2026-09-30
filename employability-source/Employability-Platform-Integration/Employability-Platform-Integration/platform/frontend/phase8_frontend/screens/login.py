import streamlit as st
from components.fun import read_svg


def render():
    if "login_mode" not in st.session_state:
        st.session_state.login_mode = "sign_in"

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
                <div class="ea-small" style="color:rgba(255,255,255,.75);margin-top:24px;">BUILT FOR FINAL-YEAR STUDENTS</div>
                <div class="ea-heading" style="color:#fff;margin-top:8px;">Find out how job-ready you actually are 🚀</div>
                <div class="ea-body" style="color:rgba(255,255,255,.85);margin-top:12px;">
                    We compare your profile against what employers are actually asking for right now,
                    tell you which skills you're short on, and give you a plan to fix them.
                </div>
                <div role="img" aria-label="A rocket climbing above a rising growth chart" style="max-width:280px;margin:16px auto 0 auto;">{hero_svg}</div>
            </div>
            <div>
                <div style="background:rgba(255,255,255,.12);border-radius:12px;padding:14px 16px;margin-bottom:12px;">
                    <div class="ea-small" style="color:rgba(255,255,255,.75);">Students gain this much, on average</div>
                    <div class="ea-subhead" style="color:#fff;">+14 points</div>
                </div>
                <div class="ea-small" style="color:rgba(255,255,255,.75);">
                    412 students so far &nbsp;·&nbsp; 58 certifications &nbsp;·&nbsp; 2 domains
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        if st.session_state.login_mode == "sign_in":
            _render_sign_in()
        else:
            _render_create_account()

        st.caption("This is a static frontend preview — sign-in is a stand-in, no real auth or backend is wired up yet.")


def _render_sign_in():
    st.markdown('<div class="ea-subhead">Welcome back</div>', unsafe_allow_html=True)
    st.markdown('<div class="ea-body" style="color:#6B6478;margin-bottom:16px;">Sign in and pick up where you left off.</div>', unsafe_allow_html=True)

    st.text_input("Email address", value="aarav.d@college.edu", key="login_email")
    st.text_input("Password", type="password", value="", placeholder="••••••••••", key="login_password")
    st.checkbox("Keep me signed in", value=True)

    if st.button("Sign in", type="primary", width="stretch"):
        st.session_state.authenticated = True
        st.session_state.page = "dashboard"
        st.rerun()

    st.markdown('<div style="text-align:center;color:#8A82A6;margin:12px 0;">or</div>', unsafe_allow_html=True)
    st.button("Continue with Google", width="stretch")

    st.markdown('<div style="text-align:center;margin-top:12px;color:#6B6478;">First time here?</div>', unsafe_allow_html=True)
    if st.button("Create an account", key="go-create-account", width="stretch"):
        st.session_state.login_mode = "create_account"
        st.rerun()


def _render_create_account():
    st.markdown('<div class="ea-subhead">Create your account</div>', unsafe_allow_html=True)
    st.markdown('<div class="ea-body" style="color:#6B6478;margin-bottom:16px;">Set up your profile, including the ID you\'ll use to sign in.</div>', unsafe_allow_html=True)

    st.text_input("Full name", placeholder="Aarav Deshpande", key="signup_name")
    st.text_input("College email address", placeholder="aarav.d@college.edu", key="signup_email")

    user_id = st.text_input(
        "Choose your User ID", placeholder="e.g. aarav.d",
        key="signup_user_id",
        help="This is how you'll sign in and how recruiters see you referenced in reports. Letters, numbers, and dots only — can't be changed later.",
    )
    if user_id:
        clean = user_id.strip().lower()
        valid = clean.replace(".", "").replace("_", "").isalnum() and len(clean) >= 4
        if valid:
            st.caption(f"employa.ai/{clean} is available")
        else:
            st.caption("Use at least 4 characters — letters, numbers, dots, or underscores only.")

    c1, c2 = st.columns(2)
    c1.text_input("Password", type="password", key="signup_password")
    c2.text_input("Confirm password", type="password", key="signup_password_confirm")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Create account", type="primary", width="stretch", key="submit-create-account"):
        st.session_state.authenticated = True
        st.session_state.page = "dashboard"
        st.rerun()

    if st.button("← Back to sign in", key="back-to-signin", width="stretch"):
        st.session_state.login_mode = "sign_in"
        st.rerun()
