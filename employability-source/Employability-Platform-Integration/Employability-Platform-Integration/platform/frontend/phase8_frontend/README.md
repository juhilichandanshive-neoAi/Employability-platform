# EmployaAI frontend

EmployaAI is a Streamlit student employability platform. The frontend uses a
session-backed student profile and assessment results to calculate a
deterministic employability score, compare recorded skills with a bundled
industry/job dataset snapshot, and produce current-session recommendations and
reports.

## Run

From the repository root:

```bash
cd platform/frontend/phase8_frontend
pip install -r requirements.txt
streamlit run app.py
```

The frontend requirements include ReportLab because the Reports screen imports
it at startup and uses it to generate downloadable PDF files.

## Current architecture

- **Streamlit frontend:** `app.py` routes to the dashboard, profile,
  assessment, score, skill-gap, career, certification, roadmap, analytics,
  report, and settings screens.
- **Session-backed profile:** a blank profile is created in
  `st.session_state.profile`. Profile edits, assessment history, and generated
  reports remain in the current Streamlit session. The entry screen collects
  an optional email but does not verify identity or create a persistent account;
  there is no database integration.
- **Assessment service:** answers from the static question bank in
  `data/dummy_data.py` are scored by the backend assessment service. Static
  question and UI configuration data remain in that module. The active routes
  use `screens/profile_session.py` and `screens/roadmap_session.py`; the older
  `screens/profile.py` and `screens/roadmap.py` sample screens are not routed
  by `app.py`.
- **Employability score:** `calculate_score(profile, assessment)` combines
  profile and assessment components using
  `platform/backend/NeoAI1stPipeline/config/employability_weights.json`.
- **Skill-gap analysis:** student proficiency is recorded on a 0–5 scale and
  compared with role requirements on a 1–10 scale from the bundled dataset.
- **Career matching:** supported roles are matched against the bundled
  industry/job CSV snapshot. It is not a live jobs feed. Any salary range shown
  is from that snapshot, not a model prediction or live salary source.
- **Certifications and roadmap:** certification recommendations are selected
  from measured skill gaps. Roadmap actions use those gaps and weak areas from
  the latest assessment; costs, ratings, durations, and score improvements are
  not estimated.
- **Analytics:** only assessments completed in the current session are shown.
  There is no fabricated historical or cohort performance.
- **PDF reports:** ReportLab generates a real downloadable PDF from the
  current session's profile, assessment, score, gaps, and recommendations.
  Historical results are not invented.
- **Salary model:** `platform/backend/NeoAI1stPipeline/models/final_salary_model.pkl`
  is absent. Although the DVC lock records its expected artifact, a pull from
  the configured remote reported that the cache object is missing. ML salary
  prediction is disabled; the existing salary ML/DVC pipeline is unchanged.

## Key files

- `app.py` — Streamlit entry point, module paths, and screen routing.
- `services/session.py` — builds and stores current-session app data.
- `services/integration.py` — composes score, skill gaps, role matches,
  certifications, roadmap, analytics, and salary-model status.
- `services/reporting.py` — creates the downloadable PDF.
- `screens/profile_session.py` and `screens/roadmap_session.py` — session-backed
  profile and roadmap screens.
- `platform/backend/NeoAI1stPipeline/src/neoai/services/` — assessment,
  employability, and read-only dataset services.