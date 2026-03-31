# Check if email credentials are configured
Write-Host ""
Write-Host "🔍 KashGroww Email Configuration Status"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

$brevoKey = $env:BREVO_API_KEY
$brevoEmail = $env:BREVO_EMAIL
$gmailPass = $env:GMAIL_PASSWORD
$gmailEmail = $env:GMAIL_EMAIL

if ($brevoKey) {
    Write-Host "✅ BREVO_API_KEY is set" -ForegroundColor Green
    Write-Host "   Value: $($brevoKey.Substring(0, [Math]::Min(10, $brevoKey.Length)))..."
} else {
    Write-Host "❌ BREVO_API_KEY is NOT set" -ForegroundColor Red
}

if ($brevoEmail) {
    Write-Host "✅ BREVO_EMAIL is set" -ForegroundColor Green
    Write-Host "   Value: $brevoEmail"
} else {
    Write-Host "❌ BREVO_EMAIL is NOT set" -ForegroundColor Yellow
    Write-Host "   Using default: noreply@kashgroww.com"
}

if ($gmailPass) {
    Write-Host "✅ GMAIL_PASSWORD is set" -ForegroundColor Green
    Write-Host "   Value: $($gmailPass.Substring(0, [Math]::Min(10, $gmailPass.Length)))..."
} else {
    Write-Host "❌ GMAIL_PASSWORD is NOT set" -ForegroundColor Red
}

if ($gmailEmail) {
    Write-Host "✅ GMAIL_EMAIL is set" -ForegroundColor Green
    Write-Host "   Value: $gmailEmail"
} else {
    Write-Host "❌ GMAIL_EMAIL is NOT set" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ($brevoKey) {
    Write-Host "✅ Email service is CONFIGURED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run:"
    Write-Host "  streamlit run app.py"
} else {
    Write-Host "❌ No email service configured" -ForegroundColor Red
    Write-Host ""
    Write-Host "Quick setup:"
    Write-Host "  1. Go to: https://app.brevo.com"
    Write-Host "  2. Get SMTP Password from Settings → SMTP & API"
    Write-Host "  3. Run:"
    Write-Host "     setx BREVO_API_KEY 'your_password'"
    Write-Host "     setx BREVO_EMAIL 'your_email@domain.com'"
    Write-Host "  4. Close this PowerShell and open a NEW one"
    Write-Host "  5. Run: streamlit run app.py"
}

Write-Host ""
