import sys
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ── PATH SETUP ───────────────────────────────────────────────────────────────
# Must happen before ANY local imports
ROOT_DIR = Path(__file__).resolve().parent   # folder containing app.py
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))        # insert at front, not append

# ── LOCAL IMPORTS ─────────────────────────────────────────────────────────────
import streamlit as st

try:
    import db.models
    db.models.init_db()
except ModuleNotFoundError as e:
    st.error(f"❌ Could not import db.models: {e}")
    st.info(
        "Make sure your project structure looks like this:\n\n"
        "```\n"
        "KashGroww Capstone Project/\n"
        "├── app.py\n"
        "├── recommend.py\n"
        "├── db/\n"
        "│   ├── __init__.py     ← must exist (can be empty)\n"
        "│   ├── models.py\n"
        "│   └── crud.py\n"
        "└── pages/\n"
        "```"
    )
    st.stop()
except Exception as e:
    st.error(f"❌ Database initialisation failed: {e}")
    st.stop()

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="💸KashGroww💹",
    page_icon="",
    layout="wide",
)

# ── SESSION STATE DEFAULTS ────────────────────────────────────────────────────
defaults = {
    "logged_in":       False,
    "user_id":         None,
    "username":        None,
    "name":            None,
    "profile":         None,
    "plan":            None,
    "dashboard_result":      None,
    "dashboard_profile_key": None,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── HOME PAGE ─────────────────────────────────────────────────────────────────
st.title("💸💹 KashGroww — Robo-Advisory Platform")
st.header("Custom Your Cash, Master Your Growth! ✈️ ✅")
st.subheader("Get your personalised Investment Plan")
st.divider()

if st.session_state["logged_in"]:
    st.success(f"Welcome back, **{st.session_state['name']}**! 👋")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("pages/2_Profile.py",  label="🧑‍💼 Investor profile")
    with col2:
        st.page_link("pages/3_Dashboard.py", label="📊 My dashboard")
    with col3:
        st.page_link("pages/4_History.py",  label="📁 My history")
else:
    st.info("Please sign in to get started.")
    st.page_link("pages/1_Login.py", label="→ Sign in or Register") # type: ignore # type: ignore # type: ignore # type: ignore