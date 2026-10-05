"""Authentication service interface for EmployaAI."""

from services.auth import (
    register_user,
    authenticate_user,
    generate_enrollment_id,
    hash_password,
    verify_password,
    validate_registration_input,
)
from services.db import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    get_user_by_enrollment_id,
)

__all__ = [
    "register_user",
    "authenticate_user",
    "generate_enrollment_id",
    "hash_password",
    "verify_password",
    "validate_registration_input",
    "get_user_by_id",
    "get_user_by_email",
    "get_user_by_username",
    "get_user_by_enrollment_id",
]
