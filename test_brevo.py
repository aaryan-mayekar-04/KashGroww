"""
Test Brevo Email Connection
Run this directly to test if emails can be sent via Brevo
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

API_KEY = st.secrets["BREVO_API_KEY"]

# Your Brevo credentials
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_LOGIN = "a69748001@smtp-brevo.com"
SMTP_PASSWORD = "xsmtpsib-fa71d7b81c218f32e55581ace4d84c00ac3ab4b67cb5cc5de7bb28628d654dce-z3Wjw2ksPFh4qmcu"

# Test email configuration
SENDER_EMAIL = "kashgroww@example.com"  # Try this first (change to your verified sender)
RECIPIENT_EMAIL = input("Enter your email to test: ")

print("\n" + "="*60)
print("🧪 Testing Brevo Email Connection")
print("="*60)

print(f"\n📝 Configuration:")
print(f"   SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
print(f"   Login: {SMTP_LOGIN}")
print(f"   From: {SENDER_EMAIL}")
print(f"   To: {RECIPIENT_EMAIL}")

try:
    print("\n📤 Connecting to Brevo...")
    context = ssl.create_default_context()
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        print("   ✅ Connected!")
        
        print("🔐 Starting TLS...")
        server.starttls(context=context)
        print("   ✅ TLS enabled!")
        
        print("🔑 Logging in...")
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        print("   ✅ Logged in!")
        
        # Create test email
        subject = "Test Email from KashGroww"
        html_body = """
        <html>
            <body>
                <h2>✅ Email Test Successful!</h2>
                <p>If you received this, your Brevo configuration is working correctly.</p>
                <p>You can now use KashGroww with email OTP support.</p>
            </body>
        </html>
        """
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = RECIPIENT_EMAIL
        message.attach(MIMEText(html_body, "html"))
        
        print("📧 Sending test email...")
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
        print("   ✅ Email sent!")
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Check your email inbox.")
        print("="*60)

except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTHENTICATION FAILED: {str(e)}")
    print("\n💡 Solutions:")
    print("   1. Check your SMTP password is correct from Brevo Settings → SMTP & API")
    print("   2. Try regenerating the SMTP password in Brevo")
    print("   3. Make sure your Brevo account is verified")
    print("   4. Try logging into Brevo web to confirm account works")

except smtplib.SMTPException as e:
    print(f"\n❌ SMTP ERROR: {str(e)}")
    print("\n💡 Solutions:")
    print("   1. Check your internet connection")
    print("   2. Try from a different network (not corporate WiFi)")
    print("   3. Your firewall might be blocking port 587")

except TimeoutError:
    print("\n❌ CONNECTION TIMEOUT")
    print("\n💡 Solutions:")
    print("   1. Check your internet connection")
    print("   2. Try from a different network")
    print("   3. Firewall might be blocking the connection")

except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
    print(f"   Error Type: {type(e).__name__}")

print("\n" + "="*60)
