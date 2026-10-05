@echo off
setlocal
echo =================================================================
echo                    EmployaAI Platform
echo       AI-Driven Student Employability & Skill Assessment
echo =================================================================
echo.

cd /d "%~dp0"

echo Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not found in your PATH. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

echo Starting EmployaAI Streamlit Application...
echo.
python -m streamlit run app.py

pause
