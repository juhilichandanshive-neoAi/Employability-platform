"""Helpers for Streamlit AppTest sessions that require a real authenticated user."""

from __future__ import annotations

import uuid
from pathlib import Path

from streamlit.testing.v1 import AppTest

from services.db import register_user

APP_DIR = Path(__file__).resolve().parents[1]
TEST_PASSWORD = "ValidPass456!"


def start_app(timeout: int = 30) -> AppTest:
    return AppTest.from_file(str(APP_DIR / "app.py"), default_timeout=timeout).run()


def open_login(app: AppTest) -> AppTest:
    app.button(key="btn-landing-login").click().run()
    return app


def register_test_user(name: str = "Flow Student") -> dict:
    token = uuid.uuid4().hex[:8]
    return register_user(
        f"flow_{token}@example.com",
        f"flow_{token}",
        TEST_PASSWORD,
        name,
    )


def login_with_user(app: AppTest, user: dict, password: str = TEST_PASSWORD) -> AppTest:
    if not any(btn.key == "open-session" for btn in app.button):
        open_login(app)
    app.text_input(key="login_enrollment_id").set_value(user["enrollment_id"])
    app.text_input(key="login_email").set_value(user["email"])
    app.text_input(key="login_password").set_value(password)
    app.button(key="open-session").click().run()
    return app


def authenticated_app(timeout: int = 30) -> tuple[AppTest, dict]:
    user = register_test_user()
    app = start_app(timeout)
    login_with_user(app, user)
    return app, user
