# Gmail Configuration Guide for KashGroww OTP

## Problem
Gmail no longer allows "Less Secure Apps" access. You need to generate an App Password instead.

## Setup Steps

### 1. Enable 2-Factor Authentication (2FA)
- Go to: https://myaccount.google.com/
- Click **Security** (left sidebar)
- Scroll down to **2-Step Verification**
- Click **Enable 2-Step Verification** and follow the setup
- Verify with your phone number or authentication app

### 2. Generate Gmail App Password
- Go to: https://myaccount.google.com/apppasswords
- **Device**: Select "Windows Computer" (or your device type)
- **App**: Select "Other (custom name)" and type "KashGroww"
- Click **Generate**
- Google will show a 16-character password (looks like: `abcd efgh ijkl mnop`)

### 3. Update KashGroww Configuration
- Copy the 16-character password
- Open: `pages/1_Login.py`
- Find this line:
  ```python
  SENDER_PASSWORD = "KashGroww@2425"
  ```
- Replace it with your App Password (remove spaces):
  ```python
  SENDER_PASSWORD = "abcdefghijklmnop"  # Your 16-char App Password
  ```

### 4. Verify It Works
- Run the application:
  ```bash
  streamlit run app.py
  ```
- Try registration and the OTP should arrive in email

## Troubleshooting

### Issue: "Gmail authentication failed"
- ✅ Verify you enabled 2FA
- ✅ Check you copied the full 16-character App Password
- ✅ Ensure no extra spaces in the password
- ✅ Account must have 2FA enabled

### Issue: "Timeout or connection error"
- ✅ Check internet connection
- ✅ Firewall might be blocking SMTP (port 587)
- ✅ Try with a different network

### Issue: Email goes to spam
- ✅ Add sender email to contacts
- ✅ Check spam/promotions folder

## Current Configuration
```
SMTP Server: smtp.gmail.com
Port: 587
Security: TLS (STARTTLS)
```

## Alternative: Use Different Email Provider

If Gmail continues to have issues, you can switch to:

### **SendGrid** (Free tier available)
```python
SMTP_SERVER = "smtp.sendgrid.net"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@yourdomain.com"
SENDER_PASSWORD = "SG.your_sendgrid_api_key"
```

### **Brevo** (Free tier: 300/day)
```python
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SENDER_EMAIL = "noreply@kashgroww.com"
SENDER_PASSWORD = "your_brevo_api_key"
```

## Security Note
⚠️ **Never commit password to git!** For production:
- Store password in environment variables
- Use `.env` file with `python-dotenv`
- Use cloud secrets manager

```python
import os
from dotenv import load_dotenv

load_dotenv()
SENDER_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
```

