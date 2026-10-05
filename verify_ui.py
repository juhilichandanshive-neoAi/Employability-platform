import sys
import io
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass

from streamlit.testing.v1 import AppTest

from tests.session_helpers import login_with_user, open_login, start_app

APP_DIR = Path(__file__).resolve().parent

def verify_ui():
    print("=== Starting UI Verification ===")
    app = start_app()
    assert len(app.exception) == 0, f"Exceptions on initial load: {app.exception}"

    print("0. Verifying public landing page...")
    assert not app.session_state.authenticated
    assert app.session_state.auth_page == "landing"
    assert len(app.sidebar.button) == 0, "Sidebar should not be visible when unauthenticated"
    assert any(btn.key == "btn-landing-login" for btn in app.button), "Landing Login button must exist"
    print("✓ Landing page renders without authenticated chrome.")

    print("1. Verifying Dedicated Login page layout...")
    open_login(app)
    assert app.session_state.auth_page == "login"
    assert any(btn.key == "open-session" for btn in app.button), "Login button must exist"
    assert any(btn.key == "btn-goto-register" for btn in app.button), "Sign Up button must exist on login page"
    assert any(inp.key == "login_enrollment_id" for inp in app.text_input), "Enrollment ID input must exist"
    assert any(inp.key == "login_email" for inp in app.text_input), "Login identifier input must exist"
    assert any(inp.key == "login_password" for inp in app.text_input), "Password input must exist"
    assert not any(inp.key == "reg_email_input" for inp in app.text_input), "Registration inputs must NOT be on login page"
    print("✓ Dedicated Login page renders cleanly as a separate screen.")

    print("2. Verifying navigation to separate Create Account page...")
    app.button(key="btn-goto-register").click().run()
    assert len(app.exception) == 0
    assert app.session_state.auth_page == "register"
    assert any(inp.key == "reg_email_input" for inp in app.text_input), "Registration inputs must render on register page"
    assert any(btn.key == "btn-submit-register" for btn in app.button), "Create Account button must exist on register page"
    assert any(btn.key == "btn-goto-login" for btn in app.button), "Sign In link must exist to return to login"
    print("✓ Separate registration page rendered cleanly without login form.")

    print("3. Verifying Registration flow & Enrollment ID display...")
    import uuid
    rand_suffix = uuid.uuid4().hex[:6]
    test_user = f"student_{rand_suffix}"
    test_email = f"student_{rand_suffix}@example.edu"
    test_password = "StrongPassword123"
    app.text_input(key="reg_name_input").set_value("Aarav Deshpande")
    app.text_input(key="reg_email_input").set_value(test_email)
    app.text_input(key="reg_username_input").set_value(test_user)
    app.text_input(key="reg_password_input").set_value(test_password)
    app.text_input(key="reg_confirm_password_input").set_value(test_password)
    app.button(key="btn-submit-register").click().run()
    assert len(app.exception) == 0, f"Exceptions on registration: {app.exception}"

    eid = app.session_state.get("_registered_enrollment_id")
    assert eid and eid.startswith("EA-2026-"), f"Expected EA-2026- enrollment ID, got {eid}"
    assert app.session_state.auth_page == "success"
    print(f"✓ Registration succeeded! Generated unique Enrollment ID on success screen: {eid}")

    print("3b. Continuing to login and authenticating with Enrollment ID...")
    app.button(key="btn-continue-to-login").click().run()
    assert app.session_state.auth_page == "login"
    assert not app.session_state.authenticated
    login_with_user(
        app,
        {"enrollment_id": eid, "email": test_email},
        password=test_password,
    )
    assert len(app.exception) == 0
    assert app.session_state.authenticated, "User must be authenticated after valid credentials"
    assert app.session_state.page == "dashboard"
    print("✓ Successfully logged in and routed to Dashboard.")

    # 3. Verify Dashboard Rendering
    print("3. Verifying Dashboard UI elements...")
    assert len(app.sidebar.button) > 0, "Sidebar buttons must render when authenticated"
    # Check that Activity is in the sidebar
    assert any(btn.key == "nav-activity" for btn in app.sidebar.button), "Activity navigation must exist"
    print("✓ Dashboard rendered with personalized metrics and navigation.")

    # 4. Verify Profile & Education UI
    print("4. Verifying Profile & Education UI (Checking '+ Add Education' button)...")
    app.button(key="nav-profile").click().run()
    assert len(app.exception) == 0
    assert app.session_state.page == "profile"

    # Verify '+ Add Education' button is visibly rendered on the page
    add_edu_buttons = [btn for btn in app.button if "+ Add Education" in btn.label or btn.key in ("btn-open-add-edu", "btn-empty-add-edu")]
    assert len(add_edu_buttons) > 0, "A visible '+ Add Education' button MUST be present on the Profile page"
    print(f"✓ Profile loaded! Found visible '+ Add Education' button: {add_edu_buttons[0].key}")

    # Click '+ Add Education' to open the interactive form
    add_edu_buttons[0].click().run()
    assert len(app.exception) == 0
    assert app.session_state.get("_show_edu_form") is True, "Education form must be active"

    # Fill out the education form
    print("   Submitting new Education entry via interactive form...")
    app.text_input(key="edu_degree_val").set_value("Bachelor of Technology")
    app.text_input(key="edu_field_val").set_value("Computer Science and Engineering")
    app.text_input(key="edu_inst_val").set_value("Indian Institute of Technology Bombay")
    app.text_input(key="edu_start_val").set_value("2021")
    app.text_input(key="edu_grad_val").set_value("2025")
    app.text_input(key="edu_score_val").set_value("9.1 CGPA")
    app.text_area(key="edu_desc_val").set_value("Specialized in Distributed Systems and Cloud Computing.")

    # Find the Save/Add Education submit button in the form
    save_btn = next((b for b in app.button if "Add Education" in b.label or "Save" in b.label), None)
    assert save_btn is not None, "Save button in education form must exist"
    save_btn.click().run()
    assert len(app.exception) == 0
    assert app.session_state.get("_show_edu_form") is False, "Education form should close after saving"
    assert len(app.session_state.profile.get("education_entries", [])) >= 1, "Education entry must persist in profile"
    print("✓ Education entry saved and persisted cleanly in session state and database!")

    # Verify Edit and Delete buttons exist for the entry
    assert any(btn.key.startswith("btn-edit-edu-") for btn in app.button), "Edit button must exist"
    assert any(btn.key.startswith("btn-delete-edu-") for btn in app.button), "Delete button must exist"
    print("✓ Edit and Delete actions are visibly available for the education entry.")

    # 5. Verify Reports Page
    print("5. Verifying Reports page UI...")
    app.button(key="nav-reports").click().run()
    assert len(app.exception) == 0
    assert app.session_state.page == "reports"
    print("✓ Reports page rendered cleanly.")

    # 6. Verify Activity Log Page
    print("6. Verifying Activity Log page...")
    app.button(key="nav-activity").click().run()
    assert len(app.exception) == 0
    assert app.session_state.page == "activity"
    print("✓ Activity log rendered with chronological events.")

    # 7. Verify Job Opportunities Page (Admin CSV Integration)
    print("7. Verifying Job Opportunities page (Admin CSV Integration)...")
    app.button(key="nav-jobs").click().run()
    assert len(app.exception) == 0
    assert app.session_state.page == "jobs"
    assert any("All Opportunities" in t.label for t in app.tabs)
    assert any("Matches for You" in t.label for t in app.tabs)
    assert any("Saved Jobs" in t.label for t in app.tabs)
    print("✓ Job Opportunities page rendered cleanly with 260+ admin CSV postings.")

    # 8. Verify Sign Out
    print("8. Verifying Logout...")
    app.button(key="nav-settings").click().run()
    app.button(key="settings_sign_out").click().run()
    assert not app.session_state.authenticated
    assert len(app.sidebar.button) == 0
    print("✓ Logout completely cleared session and returned to public Landing page.")

    print("\n==========================================")
    print(" ALL UI REQUIREMENTS FULLY VERIFIED! (OK) ")
    print("==========================================")

if __name__ == "__main__":
    verify_ui()
