"""
db/models.py
============
MySQL connection + table creation for KashGroww.

Add your credentials to .streamlit/secrets.toml:

[mysql]
host     = "localhost"
port     = 3306
user     = "root"
password = "your_mysql_password"
database = "kashgroww"
"""

import json
import streamlit as st
import mysql.connector
from mysql.connector import Error


# ── CONNECTION ────────────────────────────────────────────────────────────────

def get_connection():
    """Return a fresh MySQL connection using credentials from secrets.toml."""
    try:
        cfg = st.secrets["mysql"]
        conn = mysql.connector.connect(
            host     = cfg.get("host",     "localhost"),
            port     = int(cfg.get("port", 3306)),
            user     = cfg["user"],
            password = cfg["password"],
            database = cfg["database"],
        )
        return conn
    except KeyError:
        raise RuntimeError(
            "MySQL credentials missing from .streamlit/secrets.toml. "
            "Add a [mysql] section with host, port, user, password, database."
        )
    except Error as e:
        raise RuntimeError(f"MySQL connection failed: {e}")


# ── TABLE CREATION ────────────────────────────────────────────────────────────

def init_db():
    """Create all tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── users ─────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            name       VARCHAR(100)        NOT NULL,
            email      VARCHAR(150) UNIQUE NOT NULL,
            phone      VARCHAR(20),
            username   VARCHAR(50)  UNIQUE NOT NULL,
            password   VARCHAR(255)        NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── profiles ──────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id               INT AUTO_INCREMENT PRIMARY KEY,
            user_id          INT          NOT NULL,
            age              INT,
            gender           VARCHAR(10),
            no_dependents    INT          DEFAULT 0,
            income           BIGINT,
            invest_amount    BIGINT,
            risk_level       VARCHAR(20),
            horizon          VARCHAR(20),
            preferred_assets TEXT,
            updated_at       DATETIME     DEFAULT CURRENT_TIMESTAMP
                                          ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ── recommendations ───────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            user_id        INT          NOT NULL,
            risk_level     VARCHAR(20),
            plan_json      LONGTEXT,
            blended_return FLOAT,
            total_invested BIGINT,
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ── history (view of recommendations — kept as separate table for fast reads)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            user_id        INT          NOT NULL,
            risk_level     VARCHAR(20),
            plan_json      LONGTEXT,
            blended_return FLOAT,
            total_invested BIGINT,
            saved_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ── assets ────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            asset_type    VARCHAR(50),
            asset_name    VARCHAR(150),
            annual_return FLOAT,
            volatility    FLOAT,
            sharpe_ratio  FLOAT,
            beta          FLOAT,
            rsi           FLOAT,
            ma_20         FLOAT,
            ma_50         FLOAT,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()