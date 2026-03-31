@echo off
REM KashGroww Email Setup Helper Script
REM This script helps configure email OTP authentication

echo.
echo ====================================
echo   KashGroww Email Configuration
echo ====================================
echo.

setlocal enabledelayedexpansion

echo Choose your email provider:
echo.
echo 1. Brevo (Recommended - Free 300 emails/day)
echo 2. Gmail (Requires App Password)
echo 3. Demo Mode (Show OTP in UI for testing)
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto brevo_setup
if "%choice%"=="2" goto gmail_setup
if "%choice%"=="3" goto demo_mode
echo Invalid choice. Exiting.
exit /b

:brevo_setup
echo.
echo ========== BREVO SETUP ==========
echo.
echo Step 1: Create a Brevo account
echo Visit: https://app.brevo.com
echo.
echo Step 2: Get SMTP credentials
echo - Login to Brevo
echo - Go to Settings ^> SMTP ^& API
echo - Copy your SMTP Login and SMTP Password
echo.
set /p brevo_api="Paste your Brevo SMTP Password: "
set /p brevo_email="Paste your Brevo Email: "

setx BREVO_API_KEY "%brevo_api%"
setx BREVO_EMAIL "%brevo_email%"

echo.
echo ✅ Brevo credentials saved!
echo.
echo Now run: streamlit run app.py
echo.
pause
exit /b

:gmail_setup
echo.
echo ========== GMAIL SETUP ==========
echo.
echo Step 1: Enable 2-Factor Authentication
echo Visit: https://myaccount.google.com/security
echo - Scroll to "How you sign in to Google"
echo - Click "2-Step Verification" and enable it
echo.
echo Step 2: Generate App Password
echo Visit: https://myaccount.google.com/apppasswords
echo - Device: Windows Computer
echo - App: Other (custom name) "KashGroww"
echo - Click Generate
echo - Copy the 16-character password (remove spaces)
echo.
set /p gmail_pass="Paste your Gmail App Password (16 chars, no spaces): "
set /p gmail_email="Paste your Gmail email address: "

setx GMAIL_PASSWORD "%gmail_pass%"
setx GMAIL_EMAIL "%gmail_email%"

echo.
echo ✅ Gmail credentials saved!
echo.
echo Now run: streamlit run app.py
echo.
pause
exit /b

:demo_mode
echo.
echo ========== DEMO MODE ==========
echo Credentials not needed. OTP will show in UI.
echo.
echo Run: streamlit run app.py
echo.
pause
exit /b
