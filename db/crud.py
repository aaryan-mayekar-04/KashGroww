"""
db/crud.py
==========
All database read/write operations for KashGroww.
Every function opens its own connection and closes it when done.
"""

import json
import bcrypt
from datetime import datetime
from db.models import get_connection


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# ── USERS ─────────────────────────────────────────────────────────────────────

def create_user(name: str, email: str, phone: str,
                username: str, plain_password: str):
    """Insert a new user. Returns the new user's id."""
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (name, email, phone, username, password)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, phone, username, _hash_password(plain_password)))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_user(username: str):
    """Fetch a user row by username. Returns a SimpleNamespace or None."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE username = %s", (username,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return _dict_to_obj(row)
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email: str):
    """Fetch a user row by email. Returns a SimpleNamespace or None."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s", (email,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return _dict_to_obj(row)
    finally:
        cursor.close()
        conn.close()


def email_exists(email: str) -> bool:
    """Return True if the email is already registered."""
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE email = %s", (email,)
        )
        return cursor.fetchone()[0] > 0
    finally:
        cursor.close()
        conn.close()


def reset_password(email: str, new_plain_password: str):
    """Update the password for the given email. Returns (True, msg) or (False, msg)."""
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET password = %s WHERE email = %s",
            (_hash_password(new_plain_password), email)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, "Email not found."
        return True, "Password reset successfully."
    except Exception as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


# ── PROFILES ──────────────────────────────────────────────────────────────────

def save_profile(user_id: int, age: int, gender: str, no_dependents: int,
                 income: int, invest_amount: int, risk_level: str,
                 horizon: str, preferred_assets: list = None):
    """
    Insert or update the investor profile for user_id.
    preferred_assets is stored as a JSON string.
    """
    assets_json = json.dumps(preferred_assets) if preferred_assets else None
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        # Check if profile already exists
        cursor.execute(
            "SELECT id FROM profiles WHERE user_id = %s", (user_id,)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE profiles
                SET age=%s, gender=%s, no_dependents=%s, income=%s,
                    invest_amount=%s, risk_level=%s, horizon=%s,
                    preferred_assets=%s
                WHERE user_id=%s
            """, (age, gender, no_dependents, income, invest_amount,
                  risk_level, horizon, assets_json, user_id))
        else:
            cursor.execute("""
                INSERT INTO profiles
                    (user_id, age, gender, no_dependents, income,
                     invest_amount, risk_level, horizon, preferred_assets)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, age, gender, no_dependents, income,
                  invest_amount, risk_level, horizon, assets_json))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_profile(user_id: int):
    """Return the profile dict for user_id, or None."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM profiles WHERE user_id = %s", (user_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        # Deserialise preferred_assets JSON
        if row.get("preferred_assets"):
            try:
                row["preferred_assets"] = json.loads(row["preferred_assets"])
            except (json.JSONDecodeError, TypeError):
                row["preferred_assets"] = []
        return row
    finally:
        cursor.close()
        conn.close()


# ── RECOMMENDATIONS ───────────────────────────────────────────────────────────

def save_recommendation(user_id: int, risk_level: str, plan: list,
                         blended_return: float, total_invested: float):
    """
    Save a generated plan to both recommendations and history tables.
    plan is stored as JSON.
    """
    plan_json = json.dumps(plan)
    conn      = get_connection()
    cursor    = conn.cursor()
    try:
        # Save to recommendations
        cursor.execute("""
            INSERT INTO recommendations
                (user_id, risk_level, plan_json, blended_return, total_invested)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, risk_level, plan_json, blended_return, total_invested))

        # Also save to history
        cursor.execute("""
            INSERT INTO history
                (user_id, risk_level, plan_json, blended_return, total_invested)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, risk_level, plan_json, blended_return, total_invested))

        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ── HISTORY ───────────────────────────────────────────────────────────────────

def get_history(user_id: int) -> list:
    """
    Return all saved plans for user_id as a list of dicts, newest first.
    Each dict has: date, risk_level, returns{blended_return, total_invested}, plan
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT risk_level, plan_json, blended_return,
                   total_invested, saved_at
            FROM history
            WHERE user_id = %s
            ORDER BY saved_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    result = []
    for row in rows:
        try:
            plan = json.loads(row["plan_json"]) if row["plan_json"] else []
        except (json.JSONDecodeError, TypeError):
            plan = []

        result.append({
            "date":       row["saved_at"],
            "risk_level": row["risk_level"],
            "returns": {
                "blended_return": row["blended_return"] or 0.0,
                "total_invested": row["total_invested"] or 0,
            },
            "plan": plan,
        })
    return result


# ── ASSETS ────────────────────────────────────────────────────────────────────

def get_assets(asset_type: str = None) -> list:
    """
    Return assets from the assets table.
    Optionally filter by asset_type.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if asset_type:
            cursor.execute(
                "SELECT * FROM assets WHERE asset_type = %s", (asset_type,)
            )
        else:
            cursor.execute("SELECT * FROM assets")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def upsert_asset(asset_type: str, asset_name: str, annual_return: float,
                 volatility: float, sharpe_ratio: float, beta: float,
                 rsi: float, ma_20: float, ma_50: float):
    """Insert or update an asset record by asset_name."""
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM assets WHERE asset_name = %s", (asset_name,)
        )
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE assets
                SET asset_type=%s, annual_return=%s, volatility=%s,
                    sharpe_ratio=%s, beta=%s, rsi=%s, ma_20=%s, ma_50=%s
                WHERE asset_name=%s
            """, (asset_type, annual_return, volatility, sharpe_ratio,
                  beta, rsi, ma_20, ma_50, asset_name))
        else:
            cursor.execute("""
                INSERT INTO assets
                    (asset_type, asset_name, annual_return, volatility,
                     sharpe_ratio, beta, rsi, ma_20, ma_50)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (asset_type, asset_name, annual_return, volatility,
                  sharpe_ratio, beta, rsi, ma_20, ma_50))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ── INTERNAL HELPER ───────────────────────────────────────────────────────────

class _Obj:
    """Converts a dict to a dot-accessible object (like SQLAlchemy row)."""
    def __init__(self, d: dict):
        self.__dict__.update(d)

def _dict_to_obj(d: dict) -> _Obj:
    return _Obj(d)