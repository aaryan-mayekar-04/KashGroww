import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── PATH SETUP ───────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from recommend import generate_plan
from db.crud import save_recommendation, save_profile

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard — KashGroww", page_icon="📊", layout="wide")

# ── AUTH GUARDS ──────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("pages/1_Login.py")
if not st.session_state.get("profile"):
    st.switch_page("pages/2_Profile.py")

p = st.session_state["profile"]

# ── GENERATE PLAN ONCE (cache in session_state) ──────────────────────────────
profile_key = (
    p.get("age"), p.get("gender"), p.get("dependents"),
    p.get("income"), p.get("amount"), p.get("horizon"),
)
if (
    "dashboard_result" not in st.session_state
    or st.session_state.get("dashboard_profile_key") != profile_key
):
    with st.spinner("Our ML model is analysing your profile…"):
        result = generate_plan(
            investor_name        = p.get("name"),
            age                  = p.get("age"),
            gender               = p.get("gender"),
            number_of_dependents = p.get("dependents", 0),
            annual_income        = p.get("income"),
            investment_amount    = p.get("amount"),
            horizon              = p.get("horizon"),
            preferred_assets     = p.get("preferred_assets", None),
        )
    st.session_state["dashboard_result"]      = result
    st.session_state["dashboard_profile_key"] = profile_key

    save_profile(
        st.session_state["user_id"],
        p.get("age"),
        p.get("gender"),
        p.get("dependents", 0),
        p.get("income"),
        p.get("amount"),
        result["risk_level"],
        p.get("horizon"),
    )

result = st.session_state["dashboard_result"]

# ── GUARD: empty plan ────────────────────────────────────────────────────────
if not result.get("plan"):
    st.error("Could not generate an investment plan. Please go back and check your profile.")
    if st.button("← Back to Profile"):
        st.switch_page("pages/2_Profile.py")
    st.stop()

plan_df = pd.DataFrame(result["plan"])

# ── HEADER ───────────────────────────────────────────────────────────────────
st.title(f"📊 Investment Plan — {p.get('name', '')}")
st.header(f"Risk Level Predicted: **{result['risk_level']}**")

# ── METRIC CARDS ─────────────────────────────────────────────────────────────
total_invested = result["total_invested"]
blended_return = max(0.1, result["blended_return"])
fv5            = round(total_invested * (1 + blended_return / 100) ** 5)
gain5          = fv5 - total_invested

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total invested",  f"₹{total_invested:,.0f}")
m2.metric("Blended return",  f"{blended_return:.2f}% p.a.")
m3.metric("Risk level",      result["risk_level"])
m4.metric(
    "5-yr projection", f"₹{fv5:,.0f}",
    delta=f"+₹{gain5:,.0f}" if gain5 >= 0 else f"₹{gain5:,.0f}",
)

st.divider()

# ── TABS (4 only — SIP Calculator is a dedicated page) ───────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Portfolio allocation",
    "🏦 Asset details",
    "📉 Projected returns",
    "💡 Tips",
])

# ── TAB 1: Portfolio allocation ──────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        fig_pie = px.pie(
            plan_df,
            values="allocation_pct",
            names="asset_type",
            hole=0.6,
            title="Portfolio Mix",
            color_discrete_sequence=["#1a472a", "#52b788", "#b5803a", "#c9604a", "#888"],
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.subheader("Allocation breakdown")
        for _, row in plan_df.iterrows():
            st.metric(
                label=row["asset_type"],
                value=f"{row['allocation_pct']:.1f}%",
                delta=f"₹{row['amount_inr']:,.0f}",
            )

# ── TAB 2: Asset details ─────────────────────────────────────────────────────
with tab2:
    for _, row in plan_df.iterrows():
        with st.expander(
            f"{row['asset_type']}  ·  {row['allocation_pct']:.1f}%"
            f"  ·  ₹{row['amount_inr']:,.0f}"
        ):
            c1, c2, c3 = st.columns(3)
        
            c1.metric("Asset",      row["asset_name"])
            c2.metric("Returns",     f"{row['annual_return']:.2f}%")
            c3.metric("Estimated Gain", f"₹{row['expected_gain']:,.0f}")

# ── TAB 3: Projected returns ─────────────────────────────────────────────────
with tab3:
    years  = [1, 2, 3, 5, 7, 10]
    values = [
        round(total_invested * (1 + blended_return / 100) ** y)
        for y in years
    ]
    inv = [total_invested] * len(years)

    fig_bar = go.Figure()
    fig_bar.add_bar(
        name="Amount invested",
        x=years, y=inv,
        marker_color="#D3D1C7",
    )
    fig_bar.add_bar(
        name="Projected value",
        x=years, y=values,
        marker_color="#1a472a",
    )
    fig_bar.update_layout(
        barmode="group",
        xaxis_title="Years",
        yaxis_title="₹",
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    proj_df = pd.DataFrame({
        "Year":          years,
        "Invested (₹)":  [f"₹{total_invested:,.0f}"] * len(years),
        "Projected (₹)": [f"₹{v:,.0f}" for v in values],
        "Gain (₹)":      [f"₹{v - total_invested:,.0f}" for v in values],
        "Growth":        [f"{((v / total_invested) - 1) * 100:.1f}%" for v in values],
    })
    st.dataframe(proj_df, use_container_width=True, hide_index=True)
    st.caption("⚠️ Not financial advice. Projections assume constant blended return.")

# ── TAB 4: Tips ──────────────────────────────────────────────────────────────
with tab4:
    TIPS = {
        "Low": [
            "Build a 6-month emergency fund before investing.",
            "Consider SIP in debt mutual funds for stable compounding.",
            "Review your portfolio every 6 months.",
        ],
        "Medium": [
            "Rebalance annually — trim equity if it exceeds 55%.",
            "Use ELSS mutual funds for Section 80C tax savings.",
            "Step up your SIP by 10% every year as income grows.",
        ],
        "High": [
            "Stay invested through corrections — time in market beats timing.",
            "Diversify sectors — avoid putting all equity in one theme.",
            "Shift 5–10% to safer assets each year as you near your goal.",
        ],
    }
    for i, tip in enumerate(TIPS.get(result["risk_level"], []), 1):
        st.info(f"**{i}.** {tip}")

# ── SAVE & NAVIGATION ────────────────────────────────────────────────────────
st.divider()
col_save, col_sip, col_back = st.columns([3, 2, 1])

with col_save:
    if st.button("💾 Save this plan to my history", type="primary", use_container_width=True):
        save_recommendation(
            user_id        = st.session_state["user_id"],
            risk_level     = result["risk_level"],
            plan           = result["plan"],
            blended_return = result["blended_return"],
            total_invested = result["total_invested"],
        )
        st.session_state["plan"] = result
        st.success("✅ Plan saved! View it in My History.")

with col_sip:
    if st.button("🧮 Open SIP Calculator", use_container_width=True):
        st.switch_page("pages/4_SIP_Calculator.py")

with col_back:
    if st.button("← Edit profile", use_container_width=True):
        st.session_state.pop("dashboard_result", None)
        st.session_state.pop("dashboard_profile_key", None)
        st.switch_page("pages/2_Profile.py")