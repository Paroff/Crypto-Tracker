@echo off
:: ============================================================
::  BTC Ticker - Windows Auto-Start Installer
::  Double-click to install / uninstall
:: ============================================================

set "APP_NAME=BTC_Ticker"
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%BTC_ticker.pyw"
set "REG_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Download Python at https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Install dependencies if needed
echo Installing dependencies...
pip install requests --quiet

:: Check if already set to start automatically
reg query "%REG_KEY%" /v "%APP_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo [INFO] BTC Ticker is already configured to start automatically.
    echo Do you want to UNINSTALL it? (Y/N)
    set /p CHOICE="> "
    if /i "%CHOICE%"=="Y" (
        reg delete "%REG_KEY%" /v "%APP_NAME%" /f
        echo [OK] Removed from Windows startup.
    ) else (
        echo [INFO] No changes made.
    )
) else (
    :: Add to startup
    reg add "%REG_KEY%" /v "%APP_NAME%" /t REG_SZ /d "pythonw \"%SCRIPT_PATH%\"" /f
    if %errorlevel% equ 0 (
        echo.
        echo [OK] BTC Ticker will launch automatically at Windows startup.
        echo.
        echo Launch now? (Y/N)
        set /p RUN="> "
        if /i "%RUN%"=="Y" (
            start "" pythonw "%SCRIPT_PATH%"
            echo [OK] BTC Ticker started!
        )
    ) else (
        echo [ERROR] Unable to add to the registry.
    )
)

echo.
pause
