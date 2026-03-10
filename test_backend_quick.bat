@echo off
echo ============================================================
echo TESTING BACKEND STARTUP
echo ============================================================
echo.

cd backend

echo Starting backend server...
echo.

start /B venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > startup_test.log 2>&1

echo Waiting 3 seconds for startup...
timeout /t 3 /nobreak > nul

echo.
echo Checking if server is running...
curl -s http://127.0.0.1:8000/docs > nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS: Backend started successfully!
    echo ============================================================
    echo.
    echo Server is running at: http://127.0.0.1:8000
    echo API docs available at: http://127.0.0.1:8000/docs
    echo.
    echo Press Ctrl+C to stop the server
    echo.
) else (
    echo.
    echo ============================================================
    echo WARNING: Could not connect to server
    echo ============================================================
    echo.
    echo Check startup_test.log for details
    echo.
)

cd ..
