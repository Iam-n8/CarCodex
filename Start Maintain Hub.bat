@echo off

cd /d "%~dp0App\System\backend"

"%~dp0App\.venv\Scripts\python.exe" -m uvicorn main:app --reload

rem uvicorn main:app --reload

pause
echo Maintain Hub exited.

echo Window will close in 30 seconds...

timeout /t 30