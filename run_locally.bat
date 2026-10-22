@echo off
echo =======================================================
echo  Starting StudyBot - ATMOS '26 ^| IEEE BPHC
echo =======================================================
echo.

if exist ".venv\Scripts\python.exe" (
    echo Using virtual environment (.venv)...
    ".venv\Scripts\python.exe" app.py
) else (
    echo Using system Python...
    python app.py
)

if errorlevel 1 (
    echo.
    echo App exited with an error.
    pause
)
