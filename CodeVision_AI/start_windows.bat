@echo off
setlocal
cd /d "%~dp0"
echo === CodeVision AI -- Windows launcher ===
where npm >nul 2>&1 || (echo ERROR: Node.js/npm is missing. Install Node.js 20+ and retry. & pause & exit /b 1)
if not exist ".env" (
  copy /Y ".env.example" ".env" >nul
  echo Created .env. Add HINDSIGHT_API_KEY and GROQ_API_KEY, then restart for live AI memory.
)
if not exist ".venv\Scripts\python.exe" (
  py -3.12 --version >nul 2>&1
  if not errorlevel 1 (
    py -3.12 -m venv .venv
  ) else (
    py -3.13 --version >nul 2>&1
    if not errorlevel 1 (
      py -3.13 -m venv .venv
    ) else (
      py -3.11 --version >nul 2>&1
      if not errorlevel 1 (
        py -3.11 -m venv .venv
      ) else (
        echo ERROR: Please install Python 3.12 or 3.13; Python 3.14 has not been validated for this project.
        pause
        exit /b 1
      )
    )
  )
)
if not exist ".venv\Scripts\python.exe" (echo Virtual environment creation failed. & pause & exit /b 1)
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt || (echo Backend dependency install failed. See README. & pause & exit /b 1)
start "CodeVision FastAPI" cmd /k ""%~dp0scripts\run_backend_windows.bat""
cd frontend
call npm install --no-audit --no-fund || (echo Frontend dependency install failed. Check internet connection. & pause & exit /b 1)
start "CodeVision React" cmd /k ""%~dp0scripts\run_frontend_windows.bat""
echo.
echo Open http://127.0.0.1:5173 in your browser.
echo Backend API docs: http://127.0.0.1:8000/docs
pause
