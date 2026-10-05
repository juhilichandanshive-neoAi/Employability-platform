# EmployaAI

> **AI-Powered Student Employability & Assessment Platform**  
> A high-performance Streamlit application delivering personalized student career roadmaps, deterministic employability scoring, interactive randomized assessments, real user authentication, verified PDF reporting, and applicant activity tracking.

---

## Quick Start

### 1. Installation
Clone or navigate to the project directory and install the required dependencies:
```bash
python -m pip install -r requirements.txt
```

### 2. Launch Application
Start the Streamlit application directly from the project root:
```bash
python -m streamlit run app.py
```
*If using a specific Python version (e.g., Python 3.13):*
```bash
py -3.13 -m streamlit run app.py
```

### 3. One-Click Launch (Windows)
Double-click `run_app.bat` in the project root directory.

---

## Running the Automated Test Suite

Run all automated unit, integration, security, and UI regression tests:
```bash
python -m unittest discover -s tests
```

To run the interactive UI element verification script:
```bash
python verify_ui.py
```

---

## Project Structure

```
EmployaAI/
│
├── app.py                      # Main application entry point & session router
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation & operational guide
├── run_app.bat                 # One-click Windows startup script
├── verify_ui.py                # Automated headless UI verification script
├── .gitignore                  # Git exclusions (protects local DB & secrets)
│
├── .streamlit/                 # Streamlit configuration
│   ├── config.toml             # Theme settings (lavender/purple visual palette)
│   └── secrets.toml.example    # OAuth / API keys template
│
├── assets/                     # Static styling and images
│   ├── styles.css              # Custom CSS rules, micro-interactions, cards
│   └── images/                 # Platform branding & campus illustrations
│
├── components/                 # Reusable UI component modules
│   ├── badges.py               # Metric and category status badges
│   ├── cards.py                # Standardized card layouts and banners
│   ├── charts.py               # Plotly radar, bar, and gauge charts
│   ├── footer.py               # SaaS footer with light lavender theme
│   ├── html.py                 # Safe HTML rendering utilities
│   ├── icons.py                # SVG icon registry
│   ├── modals.py               # Confirmation dialogs
│   ├── navigation.py           # Sidebar and mobile navigation
│   └── tables.py               # Formatted data tables
│
├── screens/                    # Page controllers and view templates
│   ├── activity.py             # Applicant activity log & audit history
│   ├── analytics.py            # Cohort and skill analytics
│   ├── assessment.py           # Assessment engine (randomization, stability)
│   ├── careers.py              # Career suggestions and market demand
│   ├── certifications.py       # Certification tracker
│   ├── dashboard.py            # Personalized student dashboard
│   ├── login_session.py        # Authentication (Sign In & Registration tabs)
│   ├── profile_session.py      # Profile management & interactive Education CRUD
│   ├── reports.py              # Reports dashboard with PDF generation & downloads
│   ├── roadmap_session.py      # Interactive skill roadmap
│   ├── score.py                # Employability score breakdown
│   ├── settings.py             # User and platform preferences
│   └── skill_gap.py            # Target role skill gap analysis
│
├── services/                   # Business logic and data services
│   ├── activity_service.py     # Applicant activity logging and metrics
│   ├── assessment_service.py   # Assessment scoring and attempt history
│   ├── auth_service.py         # Registration, password hashing, enrollment IDs
│   ├── db.py                   # SQLite persistence and data isolation layer
│   ├── employability_service.py# Weighted score calculator & profile completion
│   ├── integration.py          # App data aggregation and state synchronization
│   ├── job_data_service.py     # Industry job requirements and salary evidence
│   ├── profile_service.py      # Profile and academic qualification CRUD
│   ├── question_service.py     # 15-question random selection & anti-repetition
│   ├── report_service.py       # PDF document generation
│   └── session.py              # User session state lifecycle management
│
├── data/                       # Datasets, question bank, and configuration
│   ├── dummy_data.py           # Demonstration data fallbacks
│   ├── employability_weights.json # Scoring weights configuration
│   ├── Merged_industry_jobs_industry_jobs.csv # Industry demand dataset
│   └── question_bank.py        # 100+ vetted assessment questions across domains
│
├── storage/                    # Persistent application storage
│   ├── employability.db        # SQLite database (auto-initialized)
│   └── reports/                # Generated PDF report artifacts
│
├── utils/                      # Cross-cutting platform utilities
│   ├── paths.py                # Centralized project-relative paths
│   └── state.py                # Session state initialization and navigation
│
└── tests/                      # Automated test suite (47 passing tests)
    ├── test_app_flow.py        # Streamlit user flow regression tests
    ├── test_audit_fixes.py     # UI chart, styling, and session audit tests
    ├── test_auth_education_and_security.py # Auth, security, isolation & CRUD tests
    └── test_education_and_questions.py    # Education UI & question engine tests
```

---

## Platform Features

1. **Authentication & Password Security**:
   - Secure account registration with password confirmation and input validation.
   - Passwords hashed using `bcrypt` (with automatic PBKDF2 fallback).
   - Session protection prevents unauthenticated access to application screens.

2. **Unique Enrollment ID System**:
   - Every registered user receives a permanent Enrollment ID (`EA-2026-XXXXXX`).
   - Displayed across the Dashboard, Profile header, and applicant reports.

3. **Academic Education Management**:
   - Interactive `+ Add Education` modal and inline form in Profile.
   - Add multiple qualifications: Degree, Field of Study, Institution, Start/Grad Year, Score/CGPA.
   - Inline Edit (`✏️`) and Delete (`🗑️`) with immediate persistence.

4. **15-Question Random Assessment Engine**:
   - 15 questions selected per attempt from an expanded question bank.
   - Questions and options randomized on each new attempt.
   - State-locked stability prevents question shuffling across Streamlit reruns.
   - Anti-repetition tracking remembers previously seen questions.

5. **Applicant Activity Tracking**:
   - Chronological audit log of registrations, logins, assessments, and profile edits.
   - Accessible via the dedicated **Activity** sidebar view.

6. **Personalized PDF Reports**:
   - Generates custom, verified applicant reports with performance summaries, score breakdowns, and recommended career paths.

---

## Configuration & Environment

- **Database**: Initialized automatically at `storage/employability.db`. No manual database setup required.
- **Optional OAuth**: Google Sign-In credentials can be configured in `.streamlit/secrets.toml`:
  ```toml
  [google_oauth]
  client_id = "your-google-client-id"
  client_secret = "your-google-client-secret"
  redirect_uri = "http://localhost:8501"
  ```
- **Troubleshooting**: If running into port conflicts, specify a custom port:
  ```bash
  python -m streamlit run app.py --server.port 8502
  ```