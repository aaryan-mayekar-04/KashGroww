import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import random
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db.crud import (
    create_user, get_user, verify_password,
    email_exists, get_user_by_email, reset_password
)

# ── BREVO SMTP CONFIGURATION ────────────────────────────────────────────────
#
#  Store credentials in .streamlit/secrets.toml (NEVER hardcode them here):
#
#  [brevo]
#  smtp_user     = "a69748001@smtp-brevo.com"   ← your Brevo SMTP login
#  smtp_pass     = "xsmtpsib-xxxxxxxxxxxx"       ← from Brevo → SMTP & API
#  sender_email  = "kashgrowwofficial@gmail.com" ← verified sender in Brevo
#  sender_name   = "KashGroww"
#
# ────────────────────────────────────────────────────────────────────────────

BREVO_SMTP_SERVER = "smtp-relay.brevo.com"
BREVO_SMTP_PORT   = 587
MAX_RETRIES       = 2
OTP_EXPIRY_SECS   = 600  # 10 minutes


def _get_brevo_config():
    """Load Brevo credentials from st.secrets. Returns None if not configured."""
    try:
        cfg = st.secrets["brevo"]
        return {
            "smtp_user":    cfg["smtp_user"],
            "smtp_pass":    cfg["smtp_pass"],
            "sender_email": cfg["sender_email"],
            "sender_name":  cfg.get("sender_name", "KashGroww"),
        }
    except (KeyError, FileNotFoundError):
        return None


def _build_email(recipient_email: str, otp: str, user_name: str, cfg: dict):
    """Construct the MIMEMultipart email message."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "KashGroww — Your Verification Code"
    msg["From"]    = f"{cfg['sender_name']} <{cfg['sender_email']}>"
    msg["To"]      = recipient_email
    msg["Reply-To"] = cfg["sender_email"]

    plain = (
        f"Hi {user_name},\n\n"
        f"Your KashGroww verification code is: {otp}\n\n"
        f"This code expires in 10 minutes. Do not share it with anyone.\n\n"
        f"— KashGroww Team"
    )

    html = f"""
    <html>
      <body style="font-family:Arial,sans-serif;background:#f4f7fa;padding:20px;margin:0;">
        <div style="max-width:480px;margin:auto;background:#fff;border-radius:10px;
                    padding:32px;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
          <h2 style="color:#16a34a;margin:0 0 4px;">KashGroww</h2>
          <p style="color:#888;font-size:13px;margin:0 0 24px;">Smart Investment Planning</p>
          <p style="color:#444;font-size:15px;">Hi <strong>{user_name}</strong>,</p>
          <p style="color:#444;font-size:15px;">Your verification code is:</p>
          <div style="background:#f0fdf4;border:2px dashed #16a34a;border-radius:8px;
                      padding:20px;text-align:center;margin:20px 0;">
            <span style="font-size:40px;font-weight:700;letter-spacing:10px;
                         color:#15803d;font-family:'Courier New',monospace;">
              {otp}
            </span>
          </div>
          <p style="color:#dc2626;font-size:13px;">
            <strong>⚠️ Expires in 10 minutes.</strong> Do not share this code with anyone.
          </p>
          <p style="color:#999;font-size:12px;">
            If you didn't request this, you can safely ignore this email.
          </p>
          <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;">
          <p style="color:#bbb;font-size:11px;text-align:center;margin:0;">
            KashGroww Team · Smart Investment Planning
          </p>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))
    return msg


def send_otp_email(recipient_email: str, otp: str, user_name: str):
    """
    Send OTP via Brevo SMTP relay.

    Returns:
        (True,  success_message)  on success
        (False, error_message)    on failure
    """
    cfg = _get_brevo_config()

    if cfg is None:
        return False, (
            "❌ Brevo credentials not configured. "
            "Add [brevo] section to .streamlit/secrets.toml."
        )

    msg = _build_email(recipient_email, otp, user_name, cfg)
    context = ssl.create_default_context()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with smtplib.SMTP(BREVO_SMTP_SERVER, BREVO_SMTP_PORT, timeout=15) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                # ✅ Login with SMTP user (not sender email) — critical for Brevo
                server.login(cfg["smtp_user"], cfg["smtp_pass"])
                server.sendmail(cfg["sender_email"], recipient_email, msg.as_string())

            return True, "✅ OTP sent to your email!"

        except smtplib.SMTPAuthenticationError:
            if attempt == MAX_RETRIES:
                return False, (
                    "❌ Brevo authentication failed. "
                    "Check smtp_user and smtp_pass in your secrets.toml. "
                    "The password is from Brevo → Settings → SMTP & API, "
                    "not your Brevo account password."
                )

        except smtplib.SMTPRecipientsRefused:
            return False, f"❌ Recipient address refused: {recipient_email}"

        except (smtplib.SMTPException, TimeoutError, OSError) as e:
            if attempt == MAX_RETRIES:
                return False, (
                    f"❌ Could not send email after {MAX_RETRIES} attempts. "
                    f"Check your internet connection and firewall (port 587). "
                    f"Detail: {e}"
                )

    return False, "❌ Failed to send OTP. Please try again."


# ── OTP HELPERS ─────────────────────────────────────────────────────────────

def _generate_otp() -> str:
    return str(random.randint(100000, 999999))


def _otp_expired(ts_key: str) -> bool:
    """Return True if OTP timestamp stored under ts_key has passed expiry."""
    sent_at = st.session_state.get(ts_key)
    if sent_at is None:
        return True
    return (time.time() - sent_at) > OTP_EXPIRY_SECS


def _send_and_store(email: str, name: str, otp_key: str, ts_key: str, attempts_key: str):
    """Generate OTP, send it, and store in session_state. Returns (success, message)."""
    otp = _generate_otp()
    success, message = send_otp_email(email, otp, name)
    if success:
        st.session_state[otp_key]      = otp
        st.session_state[ts_key]       = time.time()
        st.session_state[attempts_key] = 0
    return success, message


# ── PAGE SETUP ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="Login — KashGroww", page_icon="💸")
st.title("KashGroww 💸")
st.header("Sign in or Create a new account")

tab_login, tab_reg, tab_forgot = st.tabs(["Sign in", "Create account", "Forgot password"])


# ── SIGN IN ──────────────────────────────────────────────────────────────────

with tab_login:
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Sign in", type="primary", use_container_width=True):
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            user = get_user(username)
            if user and verify_password(password, user.password): # type: ignore
                st.session_state["logged_in"] = True
                st.session_state["user_id"]   = user.id
                st.session_state["username"]  = user.username
                st.session_state["name"]      = user.name
                st.success("Login successful!")
                st.switch_page("pages/2_Profile.py")
            else:
                st.error("Incorrect username or password.")


# ── REGISTER ─────────────────────────────────────────────────────────────────

with tab_reg:
    if "reg_step" not in st.session_state:
        st.session_state.reg_step = 1

    st.progress(st.session_state.reg_step / 3,
                text=f"Step {st.session_state.reg_step} of 3")

    # ── STEP 1: Personal details ──
    if st.session_state.reg_step == 1:
        st.subheader("📝 Personal information")
        r_name  = st.text_input("Full name",      key="reg_name_input")
        r_email = st.text_input("Email address",  key="reg_email_input")
        r_phone = st.text_input("Phone number",   key="reg_phone_input")

        if st.button("Continue →", use_container_width=True):
            if not all([r_name, r_email, r_phone]):
                st.error("Please fill in all fields.")
            elif email_exists(r_email):
                st.error("This email is already registered.")
            else:
                with st.spinner("Sending OTP to your email…"):
                    ok, msg = _send_and_store(
                        r_email, r_name,
                        otp_key="reg_otp", ts_key="reg_otp_ts",
                        attempts_key="reg_otp_attempts"
                    )

                if ok:
                    st.session_state.r_name  = r_name
                    st.session_state.r_email = r_email
                    st.session_state.r_phone = r_phone
                    st.session_state.reg_step = 2
                    st.success(msg)
                    st.info("Check your inbox (and spam folder) for the 6-digit OTP.")
                    st.rerun()
                else:
                    st.error(msg)

    # ── STEP 2: OTP verification ──
    elif st.session_state.reg_step == 2:
        st.subheader("✉️ Verify your email")
        st.caption(f"OTP sent to: **{st.session_state.r_email}**")

        if _otp_expired("reg_otp_ts"):
            st.warning("⏰ Your OTP has expired. Please request a new one.")

        entered = st.text_input("Enter 6-digit OTP", max_chars=6,
                                placeholder="000000", key="reg_otp_input")

        if st.button("Verify OTP", type="primary", use_container_width=True):
            if not entered:
                st.error("Please enter the OTP.")
            elif len(entered) != 6 or not entered.isdigit():
                st.error("OTP must be exactly 6 digits.")
            elif _otp_expired("reg_otp_ts"):
                st.error("OTP has expired. Please resend.")
            elif entered == st.session_state.get("reg_otp"):
                st.session_state.reg_step = 3
                st.success("✅ Email verified!")
                st.rerun()
            else:
                st.session_state.reg_otp_attempts = st.session_state.get("reg_otp_attempts", 0) + 1
                remaining = 5 - st.session_state.reg_otp_attempts
                if remaining > 0:
                    st.error(f"Incorrect OTP. {remaining} attempt(s) remaining.")
                else:
                    st.error("Too many failed attempts. Please start over.")
                    if st.button("Start over", use_container_width=True):
                        st.session_state.reg_step = 1
                        st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Resend OTP", use_container_width=True):
                with st.spinner("Sending new OTP…"):
                    ok, msg = _send_and_store(
                        st.session_state.r_email, st.session_state.r_name,
                        otp_key="reg_otp", ts_key="reg_otp_ts",
                        attempts_key="reg_otp_attempts"
                    )
                if ok:
                    st.success("New OTP sent! Check your inbox.")
                else:
                    st.error(msg)
        with col2:
            if st.button("← Go back", use_container_width=True):
                st.session_state.reg_step = 1
                st.rerun()

    # ── STEP 3: Create credentials ──
    elif st.session_state.reg_step == 3:
        st.subheader("🔑 Create Your Account")
        r_uname = st.text_input("Choose a username", key="reg_uname")
        r_pw1   = st.text_input("Password (min 8 characters)", type="password", key="reg_pw1")
        r_pw2   = st.text_input("Confirm password",            type="password", key="reg_pw2")

        if r_pw1 and len(r_pw1) < 8:
            st.warning("Password must be at least 8 characters.")
        if r_pw1 and r_pw2 and r_pw1 != r_pw2:
            st.error("Passwords do not match.")

        if st.button("Create account", type="primary", use_container_width=True):
            if not r_uname:
                st.error("Please choose a username.")
            elif len(r_pw1) < 8:
                st.error("Password must be at least 8 characters.")
            elif r_pw1 != r_pw2:
                st.error("Passwords do not match.")
            else:
                create_user(
                    name           = st.session_state.r_name,
                    email          = st.session_state.r_email,
                    phone          = st.session_state.r_phone,
                    username       = r_uname,
                    plain_password = r_pw1,
                )
                st.success("✅ Account created! Please sign in.")
                st.session_state.reg_step = 1
                st.balloons()


# ── FORGOT PASSWORD ───────────────────────────────────────────────────────────

with tab_forgot:
    st.subheader("🔐 Reset Your Password")

    if "forgot_step" not in st.session_state:
        st.session_state.forgot_step = 1

    st.progress(st.session_state.forgot_step / 3,
                text=f"Step {st.session_state.forgot_step} of 3")

    # ── STEP 1: Enter email ──
    if st.session_state.forgot_step == 1:
        st.caption("Enter the email address linked to your KashGroww account.")
        forgot_email = st.text_input("Email address", key="forgot_email_input")

        if st.button("Send OTP", use_container_width=True):
            if not forgot_email:
                st.error("Please enter your email address.")
            else:
                user = get_user_by_email(forgot_email)
                if not user:
                    st.error("No account found with that email address.")
                else:
                    with st.spinner("Sending OTP…"):
                        ok, msg = _send_and_store(
                            forgot_email, user.name,
                            otp_key="forgot_otp", ts_key="forgot_otp_ts",
                            attempts_key="forgot_otp_attempts"
                        )

                    if ok:
                        st.session_state.forgot_email   = forgot_email
                        st.session_state.forgot_user_id = user.id
                        st.session_state.forgot_step    = 2
                        st.success(msg)
                        st.info("Check your inbox (and spam folder) for the 6-digit OTP.")
                        st.rerun()
                    else:
                        st.error(msg)

    # ── STEP 2: Verify OTP ──
    elif st.session_state.forgot_step == 2:
        st.subheader("✉️ Verify Your Email")
        st.caption(f"OTP sent to: **{st.session_state.forgot_email}**")

        if _otp_expired("forgot_otp_ts"):
            st.warning("⏰ Your OTP has expired. Please request a new one.")

        entered_otp = st.text_input("Enter 6-digit OTP", max_chars=6,
                                    placeholder="000000", key="forgot_otp_input")

        if st.button("Verify OTP", type="primary", use_container_width=True):
            if not entered_otp:
                st.error("Please enter the OTP.")
            elif len(entered_otp) != 6 or not entered_otp.isdigit():
                st.error("OTP must be exactly 6 digits.")
            elif _otp_expired("forgot_otp_ts"):
                st.error("OTP has expired. Please resend.")
            elif entered_otp == st.session_state.get("forgot_otp"):
                st.session_state.forgot_step = 3
                st.success("✅ Email verified!")
                st.rerun()
            else:
                st.session_state.forgot_otp_attempts = (
                    st.session_state.get("forgot_otp_attempts", 0) + 1
                )
                remaining = 5 - st.session_state.forgot_otp_attempts
                if remaining > 0:
                    st.error(f"Incorrect OTP. {remaining} attempt(s) remaining.")
                else:
                    st.error("Too many failed attempts. Please start over.")
                    if st.button("Start over", use_container_width=True, key="forgot_restart"):
                        st.session_state.forgot_step = 1
                        st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Resend OTP", use_container_width=True, key="forgot_resend"):
                user = get_user_by_email(st.session_state.forgot_email)
                with st.spinner("Sending new OTP…"):
                    ok, msg = _send_and_store(
                        st.session_state.forgot_email, user.name,
                        otp_key="forgot_otp", ts_key="forgot_otp_ts",
                        attempts_key="forgot_otp_attempts"
                    )
                if ok:
                    st.success("New OTP sent! Check your inbox.")
                else:
                    st.error(msg)
        with col2:
            if st.button("← Go back", use_container_width=True, key="forgot_back"):
                st.session_state.forgot_step = 1
                st.rerun()

    # ── STEP 3: New password ──
    elif st.session_state.forgot_step == 3:
        st.subheader("🔑 Create a new password")
        new_pw1 = st.text_input("New password (min 8 characters)", type="password", key="forgot_pw1")
        new_pw2 = st.text_input("Confirm new password",            type="password", key="forgot_pw2")

        if new_pw1 and len(new_pw1) < 8:
            st.warning("Password must be at least 8 characters.")
        if new_pw1 and new_pw2 and new_pw1 != new_pw2:
            st.error("Passwords do not match.")

        if st.button("Reset password", type="primary", use_container_width=True):
            if not new_pw1 or not new_pw2:
                st.error("Please enter and confirm your new password.")
            elif len(new_pw1) < 8:
                st.error("Password must be at least 8 characters.")
            elif new_pw1 != new_pw2:
                st.error("Passwords do not match.")
            else:
                ok, message = reset_password(st.session_state.forgot_email, new_pw1)
                if ok:
                    st.success("✅ Password reset successfully! You can now sign in.")
                    st.balloons()
                    st.session_state.forgot_step = 1
                else:
                    st.error(f"❌ {message}")