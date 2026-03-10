@echo off
echo ============================================================
echo  FIXING GEMINI IMPORT ERROR
echo ============================================================
echo.
echo This will:
echo   1. Uninstall conflicting Google packages
echo   2. Install correct google-genai SDK
echo   3. Verify installation
echo   4. Test backend startup
echo.
pause

cd backend

echo.
echo [1/4] Uninstalling conflicting packages...
echo ============================================================
venv\Scripts\pip.exe uninstall -y google google-generativeai google-cloud 2>nul
echo Done.

echo.
echo [2/4] Installing google-genai SDK...
echo ============================================================
venv\Scripts\pip.exe install google-genai==0.2.2
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install google-genai
    pause
    exit /b 1
)

echo.
echo [3/4] Verifying installation...
echo ============================================================
venv\Scripts\pip.exe show google-genai
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Package not found after installation
    pause
    exit /b 1
)

echo.
echo [4/4] Testing imports...
echo ============================================================
venv\Scripts\python.exe -c "from google import genai; print('✅ Import successful: from google import genai')"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Import test failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  ✅ FIX COMPLETE
echo ============================================================
echo.
echo Next step: Start the backend
echo   venv\Scripts\python.exe -m uvicorn app.main:app --reload
echo.
pause
