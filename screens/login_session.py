"""Public EmployAI screens: landing, split login, registration, and success."""

from __future__ import annotations

import base64
from html import escape as html_escape
from pathlib import Path

import streamlit as st

from components.footer import render_footer
from components.fun import read_svg
from components.html import render_html
from services.db import (
    add_education_entry,
    authenticate_user,
    get_user_profile,
    register_user,
    save_user_profile,
)
from services.session import load_user_session


@st.cache_data
def get_campus_hero_base64() -> str:
    hero_path = Path(__file__).resolve().parent.parent / "assets" / "images" / "campus_hero.png"
    if hero_path.exists():
        with open(hero_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


def render() -> None:
    st.session_state.setdefault("auth_page", "landing")
    st.session_state.setdefault("_registered_enrollment_id", None)
    st.session_state.setdefault("_registered_user", None)

    if st.session_state.get("_registered_enrollment_id") and st.session_state.auth_page not in (
        "success",
        "login",
    ):
        st.session_state.auth_page = "success"

    page = st.session_state.auth_page
    _inject_public_styles(page)

    if page == "success":
        _render_success_page()
        render_footer("landing")
    elif page == "register":
        _render_register_page()
        render_footer("landing")
    elif page == "login":
        _render_login_page()
        render_footer("landing")
    else:
        _render_landing_page()
        render_footer("landing")


def _inject_public_styles(page: str) -> None:
    hero_b64 = get_campus_hero_base64()
    campus_bg = ""
    if hero_b64:
        campus_bg = f"""
        .stApp {{
            background-image:
                linear-gradient(rgba(18, 10, 36, 0.28), rgba(18, 10, 36, 0.42)),
                url("data:image/png;base64,{hero_b64}") !important;
            background-size: cover !important;
            background-position: center center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
            min-height: 100vh !important;
            animation: ea-bg-drift 48s ease-in-out infinite alternate;
        }}
        """

    st.markdown(
        f"""
        <style>
        {campus_bg}
        html, body, .stApp {{
            overflow-x: hidden !important;
        }}
        [data-testid="stHeader"] {{ background: transparent !important; }}
        [data-testid="stToolbar"] {{ right: 0.5rem !important; }}
        [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{
            display: none !important;
        }}
        [data-testid="stAppViewContainer"] > .main {{
            display: flex !important;
            flex-direction: column !important;
            min-height: 100vh !important;
            background: transparent !important;
        }}
        html {{
            scroll-behavior: smooth !important;
        }}
        .ea-top-nav-link {{
            color: rgba(255, 255, 255, 0.88) !important;
            text-decoration: none !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            padding: 8px 14px !important;
            border-radius: 8px !important;
            transition: color 0.18s ease, background 0.18s ease !important;
            display: inline-block !important;
        }}
        .ea-top-nav-link:hover {{
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.12) !important;
        }}
        .main .block-container {{
            max-width: 100% !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            padding-top: 0.8rem !important;
            padding-bottom: 320px !important;
            min-height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            box-sizing: border-box !important;
        }}
        /* Remove Streamlit's default bottom bar gap */
        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"] {{
            display: none !important;
        }}
        /* Ensure no gap below the app viewport */
        .stApp {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}
        [data-testid="stAppViewContainer"] {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}
        @keyframes ea-bg-drift {{
            from {{ background-position: 48% 50%; }}
            to {{ background-position: 52% 46%; }}
        }}
        @keyframes ea-fade-up {{
            from {{ opacity: 0; transform: translateY(14px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes ea-reveal {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes ea-float {{
            0% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
            100% {{ transform: translateY(0); }}
        }}
        @keyframes ea-pop {{
            from {{ transform: scale(0.88); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}
        .ea-orb {{
            position: fixed; pointer-events: none; border-radius: 50%;
            background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.14);
            backdrop-filter: blur(10px); animation: ea-float 9s ease-in-out infinite;
            z-index: 0;
        }}
        @media (prefers-reduced-motion: reduce) {{
            .stApp {{ animation: none !important; }}
            .ea-orb, .ea-fade-up-card, .ea-login-hero-copy {{ animation: none !important; }}
        }}

        /* ---- Input visibility fix (Crisp light background, dark typed text) ---- */
        .stTextInput input,
        .stTextInput > div > div > input,
        [data-testid="stTextInput"] input,
        [data-baseweb="input"] input,
        [class*="st-key-reg-card-box"] input,
        [class*="st-key-login-panel"] input,
        input[type="text"],
        input[type="password"],
        input[type="email"] {{
            background: rgba(255, 255, 255, 0.96) !important;
            color: #1f1633 !important;
            -webkit-text-fill-color: #1f1633 !important;
            border-radius: 11px !important;
            border: 1.5px solid rgba(196, 181, 253, 0.55) !important;
            font-size: 14.5px !important;
            font-weight: 500 !important;
            height: 44px !important;
            padding: 8px 14px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06) !important;
        }}
        [data-baseweb="input"] {{
            background: rgba(255, 255, 255, 0.96) !important;
            border-radius: 11px !important;
            border: none !important;
        }}
        [data-baseweb="base-input"] {{
            background: transparent !important;
        }}
        .stTextInput input::placeholder,
        [data-testid="stTextInput"] input::placeholder,
        [class*="st-key-reg-card-box"] input::placeholder,
        [class*="st-key-login-panel"] input::placeholder,
        input::placeholder {{
            color: #8f83a8 !important;
            -webkit-text-fill-color: #8f83a8 !important;
            opacity: 1 !important;
            font-weight: 400 !important;
        }}
        .stTextInput input:focus,
        [data-testid="stTextInput"] input:focus,
        [class*="st-key-reg-card-box"] input:focus,
        [class*="st-key-login-panel"] input:focus,
        input:focus {{
            color: #1f1633 !important;
            -webkit-text-fill-color: #1f1633 !important;
            border-color: #7C3AED !important;
            box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.25) !important;
            background: #FFFFFF !important;
            outline: none !important;
        }}
        .stTextInput input:-webkit-autofill,
        .stTextInput input:-webkit-autofill:hover, 
        .stTextInput input:-webkit-autofill:focus,
        .stTextInput input:-webkit-autofill:active {{
            -webkit-text-fill-color: #1f1633 !important;
            -webkit-box-shadow: 0 0 0px 1000px #FFFFFF inset !important;
            box-shadow: 0 0 0px 1000px #FFFFFF inset !important;
            transition: background-color 5000s ease-in-out 0s;
            caret-color: #1f1633 !important;
        }}
        [data-testid="stTextInput"] button {{
            color: #4B3F72 !important;
            background: transparent !important;
            border: none !important;
        }}
        [data-testid="stTextInput"] button svg {{
            fill: #4B3F72 !important;
            stroke: #4B3F72 !important;
        }}
        [data-testid="stTextInput"] label,
        [data-testid="stWidgetLabel"] p,
        [class*="st-key-reg-card-box"] [data-testid="stWidgetLabel"] p,
        [class*="st-key-login-panel"] [data-testid="stWidgetLabel"] p {{
            font-size: 13.5px !important;
            font-weight: 600 !important;
            color: #FFFFFF !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.45) !important;
            letter-spacing: .01em !important;
        }}
        [data-testid="stToggle"] label p {{
            color: #EDE7FA !important;
            font-size: 13px !important;
            font-weight: 500 !important;
        }}

        /* ---- Landing / register glass ---- */
        .st-key-reg-card-box, [class*="st-key-reg-card-box"],
        .st-key-success-card-box, [class*="st-key-success-card-box"] {{
            background: rgba(35, 20, 60, 0.50) !important;
            backdrop-filter: blur(18px) !important;
            -webkit-backdrop-filter: blur(18px) !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            border-radius: 20px !important;
            padding: 32px 34px !important;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.30) !important;
            animation: ea-fade-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
            margin: 16px auto 320px auto !important;
            max-width: 820px !important;
        }}
        [class*="st-key-reg-card-box"] button[kind="primary"],
        [class*="st-key-success-card-box"] button[kind="primary"],
        [class*="st-key-landing-hero-actions"] button[kind="primary"],
        [class*="st-key-login-panel"] button[kind="primary"] {{
            background: linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%) !important;
            color: #FFFFFF !important; font-weight: 700 !important;
            border: none !important; border-radius: 12px !important;
            box-shadow: 0 6px 18px rgba(124, 58, 237, 0.45) !important;
            transition: transform .2s ease, box-shadow .2s ease !important;
        }}
        [class*="st-key-reg-card-box"] button[kind="primary"]:hover,
        [class*="st-key-success-card-box"] button[kind="primary"]:hover,
        [class*="st-key-landing-hero-actions"] button[kind="primary"]:hover,
        [class*="st-key-login-panel"] button[kind="primary"]:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 10px 24px rgba(124, 58, 237, 0.55) !important;
        }}
        [class*="st-key-reg-card-box"] button[kind="secondary"],
        [class*="st-key-landing-hero-actions"] button[kind="secondary"],
        [class*="st-key-login-panel"] button[kind="secondary"] {{
            background: rgba(255,255,255,0.10) !important;
            border: 1px solid rgba(255,255,255,0.22) !important;
            color: #FFFFFF !important; font-weight: 600 !important;
            border-radius: 12px !important;
        }}
        div[class*="st-key-btn-nav-"] button,
        div[class*="st-key-btn-landing-"] button {{
            background: rgba(255,255,255,0.10) !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            color: #FFFFFF !important;
            border-radius: 10px !important;
        }}

        /* ---- Split login (reference) ---- */
        .st-key-login-shell, [class*="st-key-login-shell"] {{
            max-width: 1020px;
            margin: 20px auto 320px auto !important;
            width: calc(100% - 32px);
        }}
        [class*="st-key-login-shell"] [data-testid="stHorizontalBlock"] {{
            gap: 0 !important;
        }}
        .st-key-login-panel, [class*="st-key-login-panel"] {{
            background: rgba(20, 16, 32, 0.70) !important;
            backdrop-filter: blur(18px) !important;
            -webkit-backdrop-filter: blur(18px) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-right: none !important;
            border-radius: 22px 0 0 22px !important;
            padding: 36px 34px 28px 34px !important;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35) !important;
            min-height: 600px !important;
            animation: ea-fade-up .45s ease both;
        }}
        .st-key-login-visual, [class*="st-key-login-visual"] {{
            background: linear-gradient(155deg, rgba(139, 92, 246, 0.85) 0%, rgba(109, 40, 217, 0.90) 100%) !important;
            backdrop-filter: blur(18px) !important;
            -webkit-backdrop-filter: blur(18px) !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            border-left: none !important;
            border-radius: 0 22px 22px 0 !important;
            padding: 36px 28px 20px 28px !important;
            min-height: 600px !important;
            box-shadow: 0 20px 60px rgba(109, 77, 224, .30) !important;
            overflow: hidden !important;
            animation: ea-fade-up .55s ease both;
        }}
        .ea-login-hero-copy h1 {{
            color: #FFFFFF; font-size: 40px; font-weight: 800; line-height: 1.15;
            margin: 8px 0 10px 0; letter-spacing: -0.03em;
            animation: ea-reveal .7s ease both;
        }}
        .ea-login-hero-copy p {{
            color: rgba(255,255,255,.88); font-size: 15px; margin: 0 0 12px 0;
        }}
        .ea-login-illustration svg {{ width: 100%; max-height: 420px; height: auto; }}
        @media (max-width: 900px) {{
            .st-key-login-panel, [class*="st-key-login-panel"] {{
                border-radius: 22px 22px 0 0 !important;
                border-right: 1px solid rgba(255, 255, 255, 0.15) !important;
                border-bottom: none !important;
                min-height: 0 !important;
                padding: 24px 20px !important;
            }}
            .st-key-login-visual, [class*="st-key-login-visual"] {{
                border-radius: 0 0 22px 22px !important;
                border-left: 1px solid rgba(255, 255, 255, 0.18) !important;
                border-top: none !important;
                min-height: 0 !important;
                padding: 24px 20px !important;
            }}
            .ea-login-hero-copy h1 {{ font-size: 30px !important; }}
            .ea-login-illustration svg {{ max-height: 260px; }}
        }}
        @media (max-width: 640px) {{
            .main .block-container {{ padding-left: 0 !important; padding-right: 0 !important; }}
            .st-key-login-shell, [class*="st-key-login-shell"] {{ width: calc(100% - 16px); }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _go(page: str) -> None:
    st.session_state.auth_page = page
    st.rerun()


def _render_public_nav(active: str) -> None:
    render_html("""
    <div class="ea-orb" style="width:120px;height:120px;top:12%;left:6%;"></div>
    <div class="ea-orb" style="width:80px;height:80px;top:28%;right:10%;animation-delay:1.4s;"></div>
    <div class="ea-orb" style="width:54px;height:54px;bottom:22%;left:18%;animation-delay:2.2s;"></div>
    """)
    brand, _, c_login, c_signup = st.columns([2.4, 3.4, 1.2, 1.6], gap="small")
    with brand:
        render_html("""
        <div style="display:flex;align-items:center;gap:10px;padding:6px 0 6px 16px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#8B5CF6,#6D28D9);
                display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:18px;">E</div>
            <div style="font-weight:800;font-size:20px;color:#fff;letter-spacing:-0.02em;">EmployAI</div>
        </div>
        """)
    with c_login:
        if st.button("Login", key="btn-landing-login", width="stretch"):
            _go("login")
    with c_signup:
        if st.button("Create Account", key="btn-landing-register", type="primary", width="stretch"):
            _go("register")
    _ = active


def _render_landing_page() -> None:
    _render_public_nav("landing")

    # ── Hero section with floating feature bubbles ──
    render_html("""
    <div id="home" style="position:relative;max-width:1200px;margin:20px auto 0 auto;padding:16px 24px 0 24px;min-height:420px;">

        <!-- Floating feature bubbles -->
        <div class="ea-hero-bubbles">
            <!-- Skill Assessment bubble (top-left) -->
            <div class="ea-bubble" style="top:10px;left:28%;">
                <div class="ea-bubble-icon" style="background:rgba(139,92,246,0.25);">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M11 20V4M18 20v-7"/></svg>
                </div>
                <div>
                    <div class="ea-bubble-title">Skill Assessment</div>
                    <div class="ea-bubble-sub">Know Your Strengths</div>
                </div>
            </div>

            <!-- Resume Insights bubble (center) -->
            <div class="ea-bubble" style="top:90px;left:44%;">
                <div class="ea-bubble-icon" style="background:rgba(139,92,246,0.25);">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3.5h7l4 4V19a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 6 19V5A1.5 1.5 0 0 1 7 3.5Z"/><path d="M14 3.5V8h4"/><path d="M9 12h6M9 15.5h6"/></svg>
                </div>
                <div>
                    <div class="ea-bubble-title">Resume Insights</div>
                    <div class="ea-bubble-sub">Get AI-powered feedback</div>
                </div>
            </div>

            <!-- Skill Growth Plan bubble (right) -->
            <div class="ea-bubble" style="top:40px;right:12%;">
                <div class="ea-bubble-icon" style="background:rgba(139,92,246,0.25);">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 16 6-6 4 4 8-9"/><path d="M15 5h6v6"/></svg>
                </div>
                <div>
                    <div class="ea-bubble-title">Skill Growth Plan</div>
                    <div class="ea-bubble-sub">Personalized roadmap</div>
                </div>
            </div>

            <!-- Industry Insights bubble (bottom-right) -->
            <div class="ea-bubble" style="top:160px;right:8%;">
                <div class="ea-bubble-icon" style="background:rgba(139,92,246,0.25);">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 8v4l3 3"/></svg>
                </div>
                <div>
                    <div class="ea-bubble-title">Industry Insights</div>
                    <div class="ea-bubble-sub">Stay ahead with trends</div>
                </div>
            </div>

            <!-- Dotted connecting path SVG -->
            <svg class="ea-bubble-path" viewBox="0 0 800 220" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M200 40 Q320 30 380 100 Q440 170 560 80 Q620 40 720 170" stroke="rgba(255,255,255,0.25)" stroke-width="2" stroke-dasharray="8 6" fill="none"/>
                <circle cx="380" cy="100" r="4" fill="rgba(167,139,250,0.6)"/>
                <circle cx="560" cy="80" r="4" fill="rgba(167,139,250,0.6)"/>
            </svg>
        </div>

        <!-- Hero text -->
        <div style="position:relative;z-index:2;animation:ea-fade-up .6s ease both;max-width:440px;">
            <h1 style="color:#FFFFFF;font-size:clamp(38px,5.5vw,60px);font-weight:800;letter-spacing:-0.03em;
                margin:18px 0 6px 0;line-height:1.08;text-shadow:0 8px 28px rgba(0,0,0,.35);">
                EmployAI
            </h1>
            <div style="display:inline-block;padding:5px 14px;border-radius:999px;background:rgba(255,255,255,0.10);
                border:1px solid rgba(255,255,255,0.18);color:#E9E0FF;font-size:11px;font-weight:700;letter-spacing:.1em;margin-bottom:14px;">
                AI-POWERED EMPLOYABILITY PLATFORM
            </div>
            <p style="color:#F0EAFF;font-size:clamp(15px,1.8vw,18px);font-weight:500;margin:0;max-width:400px;line-height:1.55;">
                Assess your skills, close the gaps, and build
                a career roadmap that employers actually
                recognise.
            </p>
        </div>
    </div>

    <style>
    .ea-hero-bubbles { position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;z-index:1; }
    .ea-bubble {
        position:absolute;
        display:flex;align-items:center;gap:10px;
        background:rgba(255,255,255,0.12);
        backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
        border:1px solid rgba(255,255,255,0.20);
        border-radius:16px;padding:10px 16px;
        animation:ea-float 7s ease-in-out infinite;
        pointer-events:auto;
    }
    .ea-bubble:nth-child(2) { animation-delay:1.2s; }
    .ea-bubble:nth-child(3) { animation-delay:2.4s; }
    .ea-bubble:nth-child(4) { animation-delay:0.8s; }
    .ea-bubble-icon {
        width:38px;height:38px;border-radius:10px;
        display:flex;align-items:center;justify-content:center;flex-shrink:0;
    }
    .ea-bubble-title { color:#FFFFFF;font-size:13.5px;font-weight:700;line-height:1.3; }
    .ea-bubble-sub { color:rgba(255,255,255,0.70);font-size:11px;font-weight:500; }
    .ea-bubble-path {
        position:absolute;top:0;left:0;width:100%;height:100%;
        pointer-events:none;opacity:0.7;
    }
    @media (max-width:900px) {
        .ea-hero-bubbles { display:none; }
    }
    </style>
    """)

    # ── 6 feature cards section ──
    features = [
        ("1", "Skill Assessment",
         "Take a structured assessment that scores your readiness across core technical domains.",
         '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5.5" y="4" width="13" height="17" rx="2"/><path d="M9 3.5h6a1 1 0 0 1 1 1V6H8V4.5a1 1 0 0 1 1-1Z"/><path d="m9 13 2 2 4-4.5"/></svg>'),
        ("2", "Personalized Roadmap",
         "See exactly which skills employers expect for your target role — and where you stand today.",
         '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8"/><path d="m8.5 12.5 2.3 2.3 4.7-5.1"/></svg>'),
        ("3", "Learning Path",
         "Follow a clear learning path built from your gaps, not a generic course list.",
         '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5Z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H13v16h5.5a1.5 1.5 0 0 0 1.5-1.5Z"/></svg>'),
        ("4", "Job & Internship Opportunities",
         "Browse verified openings from the EmployAI industry dataset and match them to your skills.",
         '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><path d="M2 13h20"/></svg>'),
        ("5", "Progress Tracking",
         "Watch your score, assessments, and activity evolve as you improve.",
         '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 16 6-6 4 4 8-9"/><path d="M15 5h6v6"/></svg>'),
        ("6", "Reports & Insights",
         "Generate shareable PDF reports with your enrollment identity, scores, and recommendations.",
         '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M11 20V4M18 20v-7"/></svg>'),
    ]
    feature_cards = ""
    for num, title, desc, icon_svg in features:
        feature_cards += f"""
        <div class="ea-feature-card">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px;">
                <div style="width:32px;height:32px;border-radius:9px;background:rgba(139,92,246,0.5);
                    color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;">{num}</div>
                <div style="width:40px;height:40px;border-radius:12px;background:rgba(139,92,246,0.25);
                    display:flex;align-items:center;justify-content:center;">{icon_svg}</div>
            </div>
            <div style="color:#FFFFFF;font-size:16.5px;font-weight:700;margin-bottom:8px;line-height:1.3;">{title}</div>
            <div style="color:rgba(255,255,255,0.78);font-size:13.5px;line-height:1.55;">{desc}</div>
        </div>"""

    render_html(f"""
    <div id="features" style="max-width:1200px;margin:28px auto 320px auto;padding:0 24px;">
        <div class="ea-features-grid">{feature_cards}</div>
    </div>
    <style>
    .ea-features-grid {{
        display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;
    }}
    .ea-feature-card {{
        background:rgba(255,255,255,0.08);
        backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
        border:1px solid rgba(255,255,255,0.16);
        border-radius:18px;padding:24px 22px;
        box-shadow:0 10px 28px rgba(0,0,0,0.18);
        transition:transform .22s ease, box-shadow .22s ease;
        animation:ea-fade-up .5s ease both;
    }}
    .ea-feature-card:nth-child(2) {{ animation-delay:.08s; }}
    .ea-feature-card:nth-child(3) {{ animation-delay:.16s; }}
    .ea-feature-card:nth-child(4) {{ animation-delay:.24s; }}
    .ea-feature-card:nth-child(5) {{ animation-delay:.32s; }}
    .ea-feature-card:nth-child(6) {{ animation-delay:.40s; }}
    .ea-feature-card:hover {{ transform:translateY(-5px);box-shadow:0 18px 40px rgba(0,0,0,0.30) !important; }}
    @media (max-width:900px) {{
        .ea-features-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)) !important; }}
    }}
    @media (max-width:560px) {{
        .ea-features-grid {{ grid-template-columns:1fr !important; }}
    }}
    </style>
    """)


def _render_login_page() -> None:
    _render_public_nav("login")
    with st.container(key="login-shell"):
        # We use a custom CSS rule in the injected styles to force gap: 0 here,
        # making the left and right panels fuse into a single split card.
        left, right = st.columns([1, 1.05])
        with left:
            with st.container(key="login-panel"):
                render_html("""
                <div style="margin-bottom:28px;">
                    <div style="font-size:28px;font-weight:800;color:#FFFFFF;letter-spacing:-0.02em;">Login</div>
                    <div style="color:#B8B8C2;font-size:14px;margin-top:6px;">Enter your account details</div>
                </div>
                """)

                login_enrollment_id = st.text_input(
                    "Enrollment ID",
                    key="login_enrollment_id",
                    placeholder="Enter your enrollment ID",
                )
                login_identifier = st.text_input(
                    "Username / Email",
                    key="login_email",
                    placeholder="Enter your username or email",
                )
                show_pwd = st.toggle("Show password", key="toggle_show_pwd")
                login_password = st.text_input(
                    "Password",
                    type="default" if show_pwd else "password",
                    key="login_password",
                    placeholder="Enter your password",
                )

                if not st.session_state.get("_show_forgot"):
                    if st.button("Forgot Password?", key="btn-forgot-password"):
                        st.session_state["_show_forgot"] = True
                        st.rerun()

                if st.session_state.get("_show_forgot"):
                    with st.form("reset_password_form", clear_on_submit=True):
                        render_html("""
                        <div style="background:rgba(255,255,255,0.06);border-left:3px solid #A78BFA;padding:12px;margin:8px 0 16px 0;border-radius:0 8px 8px 0;">
                            <div style="color:#E9E0FF;font-size:13px;line-height:1.5;margin-bottom:8px;">
                                <b>Reset Password</b><br/>
                                Enter your Enrollment ID and Username/Email to verify your identity, then choose a new password.
                            </div>
                        </div>
                        """)
                        reset_eid = st.text_input("Enrollment ID *", key="reset_eid")
                        reset_ident = st.text_input("Username / Email *", key="reset_ident")
                        reset_pwd = st.text_input("New Password *", type="password", key="reset_pwd")
                        
                        r_col1, r_col2 = st.columns(2)
                        with r_col1:
                            submit_reset = st.form_submit_button("Reset Password", type="primary", use_container_width=True)
                        with r_col2:
                            cancel_reset = st.form_submit_button("Cancel", use_container_width=True)
                            
                    if cancel_reset:
                        st.session_state["_show_forgot"] = False
                        st.session_state.pop("_login_error", None)
                        st.rerun()
                        
                    if submit_reset:
                        if not reset_eid.strip() or not reset_ident.strip() or not reset_pwd:
                            st.error("All fields are required to reset your password.")
                        elif len(reset_pwd) < 6:
                            st.error("Password must be at least 6 characters long.")
                        else:
                            from services.db import update_user_password
                            success = update_user_password(reset_ident, reset_eid, reset_pwd)
                            if success:
                                st.success("Password reset successfully! You can now log in.")
                                st.session_state["_show_forgot"] = False
                                st.session_state.pop("_login_error", None)
                                # Force a rerun so the form disappears
                            else:
                                st.error("Verification failed. Invalid Enrollment ID or Username/Email.")

                if st.session_state.get("_login_error"):
                    st.error(st.session_state._login_error)

                if st.button("Login", type="primary", width="stretch", key="open-session"):
                    _handle_login(login_enrollment_id, login_identifier, login_password)

                render_html("""
                <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;
                    margin-top:22px;padding-top:8px;">
                    <div style="color:#A3A3AD;font-size:13.5px;">Don't have an account?</div>
                </div>
                """)
                if st.button("Sign Up", key="btn-goto-register"):
                    st.session_state.pop("_login_error", None)
                    _go("register")
                if st.button("← Back to Home", key="btn-login-home"):
                    _go("landing")

        with right:
            with st.container(key="login-visual"):
                try:
                    illustration = read_svg("login_hero.svg")
                except OSError:
                    illustration = ""
                render_html(f"""
                <div class="ea-login-hero-copy">
                    <h1>Welcome to<br>EmployAI</h1>
                    <p>Login to access your account</p>
                </div>
                <div class="ea-login-illustration" role="img" aria-label="Students collaborating on an employability profile">
                    {illustration}
                </div>
                """)


def _handle_login(enrollment_id: str, identifier: str, password: str) -> None:
    clean_eid = (enrollment_id or "").strip()
    clean_ident = (identifier or "").strip()
    if not clean_eid or not clean_ident or not password:
        st.session_state["_login_error"] = (
            "Enrollment ID, username/email, and password are all required."
        )
        st.rerun()
        return

    user = authenticate_user(clean_ident, password, clean_eid)
    if user is None:
        st.session_state["_login_error"] = "Invalid Enrollment ID, username/email, or password."
        st.rerun()
        return

    st.session_state.pop("_login_error", None)
    st.session_state.authenticated = True
    st.session_state.page = "dashboard"
    load_user_session(user["user_id"], user["enrollment_id"])
    st.rerun()


def _render_register_page() -> None:
    _render_public_nav("register")
    _, col, _ = st.columns([0.6, 3.2, 0.6])
    with col:
        with st.container(key="reg-card-box"):
            render_html("""
            <div style="margin-bottom:18px;">
                <div style="font-weight:800;font-size:26px;color:#FFFFFF;letter-spacing:-0.02em;">
                    Create Your EmployAI Account
                </div>
                <div style="color:#EDE7FA;font-size:14px;margin-top:6px;line-height:1.5;">
                    Fill in your details. A unique Enrollment ID will be generated after your account is created.
                </div>
            </div>
            """)
            if st.session_state.get("_reg_error"):
                st.error(st.session_state._reg_error)

            c1, c2 = st.columns(2)
            with c1:
                reg_name = st.text_input("Full Name *", key="reg_name_input", placeholder="Your full name")
            with c2:
                reg_username = st.text_input("Username *", key="reg_username_input", placeholder="Choose a username")

            c3, c4 = st.columns(2)
            with c3:
                reg_email = st.text_input("Email *", key="reg_email_input", placeholder="you@college.edu")
            with c4:
                reg_phone = st.text_input("Phone Number", key="reg_phone_input", placeholder="Optional")

            reg_show_pwd = st.toggle("Show passwords", key="toggle_reg_show_pwd")
            c5, c6 = st.columns(2)
            with c5:
                reg_password = st.text_input(
                    "Password *",
                    type="default" if reg_show_pwd else "password",
                    key="reg_password_input",
                    placeholder="Min. 6 characters",
                )
            with c6:
                reg_confirm = st.text_input(
                    "Confirm Password *",
                    type="default" if reg_show_pwd else "password",
                    key="reg_confirm_password_input",
                    placeholder="Re-enter password",
                )

            c7, c8 = st.columns(2)
            with c7:
                reg_college = st.text_input("College / University", key="reg_college_input", placeholder="Institution name")
            with c8:
                reg_course = st.text_input("Course", key="reg_course_input", placeholder="e.g. B.Tech Computer Science")

            reg_year = st.text_input("Year / Semester", key="reg_year_input", placeholder="e.g. Year 3 / Semester 6")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("Create Account", type="primary", width="stretch", key="btn-submit-register"):
                _execute_registration(
                    name=reg_name,
                    username=reg_username,
                    email=reg_email,
                    phone=reg_phone,
                    password=reg_password,
                    confirm=reg_confirm,
                    college=reg_college,
                    course=reg_course,
                    year=reg_year,
                )

            if st.button("← Back to Login", width="stretch", key="btn-goto-login"):
                st.session_state.pop("_reg_error", None)
                _go("login")


def _execute_registration(
    name: str,
    username: str,
    email: str,
    phone: str,
    password: str,
    confirm: str,
    college: str,
    course: str,
    year: str,
) -> None:
    clean_email = (email or "").strip()
    clean_username = (username or "").strip()
    clean_name = (name or "").strip()
    if not clean_name or not clean_username or not clean_email or not password:
        st.session_state["_reg_error"] = "Please fill in full name, username, email, and password."
        st.rerun()
        return
    if password != confirm:
        st.session_state["_reg_error"] = "Passwords do not match. Please retype carefully."
        st.rerun()
        return
    if "@" not in clean_email or "." not in clean_email.split("@")[-1]:
        st.session_state["_reg_error"] = "Please enter a valid email address."
        st.rerun()
        return

    try:
        new_user = register_user(clean_email, clean_username, password, clean_name)
        user_id = new_user["user_id"]
        profile = get_user_profile(user_id)
        if (phone or "").strip():
            profile["phone"] = phone.strip()
        if (course or "").strip():
            profile["degree"] = course.strip()
        if (year or "").strip():
            profile["semester"] = year.strip()
        save_user_profile(user_id, profile)
        if (college or "").strip() or (course or "").strip():
            add_education_entry(
                user_id,
                {
                    "institution": (college or "").strip() or "University",
                    "degree": (course or "").strip() or "Undergraduate",
                    "field_of_study": "",
                    "grad_year": (year or "").strip(),
                    "score": "",
                },
            )
        st.session_state.pop("_reg_error", None)
        st.session_state["_registered_enrollment_id"] = new_user["enrollment_id"]
        st.session_state["_registered_user"] = new_user
        st.session_state.auth_page = "success"
        st.rerun()
    except ValueError as err:
        st.session_state["_reg_error"] = str(err)
        st.rerun()
    except Exception:
        st.session_state["_reg_error"] = "Account creation could not be completed. Please try again."
        st.rerun()


def _render_success_page() -> None:
    enrollment_id = st.session_state.get("_registered_enrollment_id") or "EA-2026-PENDING"
    user = st.session_state.get("_registered_user") or {}
    student_name = user.get("name") or user.get("username") or "Student"
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        with st.container(key="success-card-box"):
            render_html(f"""
            <div style="text-align:center;padding:8px 4px;">
                <div style="width:58px;height:58px;border-radius:50%;background:linear-gradient(135deg,#10B981,#059669);
                    margin:0 auto 14px auto;display:flex;align-items:center;justify-content:center;
                    box-shadow:0 8px 24px rgba(16,185,129,.4);animation:ea-pop .45s ease both;">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"
                        stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                </div>
                <div style="font-size:24px;font-weight:800;color:#FFFFFF;margin-bottom:8px;">Account Created Successfully!</div>
                <div style="color:#EEE8FA;font-size:15px;line-height:1.6;margin-bottom:18px;">
                    Welcome to EmployAI, <b>{html_escape(student_name)}</b>.
                </div>
                <div style="color:#E8E0F8;font-size:14px;margin-bottom:8px;">Your Enrollment ID is:</div>
                <div style="background:rgba(124,58,237,0.22);border:2px dashed #C4B5FD;border-radius:16px;
                    padding:18px 14px;margin-bottom:16px;">
                    <div style="font-size:28px;font-family:ui-monospace,monospace;font-weight:800;color:#FFFFFF;
                        letter-spacing:.08em;">{html_escape(enrollment_id)}</div>
                </div>
                <div style="color:#F3EEFF;font-size:13.5px;line-height:1.55;">
                    Please save this Enrollment ID.<br>You will need it whenever you log in.
                </div>
            </div>
            """)
            if st.button("Continue to Login", type="primary", width="stretch", key="btn-continue-to-login"):
                st.session_state["login_enrollment_id"] = enrollment_id
                st.session_state["login_email"] = user.get("username") or user.get("email", "")
                st.session_state.auth_page = "login"
                st.session_state.pop("_registered_enrollment_id", None)
                st.session_state.pop("_registered_user", None)
                st.rerun()
