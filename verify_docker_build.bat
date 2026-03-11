@echo off
echo ========================================
echo Docker Build Verification Script
echo ========================================
echo.

echo Step 1: Checking which requirements file Dockerfile uses...
echo.
findstr /C:"COPY" Dockerfile | findstr /C:"requirements"
echo.

echo Step 2: Displaying contents of backend/requirements_enhanced.txt
echo.
type backend\requirements_enhanced.txt
echo.

echo Step 3: Searching for python-cors in all requirements files...
echo.
findstr /S /I "python-cors" backend\*.txt
if %ERRORLEVEL% EQU 0 (
    echo ERROR: Found python-cors in requirements files!
) else (
    echo SUCCESS: No python-cors found in any requirements file
)
echo.

echo Step 4: Verifying backend/requirements.txt
echo.
type backend\requirements.txt
echo.

echo Step 5: Testing Docker build (dry run)...
echo.
echo To test the actual Docker build, run:
echo docker build -t brd-test .
echo.

pause
