"""
KashGroww — Brevo SMTP Diagnostic Script
=========================================
Run this from your project root:
    python diagnose_brevo.py

It will tell you EXACTLY what is failing and why.
"""

import socket
import ssl
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

API_KEY = st.secrets["BREVO_API_KEY"]

# ── PASTE YOUR CREDENTIALS HERE (only for this test) ──────────────────────
SMTP_USER    = "a69748001@smtp-brevo.com"
SMTP_PASS    = "xsmtpsib-fa71d7b81c218f32e55581ace4d84c00ac3ab4b67cb5cc5de7bb28628d654dce-z3Wjw2ksPFh4qmcu"
SENDER_EMAIL = "a69748001@smtp-brevo.com"
SENDER_NAME  = "KashGroww"
TEST_TO      = "aaryanmayekar04@gmail.com"     # where to send the test OTP
# ──────────────────────────────────────────────────────────────────────────

SMTP_SERVER  = "smtp-relay.brevo.com"
PORTS        = [587, 465, 25]

SEP = "─" * 55

def ok(msg):  print(f"  ✅  {msg}")
def fail(msg): print(f"  ❌  {msg}")
def info(msg): print(f"  ℹ️   {msg}")
def head(msg): print(f"\n{SEP}\n  {msg}\n{SEP}")


# ── STEP 1: DNS resolution ─────────────────────────────────────────────────
head("STEP 1 — DNS resolution")
try:
    ip = socket.gethostbyname(SMTP_SERVER)
    ok(f"Resolved {SMTP_SERVER} → {ip}")
except socket.gaierror as e:
    fail(f"DNS failed: {e}")
    print("\n  FIX: You have no internet connection, or DNS is blocked.")
    print("  Try: ping google.com — if that fails too, fix your network first.")
    sys.exit(1)


# ── STEP 2: Port reachability ─────────────────────────────────────────────
head("STEP 2 — Port connectivity")
open_ports = []
for port in PORTS:
    try:
        s = socket.create_connection((SMTP_SERVER, port), timeout=8)
        s.close()
        ok(f"Port {port} is OPEN")
        open_ports.append(port)
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        fail(f"Port {port} BLOCKED — {e}")

if not open_ports:
    print("\n  FIX: All SMTP ports are blocked.")
    print("  This usually means your ISP or college/office network blocks outbound SMTP.")
    print("  Solutions:")
    print("    1. Switch to mobile hotspot and re-run this script")
    print("    2. Use Brevo HTTP API instead (see bottom of this script)")
    sys.exit(1)

USE_PORT = open_ports[0]
info(f"Will use port {USE_PORT} for the rest of the test")


# ── STEP 3: TLS handshake ─────────────────────────────────────────────────
head("STEP 3 — TLS / STARTTLS handshake")
context = ssl.create_default_context()
try:
    with smtplib.SMTP(SMTP_SERVER, USE_PORT, timeout=10) as server:
        server.ehlo()
        if USE_PORT == 587:
            server.starttls(context=context)
            server.ehlo()
            ok("STARTTLS succeeded on port 587")
        else:
            ok(f"Connected on port {USE_PORT}")
except ssl.SSLError as e:
    fail(f"TLS handshake failed: {e}")
    print("\n  FIX: SSL certificate issue. Try updating Python/certifi:")
    print("    pip install --upgrade certifi")
    sys.exit(1)
except Exception as e:
    fail(f"Connection error: {e}")
    sys.exit(1)


# ── STEP 4: SMTP authentication ───────────────────────────────────────────
head("STEP 4 — Brevo SMTP authentication")
try:
    with smtplib.SMTP(SMTP_SERVER, USE_PORT, timeout=10) as server:
        server.ehlo()
        if USE_PORT == 587:
            server.starttls(context=context)
            server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        ok(f"Logged in as {SMTP_USER}")
except smtplib.SMTPAuthenticationError as e:
    fail(f"Authentication rejected: {e}")
    print("\n  FIX: Your SMTP credentials are wrong or expired.")
    print("  Steps to fix:")
    print("    1. Go to https://app.brevo.com")
    print("    2. Click your profile (top-right) → SMTP & API")
    print("    3. Under the SMTP tab, click 'Generate a new SMTP password'")
    print("    4. Copy the new password and update:")
    print("       → SMTP_PASS in this file")
    print("       → smtp_pass in .streamlit/secrets.toml")
    sys.exit(1)
except Exception as e:
    fail(f"Unexpected error during login: {e}")
    sys.exit(1)


# ── STEP 5: Sender verification check ────────────────────────────────────
head("STEP 5 — Sender address check")
info(f"Sender set to: {SENDER_EMAIL}")
info("Make sure this email is verified in Brevo:")
info("  app.brevo.com → Senders & IP → Senders → Add / verify")
if "gmail.com" in SENDER_EMAIL:
    print()
    print("  ⚠️  WARNING: Gmail addresses as senders are blocked by Gmail's")
    print("     DMARC policy when sent via third-party SMTP relays.")
    print("     Your email may be silently dropped before it reaches inbox.")
    print()
    print("  RECOMMENDED FIX (pick one):")
    print("    A) Use Brevo's free verified address: onboarding@resend.dev")
    print("       → Change SENDER_EMAIL above to: onboarding@resend.dev")
    print("    B) Buy a cheap domain (₹500/yr) and verify it in Brevo")
    print("       → Full inbox delivery, professional look")
else:
    ok(f"{SENDER_EMAIL} is a custom domain — good for deliverability")


# ── STEP 6: Send actual test email ────────────────────────────────────────
head("STEP 6 — Sending test OTP email")
TEST_OTP = "482910"

msg = MIMEMultipart("alternative")
msg["Subject"] = "KashGroww — Test OTP"
msg["From"]    = f"{SENDER_NAME} <{SENDER_EMAIL}>"
msg["To"]      = TEST_TO
msg["Reply-To"] = SENDER_EMAIL

plain = f"Your KashGroww test OTP is: {TEST_OTP}\n\nThis is a diagnostic test email."
html  = f"""
<div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:32px;">
  <h2 style="color:#16a34a;">KashGroww</h2>
  <p>Your test OTP is:</p>
  <div style="font-size:40px;font-weight:700;letter-spacing:10px;
              background:#f0fdf4;padding:20px;text-align:center;
              border-radius:8px;color:#15803d;">{TEST_OTP}</div>
  <p style="color:#999;font-size:12px;margin-top:16px;">
    Diagnostic test — ignore if unexpected.
  </p>
</div>
"""

msg.attach(MIMEText(plain, "plain"))
msg.attach(MIMEText(html,  "html"))

try:
    with smtplib.SMTP(SMTP_SERVER, USE_PORT, timeout=10) as server:
        server.ehlo()
        if USE_PORT == 587:
            server.starttls(context=context)
            server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SENDER_EMAIL, TEST_TO, msg.as_string())
    ok(f"Email sent to {TEST_TO}!")
    print()
    print("  Now check:")
    print(f"    → {TEST_TO} inbox")
    print(f"    → Spam / Promotions folder")
    print(f"    → Brevo dashboard: app.brevo.com → Transactional → Email Logs")
    print(f"      The log shows EXACTLY what Gmail did with the email.")
except smtplib.SMTPSenderRefused as e:
    fail(f"Sender refused: {e}")
    print(f"\n  FIX: '{SENDER_EMAIL}' is not verified in Brevo.")
    print("  Go to: app.brevo.com → Senders & IP → Senders → Add & verify it")
except smtplib.SMTPRecipientsRefused as e:
    fail(f"Recipient refused: {e}")
    print(f"\n  FIX: '{TEST_TO}' was rejected. Check the address is correct.")
except Exception as e:
    fail(f"Send failed: {e}")


# ── SUMMARY ───────────────────────────────────────────────────────────────
head("SUMMARY")
print("  If Step 6 succeeded but email never arrives:")
print("  1. Check Brevo Email Logs for status (Delivered / Blocked / Spam)")
print("  2. If 'Delivered' but not in inbox → sender domain issue (Gmail DMARC)")
print("  3. If 'Blocked' → sender not verified in Brevo")
print()
print("  If any step FAILED, follow the FIX instructions printed above.")
print()
print(SEP)