import sys
from pathlib import Path
import streamlit as st

# ── PATH SETUP ───────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from db.crud import save_profile

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Investor Profile — KashGroww", layout="wide")

# ── AUTH GUARD ───────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.switch_page("pages/1_Login.py")

# ── HEADER ───────────────────────────────────────────────────────────────────
st.title("🧑‍💼 Investor Profile")
st.subheader("Used to Predict Risk Level and Build a Personalised Investment Plan.")

# ── FORM COLUMNS ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Personal details")
    name       = st.text_input("Full name", value=st.session_state.get("name", ""))
    age        = st.slider("Age", min_value=19, max_value=60, value=30)
    gender     = st.selectbox("Gender", ["Male", "Female"])
    dependents = st.slider("Number of dependents", 0, 10, 2)

with col2:
    st.subheader("Financial details")
    income = st.number_input(
        "Annual income (₹)",
        min_value=60_000,
        max_value=1_00_00_000,
        value=1_00_000,
        step=5_000,
    )
    amount = st.number_input(
        "Investment amount (₹)",
        min_value=1_000,
        max_value=1_00_00_000,
        value=50_000,
        step=1_000,
    )
    horizon = st.radio(
        "Investment horizon",
        ["Short Term", "Mid Term", "Long Term"],
        horizontal=True,
    )

# ── ASSET PREFERENCES ────────────────────────────────────────────────────────
st.divider()
st.header("🏦 Asset Preferences")
st.subheader(
    "Select the asset types you are comfortable investing in. ")
st.info(
    "Your plan will only allocate funds to your chosen assets."
)

ASSET_OPTIONS = [
    "Stocks",
    "Mutual Funds",
    "Gold",
    "Active Fixed Income",
    "Passive Equity",
]

# Pre-fill from session if returning to edit profile
st.subheader("📊 Choose Your Preferred Asset Types")

default_assets = (st.session_state.get("profile") or {}).get("preferred_assets", ASSET_OPTIONS)

preferred_assets = st.multiselect(
    "Select at least one asset type",
    options=ASSET_OPTIONS,
    default=default_assets,
    help="Only the assets you select here will be included in your investment plan."
)

# Visual indicator of selected assets
if preferred_assets:
    cols = st.columns(len(preferred_assets))
    asset_icons = {
        "Stocks":              "📈",
        "Mutual Funds":        "💼",
        "Gold":                "🥇",
        "Active Fixed Income": "🏦",
        "Passive Equity":      "📊",
    }
    for col, asset in zip(cols, preferred_assets):
        col.success(f"{asset_icons.get(asset, '✅')} {asset}")
else:
    st.warning("⚠️ Please select at least one asset type to continue.")

# ── PROFILE SUMMARY ───────────────────────────────────────────────────────────
st.divider()
st.subheader("Your Profile Summary")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Age",        age)
m2.metric("Dependents", dependents)
m3.metric("Income",     f"₹{income:,.0f}")
m4.metric("Investment", f"₹{amount:,.0f}")
m5.metric("Horizon",    horizon)

if preferred_assets:
    st.info(
        f"**Selected assets:** {', '.join(preferred_assets)}  ·  "
        f"Allocation will be split equally across your {len(preferred_assets)} chosen asset(s)."
    )

# ── SUBMIT ────────────────────────────────────────────────────────────────────
st.subheader("Submit Your Profile")
if st.button("Generate my Investment Plan →", type="primary", use_container_width=True):

    # Validate asset selection
    if not preferred_assets:
        st.error("❌ Please select at least one asset type before continuing.")
        st.stop()

    # Validate investment amount vs income
    if amount > income:
        st.warning("⚠️ Your investment amount exceeds your annual income. Are you sure?")

    # Store full profile in session_state
    st.session_state["profile"] = {
        "name":             name,
        "age":              age,
        "gender":           gender,
        "dependents":       dependents,
        "income":           income,
        "amount":           amount,
        "horizon":          horizon,
        "preferred_assets": preferred_assets,   # ← new field
    }

    # Clear cached dashboard result so plan regenerates with new preferences
    st.session_state.pop("dashboard_result", None)
    st.session_state.pop("dashboard_profile_key", None)

    # Save to DB (risk_level pending until ML prediction on dashboard)
    save_profile(
        user_id       = st.session_state["user_id"],
        age           = age,
        gender        = gender,
        no_dependents = dependents,
        income        = income,
        invest_amount = amount,
        risk_level    = "Pending",
        horizon       = horizon,
    )

    st.switch_page("pages/3_Dashboard.py")