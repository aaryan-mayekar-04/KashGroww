from sqlalchemy import (
    create_engine, Column, Integer, String,
    Float, DateTime, Text, BigInteger, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# ── CONNECTION FUNCTION ─────────────────────────────────────────
def get_db_url():
    # When running in Streamlit → reads from secrets.toml
    # When running in Jupyter   → uses the hardcoded local URL
    try:
        import streamlit as st
        c = st.secrets["mysql"]
        return f"mysql+pymysql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"
    except:
        return "mysql+pymysql://root:@localhost:3306/kashgroww_db"

# pool_pre_ping=True → auto-reconnect if MySQL closes idle connection
ENGINE       = create_engine(get_db_url(), pool_pre_ping=True, pool_recycle=3600)
Base         = declarative_base()
SessionLocal = sessionmaker(bind=ENGINE)

# ── TABLE DEFINITIONS ───────────────────────────────────────────
class User(Base):
    __tablename__ = 'users'
    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False)
    phone      = Column(String(20))
    username   = Column(String(80), unique=True, nullable=False)
    password   = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class Profile(Base):
    __tablename__ = 'profiles'
    id            = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey('users.id'), nullable=False)
    age           = Column(Integer)
    gender        = Column(String(20))
    no_dependents = Column(Integer)
    income        = Column(BigInteger)
    invest_amount = Column(BigInteger)
    risk_level    = Column(String(20))
    horizon       = Column(String(30))
    updated_at    = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Recommendation(Base):
    __tablename__ = 'recommendations'
    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at   = Column(DateTime, default=datetime.now)
    risk_level   = Column(String(20))
    plan_json    = Column(Text)
    returns_json = Column(Text)

# ── HELPER FUNCTIONS ────────────────────────────────────────────
def get_session():
    return SessionLocal()

def init_db():
    # Creates all tables. Safe to call many times — won't overwrite data.
    Base.metadata.create_all(bind=ENGINE)
    print("Database tables ready.")