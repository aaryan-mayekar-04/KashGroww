# KashGroww Email Setup Script (PowerShell)
# Run this script to configure your email provider

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "╔════════════════════════════════════════╗"
    Write-Host "║   KashGroww Email Configuration       ║"
    Write-Host "╚════════════════════════════════════════╝"
    Write-Host ""
    Write-Host "Choose your email provider:"
    Write-Host ""
    Write-Host "  1. Brevo (Recommended ⭐ - Free 300 emails/day)"
    Write-Host "  2. Gmail (Requires App Password)"
    Write-Host "  3. Demo Mode (Show OTP in UI for testing)"
    Write-Host ""
    Write-Host "Enter your choice [1-3]: " -NoNewline
}

function Setup-Brevo {
    Clear-Host
    Write-Host ""
    Write-Host "╔════════════════════════════════════════╗"
    Write-Host "║        BREVO SETUP                    ║"
    Write-Host "╚════════════════════════════════════════╝"
    Write-Host ""
    Write-Host "Step 1: Create a Brevo account"
    Write-Host "  Visit: https://app.brevo.com"
    Write-Host "  Sign up and verify your email"
    Write-Host ""
    Write-Host "Step 2: Get SMTP credentials"
    Write-Host "  - Login to Brevo Dashboard"
    Write-Host "  - Go to Settings → SMTP & API"
    Write-Host "  - Copy your SMTP Login and SMTP Password"
    Write-Host ""
    Write-Host "Press Enter to continue..." -ForegroundColor Green
    Read-Host

    $brevoKey = Read-Host "Paste your Brevo SMTP Password (this is the important one)"
    $brevoEmail = Read-Host "Paste your Brevo Sender Email"

    Write-Host ""
    Write-Host "Setting environment variables..." -ForegroundColor Yellow

    [Environment]::SetEnvironmentVariable("BREVO_API_KEY", $brevoKey, "User")
    [Environment]::SetEnvironmentVariable("BREVO_EMAIL", $brevoEmail, "User")

    Write-Host ""
    Write-Host "✅ Brevo credentials saved!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Registered Environment Variables:"
    Write-Host "  BREVO_API_KEY = $brevoKey"
    Write-Host "  BREVO_EMAIL = $brevoEmail"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Restart any open PowerShell windows"
    Write-Host "  2. Run: streamlit run app.py"
    Write-Host "  3. Try registering - OTP should arrive in email"
    Write-Host ""
    Write-Host "Press Enter to finish..." -ForegroundColor Green
    Read-Host
}

function Setup-Gmail {
    Clear-Host
    Write-Host ""
    Write-Host "╔════════════════════════════════════════╗"
    Write-Host "║        GMAIL SETUP                    ║"
    Write-Host "╚════════════════════════════════════════╝"
    Write-Host ""
    Write-Host "Step 1: Enable 2-Factor Authentication"
    Write-Host "  Visit: https://myaccount.google.com/security"
    Write-Host "  Scroll to 'How you sign in to Google'"
    Write-Host "  Click '2-Step Verification' and enable it"
    Write-Host ""
    Write-Host "Step 2: Generate App Password"
    Write-Host "  Visit: https://myaccount.google.com/apppasswords"
    Write-Host "  - Device: Windows Computer"
    Write-Host "  - App: Other (custom name)"
    Write-Host "  - Type: 'KashGroww'"
    Write-Host "  - Click Generate"
    Write-Host "  - Copy the 16-character password (remove spaces)"
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Use the 16-character App Password, NOT your regular password!"
    Write-Host ""
    Write-Host "Press Enter to continue..." -ForegroundColor Green
    Read-Host

    $gmailPass = Read-Host "Paste your Gmail App Password (16 characters, no spaces)"
    $gmailEmail = Read-Host "Paste your Gmail email address"

    Write-Host ""
    Write-Host "Setting environment variables..." -ForegroundColor Yellow

    [Environment]::SetEnvironmentVariable("GMAIL_PASSWORD", $gmailPass, "User")
    [Environment]::SetEnvironmentVariable("GMAIL_EMAIL", $gmailEmail, "User")

    Write-Host ""
    Write-Host "✅ Gmail credentials saved!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Registered Environment Variables:"
    Write-Host "  GMAIL_PASSWORD = $gmailPass"
    Write-Host "  GMAIL_EMAIL = $gmailEmail"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Restart any open PowerShell windows"
    Write-Host "  2. Edit pages/1_Login.py: change USE_BREVO = False"
    Write-Host "  3. Run: streamlit run app.py"
    Write-Host "  4. Try registering - OTP should arrive in email"
    Write-Host ""
    Write-Host "Press Enter to finish..." -ForegroundColor Green
    Read-Host
}

function Setup-DemoMode {
    Clear-Host
    Write-Host ""
    Write-Host "╔════════════════════════════════════════╗"
    Write-Host "║        DEMO MODE SETUP                ║"
    Write-Host "╚════════════════════════════════════════╝"
    Write-Host ""
    Write-Host "Demo Mode enabled! OTP will display in the UI."
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Edit pages/1_Login.py"
    Write-Host "  2. Set: DEMO_MODE = True"
    Write-Host "  3. Run: streamlit run app.py"
    Write-Host "  4. Try registering - OTP will show in the app"
    Write-Host ""
    Write-Host "Press Enter to finish..." -ForegroundColor Green
    Read-Host
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host

    switch ($choice) {
        "1" {
            Setup-Brevo
        }
        "2" {
            Setup-Gmail
        }
        "3" {
            Setup-DemoMode
        }
        default {
            Write-Host "Invalid choice. Please try again." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }

} while ($true)
