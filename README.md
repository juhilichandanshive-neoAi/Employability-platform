# EmployaAI

> **AI-Powered Student Employability & Assessment Platform**
>
> A high-performance Streamlit application for student employability assessment, personalized career roadmaps, skill-gap analysis, randomized assessments, secure authentication, PDF reporting, job opportunities, and applicant activity tracking.

---

## 🚀 Quick Start

### 1. Installation

Clone the repository or navigate to the project directory and install the required dependencies:

```bash
python -m pip install -r requirements.txt

2. Launch Application
Start the application from the project root:
streamlit run app.py

The application will open in your browser at:
http://localhost:8501

3. Windows One-Click Launch
On Windows, you can also launch the application by double-clicking:
run_app.bat

🧪 Running the Test Suite
Run the complete automated test suite:
python -m unittest discover -s tests

To run the UI verification script:
python verify_ui.py

✨ Platform Features
🔐 Authentication & Account Security
- Secure student registration and login
- Enrollment ID generation for every registered student
- Username/email-based authentication
- Password confirmation and validation
- Secure password hashing
- Session protection
- Applicant activity tracking
🎓 Student Profile & Education
- Complete student profile management
- Multiple education/qualification entries
- Degree and field-of-study information
- Institution details
- Start year and graduation year
- Score/CGPA tracking
- Add, edit, and delete education records
- Persistent profile data
📊 Employability Assessment
- 15-question assessment attempts
- Randomized question selection
- Randomized answer options
- Anti-repetition question tracking
- Stable questions during Streamlit reruns
- Automatic score calculation
- Skill-gap identification
- Employability score generation
🧠 Skill Gap Analysis
The platform analyses assessment performance and identifies areas where students need improvement.
Students can view:
- Current skill level
- Skill gaps
- Target skills
- Recommended learning areas
- Career development priorities
🛣️ Personalized Career Roadmap
EmployaAI provides personalized career guidance based on the student's profile and assessment performance.
The roadmap includes:
- Recommended skills
- Learning priorities
- Career direction
- Development milestones
- Recommended certifications
- Improvement areas
💼 Career & Job Opportunities
The platform provides career-oriented job information based on industry requirements and available job data.
Features include:
- Industry job requirements
- Career recommendations
- Job opportunity information
- Required skills
- Industry demand information
- Salary-related evidence where available
📄 Personalized PDF Reports
Students can generate professional reports containing:
- Student information
- Enrollment ID
- Employability score
- Assessment performance
- Skill-gap analysis
- Career recommendations
- Personalized roadmap
📈 Analytics
The platform includes analytics for:
- Employability performance
- Skill distribution
- Assessment results
- Career-related insights
- Cohort-level analysis where applicable
📝 Applicant Activity Tracking
The platform maintains an activity history for important student actions, including:
- Registration
- Login activity
- Assessment attempts
- Profile updates
- Education updates
- Other supported platform activities
🏗️ Project Structure
Employability-platform/
│
├── app.py
├── requirements.txt
├── README.md
├── run_app.bat
├── verify_ui.py
├── .gitignore
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
│
├── assets/
│   ├── styles.css
│   └── images/
│
├── components/
│   ├── badges.py
│   ├── cards.py
│   ├── charts.py
│   ├── footer.py
│   ├── html.py
│   ├── icons.py
│   ├── modals.py
│   ├── navigation.py
│   └── tables.py
│
├── screens/
│   ├── activity.py
│   ├── analytics.py
│   ├── assessment.py
│   ├── careers.py
│   ├── certifications.py
│   ├── dashboard.py
│   ├── login_session.py
│   ├── profile_session.py
│   ├── reports.py
│   ├── roadmap_session.py
│   ├── score.py
│   ├── settings.py
│   └── skill_gap.py
│
├── services/
│   ├── activity_service.py
│   ├── assessment_service.py
│   ├── auth_service.py
│   ├── db.py
│   ├── employability_service.py
│   ├── integration.py
│   ├── job_data_service.py
│   ├── profile_service.py
│   ├── question_service.py
│   ├── report_service.py
│   └── session.py
│
├── data/
│   ├── dummy_data.py
│   ├── employability_weights.json
│   ├── Merged_industry_jobs_industry_jobs.csv
│   └── question_bank.py
│
├── storage/
│   ├── employability.db
│   └── reports/
│
├── utils/
│   ├── paths.py
│   └── state.py
│
└── tests/
    ├── test_app_flow.py
    ├── test_audit_fixes.py
    ├── test_auth_education_and_security.py
    └── test_education_and_questions.py

⚙️ Configuration
Database
The application uses SQLite for local persistence.
The database is initialized automatically by the application.
storage/employability.db

The local database is excluded from version control.
Google OAuth
Google Sign-In can be configured through Streamlit secrets.
Create:
.streamlit/secrets.toml

using the provided example:
.streamlit/secrets.toml.example

Example configuration:
[google_oauth]
client_id = "your-google-client-id"
client_secret = "your-google-client-secret"
redirect_uri = "http://localhost:8501"

Do not commit real credentials or secrets to GitHub.
🔒 Security
The project follows basic application security practices including:
- Password hashing
- Session protection
- User data isolation
- Environment/secrets exclusion through .gitignore
- Local database exclusion from version control
- Input validation
- Authentication checks
- Protected application screens
Never commit:
.env
.streamlit/secrets.toml
credentials.json
service-account.json
*.pem
*.key

🧠 Assessment Engine
The assessment engine provides a controlled and repeatable assessment experience.
Each attempt:
1. Selects 15 questions.
2. Randomizes the question order.
3. Randomizes answer options.
4. Locks the selected questions during the current attempt.
5. Calculates the final score.
6. Records the assessment attempt.
7. Updates the student's employability profile.
8. Identifies skill gaps.
9. Updates the personalized roadmap.
Previously seen questions are tracked to reduce unnecessary repetition between attempts.
📊 Employability Scoring
The platform calculates an employability score using student information and assessment performance.
The score is used to support:
- Performance analysis
- Skill-gap identification
- Career recommendations
- Roadmap generation
- Progress tracking
The scoring configuration is maintained in:
data/employability_weights.json

📄 Reporting
EmployaAI provides personalized PDF reports based on the student's current platform data.
Reports can include:
- Student profile
- Enrollment ID
- Education information
- Assessment results
- Employability score
- Skill gaps
- Career recommendations
- Roadmap information
🧪 Quality & Testing
The repository contains automated tests covering major application functionality, including:
- Authentication
- User isolation
- Education management
- Assessment logic
- Question randomization
- Question history
- Score calculation
- UI-related regression checks
- Session state handling
- Security-related checks
Run:
python -m unittest discover -s tests

🛠️ Technology Stack
Frontend / Application
- Streamlit
- HTML
- CSS
- Plotly
- Responsive UI components
Backend / Application Logic
- Python
- SQLite
- Session management
- Service-oriented application architecture
AI / Data
- Employability scoring
- Skill-gap analysis
- Career recommendation logic
- Assessment analytics
- Industry job datasets
Reporting
- PDF report generation
- Personalized student reports
📌 Application Workflow
Student Registration
        ↓
Enrollment ID Generation
        ↓
Secure Login
        ↓
Student Profile
        ↓
Education & Skills
        ↓
Employability Assessment
        ↓
Score Calculation
        ↓
Skill Gap Analysis
        ↓
Career Recommendations
        ↓
Personalized Roadmap
        ↓
Job Opportunities
        ↓
PDF Report
        ↓
Activity Tracking

🎯 Purpose
EmployaAI is designed to help students understand their current employability level and identify the skills they need to develop for their desired career path.
The platform brings together:
- Student profiling
- Skill assessment
- Employability scoring
- Skill-gap analysis
- Career guidance
- Job opportunities
- Learning roadmaps
- Progress tracking
- Professional reporting
into a single platform.
👩‍💻 Project
EmployaAI — AI-Powered Student Employability & Assessment Platform
Built as an academic/project platform focused on improving student career readiness through structured assessment, analytics, and personalized career guidance.
📜 License
This project is intended for academic, educational, research, and demonstration purposes.

### ❤️ What you do now

On GitHub:

**README.md → ✏️ Edit → `Ctrl + A` → delete everything → paste the entire README above → Commit changes.**

That will update **everything in one shot**, including the incorrect:

```bash
python -m streamlit run app.py

to the actual working:
streamlit run app.py
