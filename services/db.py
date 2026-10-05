"""
SQLite Database and Data Persistence Layer for EmployaAI.

Provides:
- User registration and password hashing (bcrypt with PBKDF2 fallback)
- Unique Enrollment ID generation (EA-2026-XXXXXX)
- User profile persistence with full data isolation
- Multi-entry Education CRUD (Add, Edit, Delete, List)
- Applicant Activity history logging
- Assessment attempt history and question history persistence
- Report generation history
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import random
import secrets
import sqlite3
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Try importing bcrypt, fallback to hashlib PBKDF2-HMAC-SHA256
try:
    import bcrypt

    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

try:
    from utils.paths import get_db_path, STORAGE_DIR
    DB_PATH = get_db_path()
    DB_DIR = DB_PATH.parent
except Exception:
    DB_DIR = Path(__file__).resolve().parents[1] / "storage"
    DB_PATH = DB_DIR / "employability.db"


def get_db_connection() -> sqlite3.Connection:
    """Get a SQLite database connection with row factory configured."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create all required tables if they don't already exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                enrollment_id TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                last_login_at TEXT
            )
            """
        )

        # Profiles table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT DEFAULT '',
                target_role TEXT DEFAULT 'Cloud Solutions Architect',
                track TEXT DEFAULT '',
                semester TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                degree TEXT DEFAULT '',
                cgpa REAL,
                github TEXT DEFAULT '',
                linkedin TEXT DEFAULT '',
                languages TEXT DEFAULT '',
                resume_filename TEXT,
                resume_size INTEGER,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Education entries table (Supports multi-entry with full fields)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS education (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                degree TEXT NOT NULL,
                field_of_study TEXT DEFAULT '',
                institution TEXT NOT NULL,
                start_year TEXT DEFAULT '',
                grad_year TEXT DEFAULT '',
                score TEXT DEFAULT '',
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Skills table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS skills (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                level INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Certifications table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS certifications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                provider TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Projects table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Internships table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS internships (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                organization TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Assessment attempts table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS assessment_attempts (
                attempt_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                domain_key TEXT NOT NULL,
                domain_name TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                overall_pct REAL NOT NULL,
                correct_count INTEGER NOT NULL,
                total INTEGER NOT NULL,
                submitted_at TEXT NOT NULL,
                result_json TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Question history for non-repetition
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS question_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                domain_key TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question_ids_json TEXT NOT NULL,
                attempt_id TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Applicant activities table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL,
                metadata_json TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Reports table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                score REAL,
                size_bytes INTEGER,
                created_at TEXT NOT NULL,
                sections_json TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Saved jobs table (isolated per user)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_jobs (
                user_id TEXT NOT NULL,
                job_id INTEGER NOT NULL,
                saved_at TEXT NOT NULL,
                PRIMARY KEY (user_id, job_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        conn.commit()


# ----------------------------------------------------------------- Hashing --

def hash_password(password: str) -> str:
    """Hash password using bcrypt if installed, otherwise PBKDF2-HMAC-SHA256."""
    if not password:
        raise ValueError("Password cannot be empty")
    if HAS_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return "bcrypt$" + hashed.decode("utf-8")
    else:
        salt = secrets.token_hex(16)
        iterations = 260000
        key = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
        )
        return f"pbkdf2_sha256${iterations}${salt}${key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plain password against the stored hash safely."""
    if not password or not password_hash:
        return False
    try:
        if password_hash.startswith("bcrypt$"):
            if not HAS_BCRYPT:
                return False
            raw_hash = password_hash[7:].encode("utf-8")
            return bcrypt.checkpw(password.encode("utf-8"), raw_hash)
        elif password_hash.startswith("pbkdf2_sha256$"):
            parts = password_hash.split("$")
            if len(parts) != 4:
                return False
            iterations = int(parts[1])
            salt = parts[2]
            stored_key = parts[3]
            computed_key = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
            )
            return hmac.compare_digest(computed_key.hex(), stored_key)
        return False
    except Exception:
        return False


# ----------------------------------------------------------- Enrollment ID --

def generate_enrollment_id(year: int = 2026) -> str:
    """Generate a unique Enrollment ID format: EA-2026-XXXXXX."""
    chars = string.ascii_uppercase + string.digits
    # Exclude ambiguous characters like 0, O, 1, I
    clean_chars = "".join(c for c in chars if c not in "0O1I")
    suffix = "".join(secrets.choice(clean_chars) for _ in range(6))
    return f"EA-{year}-{suffix}"


def get_unique_enrollment_id() -> str:
    """Ensure generated Enrollment ID does not collide in the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for _ in range(100):
            candidate = generate_enrollment_id()
            cursor.execute("SELECT 1 FROM users WHERE enrollment_id = ?", (candidate,))
            if cursor.fetchone() is None:
                return candidate
    # Fallback to high entropy hex
    return f"EA-2026-{secrets.token_hex(4).upper()}"


# ------------------------------------------------------------- User & Auth --

def register_user(
    email: str, username: str, password: str, name: str = ""
) -> dict[str, Any]:
    """Register a new user account with secure password hashing and unique enrollment ID.

    Returns dict with user details and enrollment_id, or raises ValueError.
    """
    clean_email = email.strip().lower()
    clean_username = username.strip().lower()

    if not clean_email or "@" not in clean_email or "." not in clean_email.split("@")[-1]:
        raise ValueError("Please provide a valid email address.")
    if not clean_username or len(clean_username) < 3:
        raise ValueError("Username must be at least 3 characters long.")
    if any(c.isspace() for c in clean_username):
        raise ValueError("Username cannot contain spaces.")
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check existing email
        cursor.execute("SELECT id FROM users WHERE email = ?", (clean_email,))
        if cursor.fetchone() is not None:
            raise ValueError("An account with this email address already exists.")

        # Check existing username
        cursor.execute("SELECT id FROM users WHERE username = ?", (clean_username,))
        if cursor.fetchone() is not None:
            raise ValueError("This username is already taken. Please choose another.")

        user_id = f"usr_{secrets.token_hex(8)}"
        enrollment_id = get_unique_enrollment_id()
        pw_hash = hash_password(password)
        now_iso = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            INSERT INTO users (id, email, username, password_hash, enrollment_id, created_at, last_login_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, clean_email, clean_username, pw_hash, enrollment_id, now_iso, now_iso),
        )

        display_name = name.strip() or clean_username.title()
        cursor.execute(
            """
            INSERT INTO profiles (user_id, name, updated_at)
            VALUES (?, ?, ?)
            """,
            (user_id, display_name, now_iso),
        )

        conn.commit()

    # Log initial activity
    log_activity(
        user_id,
        "account_created",
        "Account created",
        f"Joined EmployaAI with Enrollment ID {enrollment_id}.",
    )

    return {
        "id": user_id,
        "user_id": user_id,
        "email": clean_email,
        "username": clean_username,
        "enrollment_id": enrollment_id,
        "name": display_name,
    }


def authenticate_user(
    identifier: str, password: str, enrollment_id_check: str = ""
) -> dict[str, Any] | None:
    """Authenticate a user via email or username and password.

    Optional enrollment_id_check for returning user identity verification.
    """
    clean_ident = identifier.strip().lower()
    if not clean_ident or not password:
        return None

    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, email, username, password_hash, enrollment_id
            FROM users
            WHERE email = ? OR username = ?
            """,
            (clean_ident, clean_ident),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        if not verify_password(password, row["password_hash"]):
            return None

        # If user supplied enrollment ID verification, check it
        if enrollment_id_check and enrollment_id_check.strip().upper() != row["enrollment_id"].upper():
            return None

        user_id = row["id"]
        now_iso = datetime.now(timezone.utc).isoformat()
        cursor.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now_iso, user_id))
        conn.commit()

        # Fetch profile display name
        cursor.execute("SELECT name FROM profiles WHERE user_id = ?", (user_id,))
        p_row = cursor.fetchone()
        display_name = (p_row["name"] if p_row and p_row["name"] else row["username"]).strip()

    log_activity(user_id, "login", "Logged in", "Signed in to EmployaAI session.")

    return {
        "user_id": user_id,
        "email": row["email"],
        "username": row["username"],
        "enrollment_id": row["enrollment_id"],
        "name": display_name,
    }


def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    """Get basic user info by user_id."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, username, enrollment_id FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)


# ------------------------------------------------------------- Profile CRUD --

def get_user_profile(user_id: str) -> dict[str, Any]:
    """Retrieve full isolated profile data for a specific user."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # User account info
        cursor.execute("SELECT email, enrollment_id FROM users WHERE id = ?", (user_id,))
        u_row = cursor.fetchone()
        user_email = u_row["email"] if u_row else ""
        enrollment_id = u_row["enrollment_id"] if u_row else ""

        # Profile basic fields
        cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
        p_row = cursor.fetchone()
        profile_data = dict(p_row) if p_row else {}

        # Education entries
        cursor.execute(
            """
            SELECT id, degree, field_of_study, institution, start_year, grad_year, score, description
            FROM education WHERE user_id = ? ORDER BY created_at ASC
            """,
            (user_id,),
        )
        edu_rows = [dict(r) for r in cursor.fetchall()]

        # Skills
        cursor.execute("SELECT name, level FROM skills WHERE user_id = ?", (user_id,))
        skills = [{"name": r["name"], "level": r["level"]} for r in cursor.fetchall()]

        # Certifications
        cursor.execute("SELECT name, provider FROM certifications WHERE user_id = ?", (user_id,))
        certs = [{"name": r["name"], "provider": r["provider"]} for r in cursor.fetchall()]

        # Projects
        cursor.execute("SELECT title, description, tags FROM projects WHERE user_id = ?", (user_id,))
        projects = []
        for r in cursor.fetchall():
            tags_list = [t.strip() for t in (r["tags"] or "").split(",") if t.strip()]
            projects.append({"title": r["title"], "description": r["description"] or "", "tags": tags_list})

        # Internships
        cursor.execute("SELECT role, organization FROM internships WHERE user_id = ?", (user_id,))
        internships = [{"role": r["role"], "organization": r["organization"] or ""} for r in cursor.fetchall()]

    name = profile_data.get("name", "")
    resume = None
    if profile_data.get("resume_filename"):
        resume = {
            "filename": profile_data["resume_filename"],
            "size_bytes": profile_data.get("resume_size") or 0,
        }

    return {
        "user_id": user_id,
        "name": name,
        "initials": "".join(part[0] for part in name.split()[:2]).upper() if name.strip() else "?",
        "email": user_email,
        "enrolment_id": enrollment_id,
        "target_role": profile_data.get("target_role") or "Cloud Solutions Architect",
        "track": profile_data.get("track") or "",
        "semester": profile_data.get("semester") or "",
        "phone": profile_data.get("phone") or "",
        "degree": profile_data.get("degree") or "",
        "cgpa": profile_data.get("cgpa"),
        "github": profile_data.get("github") or "",
        "linkedin": profile_data.get("linkedin") or "",
        "languages": profile_data.get("languages") or "",
        "skills": skills,
        "certifications": certs,
        "projects": projects,
        "internships": internships,
        "education_entries": edu_rows,
        "resume": resume,
    }


def save_user_profile(user_id: str, profile: dict[str, Any]) -> None:
    """Save full user profile to database with isolated relations."""
    init_db()
    now_iso = datetime.now(timezone.utc).isoformat()
    resume = profile.get("resume") or {}

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Update or insert into profiles
        cursor.execute(
            """
            INSERT INTO profiles (
                user_id, name, target_role, track, semester, phone, degree, cgpa,
                github, linkedin, languages, resume_filename, resume_size, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                name=excluded.name,
                target_role=excluded.target_role,
                track=excluded.track,
                semester=excluded.semester,
                phone=excluded.phone,
                degree=excluded.degree,
                cgpa=excluded.cgpa,
                github=excluded.github,
                linkedin=excluded.linkedin,
                languages=excluded.languages,
                resume_filename=excluded.resume_filename,
                resume_size=excluded.resume_size,
                updated_at=excluded.updated_at
            """,
            (
                user_id,
                profile.get("name", "").strip(),
                profile.get("target_role", "Cloud Solutions Architect"),
                profile.get("track", ""),
                profile.get("semester", ""),
                profile.get("phone", ""),
                profile.get("degree", ""),
                profile.get("cgpa"),
                profile.get("github", ""),
                profile.get("linkedin", ""),
                profile.get("languages", ""),
                resume.get("filename"),
                resume.get("size_bytes"),
                now_iso,
            ),
        )

        # Sync skills
        cursor.execute("DELETE FROM skills WHERE user_id = ?", (user_id,))
        for s in profile.get("skills", []):
            if s.get("name"):
                cursor.execute(
                    "INSERT INTO skills (id, user_id, name, level) VALUES (?, ?, ?, ?)",
                    (f"sk_{secrets.token_hex(6)}", user_id, s["name"].strip(), int(s.get("level", 0))),
                )

        # Sync certifications
        cursor.execute("DELETE FROM certifications WHERE user_id = ?", (user_id,))
        for c in profile.get("certifications", []):
            if c.get("name"):
                cursor.execute(
                    "INSERT INTO certifications (id, user_id, name, provider) VALUES (?, ?, ?, ?)",
                    (f"cert_{secrets.token_hex(6)}", user_id, c["name"].strip(), c.get("provider", "").strip()),
                )

        # Sync projects
        cursor.execute("DELETE FROM projects WHERE user_id = ?", (user_id,))
        for p in profile.get("projects", []):
            if p.get("title"):
                tags_str = ", ".join(p.get("tags") or [])
                cursor.execute(
                    "INSERT INTO projects (id, user_id, title, description, tags) VALUES (?, ?, ?, ?, ?)",
                    (f"proj_{secrets.token_hex(6)}", user_id, p["title"].strip(), p.get("description", "").strip(), tags_str),
                )

        # Sync internships
        cursor.execute("DELETE FROM internships WHERE user_id = ?", (user_id,))
        for i in profile.get("internships", []):
            if i.get("role"):
                cursor.execute(
                    "INSERT INTO internships (id, user_id, role, organization) VALUES (?, ?, ?, ?)",
                    (f"int_{secrets.token_hex(6)}", user_id, i["role"].strip(), i.get("organization", "").strip()),
                )

        # Sync education_entries if provided in profile dict
        if "education_entries" in profile:
            cursor.execute("DELETE FROM education WHERE user_id = ?", (user_id,))
            for edu in profile.get("education_entries", []):
                edu_id = edu.get("id") or f"edu_{secrets.token_hex(6)}"
                cursor.execute(
                    """
                    INSERT INTO education (id, user_id, degree, field_of_study, institution, start_year, grad_year, score, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        edu_id,
                        user_id,
                        edu.get("degree") or edu.get("level") or "Degree",
                        edu.get("field_of_study", ""),
                        edu.get("institution", ""),
                        edu.get("start_year", ""),
                        edu.get("grad_year") or edu.get("year", ""),
                        edu.get("score", ""),
                        edu.get("description", ""),
                        now_iso,
                    ),
                )

        conn.commit()


# -------------------------------------------------------- Education CRUD --

def add_education_entry(user_id: str, entry: dict[str, Any]) -> str:
    """Add a new education entry for the user and log activity."""
    init_db()
    edu_id = f"edu_{secrets.token_hex(6)}"
    now_iso = datetime.now(timezone.utc).isoformat()

    degree = entry.get("degree") or entry.get("level") or "Degree"
    institution = entry.get("institution") or "Institution"
    field_of_study = entry.get("field_of_study") or ""
    start_year = entry.get("start_year") or ""
    grad_year = entry.get("grad_year") or entry.get("year") or ""
    score = entry.get("score") or ""
    description = entry.get("description") or ""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO education (id, user_id, degree, field_of_study, institution, start_year, grad_year, score, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                edu_id,
                user_id,
                degree.strip(),
                field_of_study.strip(),
                institution.strip(),
                start_year.strip(),
                grad_year.strip(),
                score.strip(),
                description.strip(),
                now_iso,
            ),
        )
        conn.commit()

    log_activity(user_id, "education_added", "Education added", f"Added {degree} from {institution}.")
    return edu_id


def update_education_entry(user_id: str, edu_id: str, entry: dict[str, Any]) -> bool:
    """Update an existing education entry for the user."""
    init_db()
    degree = entry.get("degree") or entry.get("level") or "Degree"
    institution = entry.get("institution") or "Institution"
    field_of_study = entry.get("field_of_study") or ""
    start_year = entry.get("start_year") or ""
    grad_year = entry.get("grad_year") or entry.get("year") or ""
    score = entry.get("score") or ""
    description = entry.get("description") or ""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE education
            SET degree = ?, field_of_study = ?, institution = ?, start_year = ?, grad_year = ?, score = ?, description = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                degree.strip(),
                field_of_study.strip(),
                institution.strip(),
                start_year.strip(),
                grad_year.strip(),
                score.strip(),
                description.strip(),
                edu_id,
                user_id,
            ),
        )
        updated = cursor.rowcount > 0
        conn.commit()

    if updated:
        log_activity(user_id, "education_updated", "Education updated", f"Updated {degree} at {institution}.")
    return updated


def delete_education_entry(user_id: str, edu_id: str) -> bool:
    """Delete an education entry for the user."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT degree, institution FROM education WHERE id = ? AND user_id = ?", (edu_id, user_id))
        existing = cursor.fetchone()
        cursor.execute("DELETE FROM education WHERE id = ? AND user_id = ?", (edu_id, user_id))
        deleted = cursor.rowcount > 0
        conn.commit()

    if deleted and existing:
        log_activity(
            user_id,
            "education_deleted",
            "Education removed",
            f"Removed {existing['degree']} from {existing['institution']}.",
        )
    return deleted


# ----------------------------------------------------- Activity Logging --

def log_activity(
    user_id: str,
    activity_type: str,
    title: str,
    description: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Log an applicant activity timestamped in UTC."""
    if not user_id:
        return
    init_db()
    act_id = f"act_{secrets.token_hex(6)}"
    now_iso = datetime.now(timezone.utc).isoformat()
    meta_json = json.dumps(metadata) if metadata else None

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO activities (id, user_id, activity_type, title, description, timestamp, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (act_id, user_id, activity_type, title, description, now_iso, meta_json),
            )
            conn.commit()
    except Exception:
        pass


def get_user_activities(user_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Retrieve chronologically sorted activities for a user."""
    if not user_id:
        return []
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, activity_type, title, description, timestamp, metadata_json
            FROM activities
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        results = []
        for r in cursor.fetchall():
            meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
            results.append(
                {
                    "id": r["id"],
                    "activity_type": r["activity_type"],
                    "title": r["title"],
                    "description": r["description"] or "",
                    "timestamp": r["timestamp"],
                    "metadata": meta,
                }
            )
        return results


# --------------------------------------------------- Assessment Attempts --

def save_assessment_attempt_db(user_id: str, attempt: dict[str, Any]) -> None:
    """Save completed assessment attempt and question history to DB."""
    if not user_id or not attempt:
        return
    init_db()
    attempt_id = attempt.get("attempt_id") or f"att_{secrets.token_hex(8)}"
    now_iso = attempt.get("submitted_at") or datetime.now(timezone.utc).isoformat()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO assessment_attempts (
                attempt_id, user_id, domain_key, domain_name, difficulty,
                overall_pct, correct_count, total, submitted_at, result_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt_id,
                user_id,
                attempt.get("domain_key", "general"),
                attempt.get("domain_name", "Assessment"),
                attempt.get("difficulty", "Easy"),
                float(attempt.get("overall_pct", 0.0)),
                int(attempt.get("correct_count", 0)),
                int(attempt.get("total", 0)),
                now_iso,
                json.dumps(attempt),
            ),
        )

        # Question history for non-repetition
        q_ids = attempt.get("question_ids") or []
        if q_ids:
            cursor.execute(
                """
                INSERT INTO question_history (user_id, domain_key, difficulty, question_ids_json, attempt_id, submitted_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    attempt.get("domain_key", "general"),
                    attempt.get("difficulty", "Easy").lower(),
                    json.dumps(q_ids),
                    attempt_id,
                    now_iso,
                ),
            )

        conn.commit()

    log_activity(
        user_id,
        "assessment_completed",
        "Assessment completed",
        f"Completed {attempt.get('domain_name', 'Assessment')} ({attempt.get('difficulty', 'Standard')}) with {attempt.get('overall_pct', 0)}% score.",
        metadata={"attempt_id": attempt_id, "score": attempt.get("overall_pct")},
    )


def get_user_assessment_history(user_id: str) -> list[dict[str, Any]]:
    """Retrieve all historical assessment attempts for a user."""
    if not user_id:
        return []
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT result_json FROM assessment_attempts
            WHERE user_id = ?
            ORDER BY submitted_at ASC
            """,
            (user_id,),
        )
        history = []
        for r in cursor.fetchall():
            try:
                history.append(json.loads(r["result_json"]))
            except Exception:
                continue
        return history


def get_user_question_history_db(user_id: str) -> list[dict[str, Any]]:
    """Get question history records for non-repetition question picker."""
    if not user_id:
        return []
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT domain_key, difficulty, question_ids_json, attempt_id, submitted_at
            FROM question_history
            WHERE user_id = ?
            ORDER BY submitted_at DESC
            """,
            (user_id,),
        )
        records = []
        for r in cursor.fetchall():
            try:
                q_ids = json.loads(r["question_ids_json"])
                records.append(
                    {
                        "domain_key": r["domain_key"],
                        "difficulty": r["difficulty"],
                        "question_ids": q_ids,
                        "attempt_id": r["attempt_id"],
                        "submitted_at": r["submitted_at"],
                    }
                )
            except Exception:
                continue
        return records


# ------------------------------------------------------------- Reports DB --

def save_report_db(
    user_id: str, filename: str, score: float | None, size_bytes: int, sections: list[str]
) -> str:
    """Save a record of a generated report in the database."""
    if not user_id:
        return ""
    init_db()
    rep_id = f"rep_{secrets.token_hex(6)}"
    now_iso = datetime.now(timezone.utc).isoformat()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO reports (id, user_id, filename, score, size_bytes, created_at, sections_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (rep_id, user_id, filename, score, size_bytes, now_iso, json.dumps(sections)),
        )
        conn.commit()

    log_activity(
        user_id,
        "report_generated",
        "Report generated",
        f"Generated PDF report {filename}.",
        metadata={"report_id": rep_id, "filename": filename},
    )
    return rep_id


def get_user_reports_db(user_id: str) -> list[dict[str, Any]]:
    """Retrieve list of generated reports for the user."""
    if not user_id:
        return []
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, filename, score, size_bytes, created_at, sections_json
            FROM reports
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        reports = []
        for r in cursor.fetchall():
            reports.append(
                {
                    "id": r["id"],
                    "filename": r["filename"],
                    "name": r["filename"],
                    "score": r["score"],
                    "size_bytes": r["size_bytes"],
                    "size": f"{r['size_bytes'] / 1024:.1f} KB" if r["size_bytes"] else "N/A",
                    "when": r["created_at"],
                    "sections": json.loads(r["sections_json"]) if r["sections_json"] else [],
                }
            )
        return reports


# ------------------------------------------------------------- Saved Jobs --

def save_user_job(user_id: str, job_id: int) -> bool:
    """Save/bookmark a job for a user."""
    if not user_id or not job_id:
        return False
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO saved_jobs (user_id, job_id, saved_at)
            VALUES (?, ?, ?)
            """,
            (user_id, int(job_id), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return True


def unsave_user_job(user_id: str, job_id: int) -> bool:
    """Remove a saved job for a user."""
    if not user_id or not job_id:
        return False
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM saved_jobs
            WHERE user_id = ? AND job_id = ?
            """,
            (user_id, int(job_id)),
        )
        conn.commit()
    return True


def get_user_saved_job_ids(user_id: str) -> set[int]:
    """Return set of saved job IDs for a user."""
    if not user_id:
        return set()
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT job_id FROM saved_jobs WHERE user_id = ?
            """,
            (user_id,),
        )
        return {row["job_id"] for row in cursor.fetchall()}


def is_job_saved(user_id: str, job_id: int) -> bool:
    """Check if a specific job is saved by a user."""
    if not user_id or not job_id:
        return False
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM saved_jobs WHERE user_id = ? AND job_id = ?
            """,
            (user_id, int(job_id)),
        )
        return cursor.fetchone() is not None


def update_user_password(identifier: str, enrollment_id: str, new_password: str) -> bool:
    """Update the user's password if the identifier (email/username) and enrollment_id match."""
    clean_ident = identifier.strip().lower()
    clean_eid = enrollment_id.strip()
    if not clean_ident or not clean_eid or not new_password:
        return False
        
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id FROM users
            WHERE (email = ? OR username = ?) AND enrollment_id = ?
            """,
            (clean_ident, clean_ident, clean_eid),
        )
        row = cursor.fetchone()
        if not row:
            return False
            
        pw_hash = hash_password(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (pw_hash, row["id"])
        )
        conn.commit()
        return True
