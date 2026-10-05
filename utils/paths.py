"""Centralized project path configuration.

Provides reliable, cross-platform, project-relative paths.
Never hardcodes absolute Windows or machine-specific directories.
"""

from pathlib import Path

# Project root directory (EmployaAI root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Core subdirectories
ASSETS_DIR = PROJECT_ROOT / "assets"
COMPONENTS_DIR = PROJECT_ROOT / "components"
SCREENS_DIR = PROJECT_ROOT / "screens"
SERVICES_DIR = PROJECT_ROOT / "services"
DATA_DIR = PROJECT_ROOT / "data"
STORAGE_DIR = PROJECT_ROOT / "storage"
REPORTS_DIR = STORAGE_DIR / "reports"
TESTS_DIR = PROJECT_ROOT / "tests"

# Core persistent and data file paths
DB_PATH = STORAGE_DIR / "employability.db"
LEGACY_DB_PATH = DATA_DIR / "employability.db"

WEIGHTS_PATH = DATA_DIR / "employability_weights.json"
JOBS_DATA_PATH = DATA_DIR / "Merged_industry_jobs_industry_jobs.csv"

# Ensure runtime directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_db_path() -> Path:
    """Return active database path, with fallback to legacy data dir if present."""
    if DB_PATH.exists():
        return DB_PATH
    if LEGACY_DB_PATH.exists():
        return LEGACY_DB_PATH
    return DB_PATH
