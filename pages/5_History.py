import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd

# ── PATH SETUP ───────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from db.crud import get_history

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="My History — KashGroww", page_icon="📁", layout="wide")

# ── AUTH GUARD ───────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("pages/1_Login.py")

# ── HEADER ───────────────────────────────────────────────────────────────────
st.title("📁 My Investment History")
st.caption("All your saved investment plans in one place.")

# ── FETCH DATA ───────────────────────────────────────────────────────────────
history = get_history(st.session_state["user_id"])

if not history:
    st.info("No plans saved yet. Go to Dashboard and click 'Save this plan'.")
    if st.button("← Go to Dashboard"):
        st.switch_page("pages/3_Dashboard.py")
    st.stop()

# ── SUMMARY METRICS ──────────────────────────────────────────────────────────
avg_return     = sum(h["returns"]["blended_return"] for h in history) / len(history)
avg_invested   = sum(h["returns"]["total_invested"] for h in history) / len(history)
risk_trend     = history[0]["risk_level"]
if len(history) > 1:
    risk_trend += " → " + history[-1]["risk_level"]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Plans saved",    len(history))
m2.metric("Avg return",     f"{avg_return:.2f}%")
m3.metric("Avg invested",   f"₹{avg_invested:,.0f}")
m4.metric("Risk trend",     risk_trend)

st.divider()

# ── HISTORY LIST (newest first) ───────────────────────────────────────────────
# ✅ Fixed: single loop only, enumerate on reversed list for unique keys
for i, h in enumerate(reversed(history)):
    date_str = h["date"].strftime("%d %b %Y, %I:%M %p")
    ret      = h["returns"]["blended_return"]
    invested = h["returns"]["total_invested"]
    risk     = h["risk_level"]

    with st.expander(
        f"📅 {date_str}  ·  {risk} risk  ·  {ret:.2f}% return  ·  ₹{invested:,.0f} invested"
    ):
        plan_df = pd.DataFrame(h["plan"])

        # ✅ Fixed: chart and columns are all at the same indentation level
        col_a, col_b = st.columns(2)

        with col_a:
            fig = px.pie(
                plan_df,
                values="allocation_pct",
                names="asset_type",
                hole=0.5,
                title="Allocation mix",
                color_discrete_sequence=["#1a472a", "#52b788", "#b5803a", "#c9604a", "#888"],
            )
            fig.update_traces(textposition="outside", textinfo="percent+label")
            # ✅ Fixed: unique key per expander using outer loop index i
            st.plotly_chart(fig, use_container_width=True, key=f"pie_{i}")

        with col_b:
            c1, c2 = st.columns(2)
            c1.metric("Total invested", f"₹{invested:,.0f}")
            c2.metric("Blended return", f"{ret:.2f}%")

            st.dataframe(
                plan_df[["asset_type", "asset_name", "allocation_pct", "amount_inr"]].rename(
                    columns={
                        "asset_type":    "Asset type",
                        "asset_name":    "Asset name",
                        "allocation_pct":"Allocation %",
                        "amount_inr":    "Amount (₹)",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

# ── NAVIGATION ───────────────────────────────────────────────────────────────
st.divider()
if st.button("← Back to Dashboard", use_container_width=True):
    st.switch_page("pages/3_Dashboard.py")