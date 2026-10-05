"""Applicant activity service interface for EmployaAI."""

from services.db import (
    log_activity,
    get_user_activities,
    get_activity_stats,
)

__all__ = [
    "log_activity",
    "get_user_activities",
    "get_activity_stats",
]
