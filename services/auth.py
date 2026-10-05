"""Google OIDC (Streamlit ``st.login``) plus local session fallback."""

from __future__ import annotations

from typing import Any

import streamlit as st

from services.integration import empty_profile

PLACEHOLDER_SECRET_VALUES = {
    "",
    "xxx",
    "your-google-oauth-client-id",
    "your-google-oauth-client-secret",
    "replace-with-a-long-random-string",
}

GOOGLE_SETUP_MESSAGE = (
    "Google sign-in is temporarily unavailable. Please try again or use email sign-in."
)


def _secret_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    try:
        return dict(value)
    except Exception:
        return {}


import os


def auth_secrets() -> dict[str, Any]:
    res: dict[str, Any] = {}
    try:
        secrets = st.secrets
        if secrets and "auth" in secrets:
            res = _secret_mapping(secrets.get("auth"))
    except Exception:
        pass

    # Environment variable fallback for flexible deployment
    if not res.get("client_id") and os.environ.get("GOOGLE_CLIENT_ID"):
        res["client_id"] = os.environ.get("GOOGLE_CLIENT_ID")
    if not res.get("client_secret") and os.environ.get("GOOGLE_CLIENT_SECRET"):
        res["client_secret"] = os.environ.get("GOOGLE_CLIENT_SECRET")
    if not res.get("cookie_secret") and os.environ.get("AUTH_COOKIE_SECRET"):
        res["cookie_secret"] = os.environ.get("AUTH_COOKIE_SECRET")
    if not res.get("server_metadata_url") and os.environ.get("AUTH_SERVER_METADATA_URL"):
        res["server_metadata_url"] = os.environ.get("AUTH_SERVER_METADATA_URL")
    if not res.get("redirect_uri") and os.environ.get("AUTH_REDIRECT_URI"):
        res["redirect_uri"] = os.environ.get("AUTH_REDIRECT_URI")

    return res


def _non_placeholder(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text or text in PLACEHOLDER_SECRET_VALUES:
        return None
    return text


def google_auth_configured() -> bool:
    auth = auth_secrets()
    nested = _secret_mapping(auth.get("google"))
    client_id = _non_placeholder(auth.get("client_id")) or _non_placeholder(nested.get("client_id"))
    client_secret = _non_placeholder(auth.get("client_secret")) or _non_placeholder(
        nested.get("client_secret")
    )
    cookie_secret = _non_placeholder(auth.get("cookie_secret"))
    metadata = _non_placeholder(auth.get("server_metadata_url")) or _non_placeholder(
        nested.get("server_metadata_url")
    )
    redirect_uri = _non_placeholder(auth.get("redirect_uri"))
    return bool(client_id and client_secret and cookie_secret and metadata and redirect_uri)


def oidc_user_logged_in() -> bool:
    user = getattr(st, "user", None)
    if user is None:
        return False
    try:
        return bool(getattr(user, "is_logged_in", False))
    except Exception:
        return False


def oidc_user_info() -> dict[str, Any]:
    user = getattr(st, "user", None)
    if user is None:
        return {}
    try:
        if hasattr(user, "to_dict"):
            info = dict(user.to_dict())
        else:
            info = dict(user)
    except Exception:
        info = {}
    for key in ("name", "email", "given_name", "family_name", "picture"):
        if key not in info:
            try:
                value = user[key]
            except Exception:
                value = getattr(user, key, None)
            if value:
                info[key] = value
    return info


def display_name_from_oidc(info: dict[str, Any]) -> str:
    name = str(info.get("name") or "").strip()
    if name:
        return name
    given = str(info.get("given_name") or "").strip()
    family = str(info.get("family_name") or "").strip()
    combined = " ".join(part for part in (given, family) if part)
    if combined:
        return combined
    email = str(info.get("email") or "").strip()
    return email.split("@")[0] if email else ""


def apply_oidc_user_to_session(info: dict[str, Any] | None = None) -> None:
    payload = info if info is not None else oidc_user_info()
    profile = st.session_state.get("profile") or empty_profile()
    email = str(payload.get("email") or "").strip()
    name = display_name_from_oidc(payload)
    if email:
        profile["email"] = email
    if name and not str(profile.get("name") or "").strip():
        profile["name"] = name
    st.session_state.profile = profile
    st.session_state.authenticated = True
    st.session_state.auth_provider = "google"
    if not st.session_state.get("page"):
        st.session_state.page = "dashboard"


def start_google_login() -> str | None:
    """Start Streamlit OIDC login. Return a user-facing error, or None."""
    if not google_auth_configured():
        return GOOGLE_SETUP_MESSAGE
    st.session_state.pop("_user_signed_out", None)
    auth = auth_secrets()
    try:
        if "google" in auth and isinstance(auth["google"], dict):
            try:
                st.login("google")
            except Exception:
                st.login()
        else:
            st.login()
    except Exception as exc:
        return f"Google sign-in could not start: {exc}"
    return None


def logout_identity() -> None:
    if not oidc_user_logged_in():
        return
    try:
        st.logout()
    except Exception:
        pass
