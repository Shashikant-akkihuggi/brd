@echo off
echo ============================================================
echo  AUTHENTICATION FIX - INSTALLATION SCRIPT
echo ============================================================
echo.
echo This script will:
echo   1. Install missing google-genai dependency
echo   2. Verify installation
echo   3. Test backend startup
echo.
pause

echo.
echo [1/3] Installing google-genai package...
echo ============================================================
cd backend
venv\Scripts\pip.exe install google-genai==0.2.2
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install google-genai
    pause
    exit /b 1
)
echo.
echo ✅ Package installed successfully
echo.

echo [2/3] Verifying installation...
echo ============================================================
venv\Scripts\pip.exe show google-genai
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Package not found after installation
    pause
    exit /b 1
)
echo.
echo ✅ Package verified
echo.

echo [3/3] Testing backend import...
echo ============================================================
venv\Scripts\python.exe ..\test_imports.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Backend import test failed
    echo Check the error message above
    pause
    exit /b 1
)
echo.

echo ============================================================
echo  INSTALLATION COMPLETE
echo ============================================================
echo.
echo Next steps:
echo   1. Start the backend:
echo      cd backend
echo      venv\Scripts\python.exe -m uvicorn app.main:app --reload
echo.
echo   2. In another terminal, run diagnosis:
echo      venv\Scripts\python.exe diagnose_auth.py
echo.
echo   3. Test from frontend (register/login)
echo.
pause
