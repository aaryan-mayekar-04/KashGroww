# KashGroww Email OTP Setup Guide

## Quick Start (Easiest Option)

### Option 1: Use Brevo (Recommended ⭐)
Free tier: **300 emails per day**

**Step 1: Create Brevo Account**
1. Visit: https://app.brevo.com
2. Sign up with your email
3. Complete verification

**Step 2: Get SMTP Credentials**
1. Login to Brevo Dashboard
2. Go to **Settings → SMTP & API**
3. Copy your **SMTP Login** and **SMTP Password**

**Step 3: Configure KashGroww**

#### Option A: Using Batch Script (Easiest for Windows)
```batch
Double-click: setup_email.bat
Follow the prompts and paste your Brevo credentials
Run: streamlit run app.py
```

#### Option B: Manual Environment Variables
```powershell
# In PowerShell (run as Administrator)
setx BREVO_API_KEY "your_brevo_smtp_password"
setx BREVO_EMAIL "your_email@brevo-email.com"

# Then run
streamlit run app.py
```

**Step 4: Verify Setup**
- Go to "Create account" tab
- You should see ✅ **Brevo Email Service** - Active
- Try registering with an email address
- OTP should arrive in inbox

---

## Option 2: Use Gmail

Gmail requires an **App Password** (not your regular Gmail password).

**Step 1: Enable 2-Factor Authentication**
1. Go to: https://myaccount.google.com/security
2. Scroll to "How you sign in to Google"
3. Click **2-Step Verification**
4. Follow setup steps with your phone

**Step 2: Generate App Password**
1. Go to: https://myaccount.google.com/apppasswords
2. **Device**: Select "Windows Computer" (or your device type)
3. **App**: Select "Other (custom name)"
4. Type: `KashGroww`
5. Click **Generate**
6. ⚠️ Google shows a 16-character password like: `abcd efgh ijkl mnop`
7. Copy this password (remove spaces)

**Step 3: Configure KashGroww**

#### Option A: Using Batch Script
```batch
Double-click: setup_email.bat
Choose option 2 (Gmail)
Paste your 16-character App Password (no spaces)
Paste your Gmail email address
Run: streamlit run app.py
```

#### Option B: Manual Environment Variables
```powershell
# In PowerShell (run as Administrator)
setx GMAIL_PASSWORD "abcdefghijklmnop"
setx GMAIL_EMAIL "your.email@gmail.com"

# Then run
streamlit run app.py
```

---

## Option 3: Demo Mode (Testing Only)

If you want to **test registration without email**:

**Edit** [pages/1_Login.py](pages/1_Login.py):
```python
DEMO_MODE = True  # Set to True
```

Now OTP will display in the UI instead of being sent via email.

---

## Troubleshooting

### Problem: "Gmail authentication failed"
✅ **Solutions:**
1. Verify 2FA is enabled at https://myaccount.google.com/security
2. You're using App Password (not regular password)
3. Copy the full 16 characters (remove spaces)
4. Restart PowerShell after setting environment variables
5. Try Brevo instead (easier setup)

### Problem: "Brevo authentication failed"
✅ **Solutions:**
1. Verify SMTP password (not SMTP login username)
2. Check email domain at https://app.brevo.com
3. Login again and copy password carefully
4. Try Gmail instead

### Problem: Email doesn't arrive
✅ **Solutions:**
1. Check spam/promotions folder
2. Check email filter settings
3. Verify recipient email is correct
4. Try resending OTP using "Resend" button

### Problem: Connection timeout
✅ **Solutions:**
1. Check internet connection
2. Firewall might be blocking SMTP port 587
3. Try switching to different WiFi/network
4. Contact your network administrator

---

## What's the Difference?

| Feature | Brevo | Gmail | Demo Mode |
|---------|-------|-------|-----------|
| Setup Difficulty | ⭐ Easy | ⭐⭐⭐ Hard | ⭐ Very Easy |
| Free Tier | 300/day | Unlimited | N/A |
| Auth Required | App Password | Gmail App Password | None |
| 2FA Required | No | Yes | No |
| Best For | Production | Personal | Testing |

---

## Advanced: Using .env File

1. Copy `.env.example` to `.env`
2. Fill in your credentials
3. Run: `pip install python-dotenv`
4. Edit `pages/1_Login.py` to use:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## Security Best Practices

⚠️ **NEVER:**
- Commit `.env` file to Git
- Share your App Password with others
- Use production emails for testing

✅ **DO:**
- Keep passwords in environment variables
- Use `.gitignore` to exclude `.env`
- Rotate passwords regularly
- Use separate email for development vs production

---

## Still Having Issues?

Try these steps in order:

1. **Clear cache**: Close browser, empty cache, reopen
2. **Restart Streamlit**: Stop (Ctrl+C) and run `streamlit run app.py` again
3. **Check logs**: Look for error messages in terminal
4. **Switch providers**: Try the other service
5. **Use Demo Mode**: Test the app with Demo Mode enabled
6. **Contact support**: Reach out to the team

---

## Integration Code

Current configuration in `pages/1_Login.py`:

```python
USE_BREVO = True      # Set to True for Brevo, False for Gmail
DEMO_MODE = False     # Set to True to show OTP in UI (no email)
```

Environment variables checked:
- `BREVO_API_KEY` - Brevo SMTP password
- `BREVO_EMAIL` - Brevo sender email
- `GMAIL_PASSWORD` - Gmail App Password
- `GMAIL_EMAIL` - Gmail sender email

---

**Last Updated:** March 2026  
**Status:** Production Ready ✅
