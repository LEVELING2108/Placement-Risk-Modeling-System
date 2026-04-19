@echo off
echo ======================================================================
echo   PLACEMENT-RISK MODELING SYSTEM - QUICK START
echo ======================================================================
echo.

echo Running validation...
python validate_setup.py
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Validation failed! Check the errors above.
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" (
        echo Startup cancelled.
        pause
        exit /b 1
    )
)

echo.
echo ======================================================================
echo   STARTING SERVER
echo ======================================================================
echo.
echo Server: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause
