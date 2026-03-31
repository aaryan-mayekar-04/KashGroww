import sys
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── PATH SETUP ───────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from recommend import sip_future_value

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SIP Calculator — KashGroww",
    page_icon="🧮",
    layout="wide",
)

# ── AUTH GUARD ───────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("pages/1_Login.py")

# ── HEADER ───────────────────────────────────────────────────────────────────
st.title("🧮 SIP Calculator")
st.subheader("Estimate How Much Your Monthly Investment Will Grow Over Time.")
st.divider()

# ── PULL DEFAULTS FROM DASHBOARD IF AVAILABLE ────────────────────────────────
result         = st.session_state.get("dashboard_result", {})
blended_return = result.get("blended_return", 12.0)
blended_return = max(1.0, blended_return)   # clamp — never below 1.0

# ── INPUT CONTROLS ───────────────────────────────────────────────────────────
sc1, sc2, sc3 = st.columns(3)

with sc1:
    sip_amount = st.number_input(
        "Monthly SIP amount (₹)",
        min_value=100,
        max_value=1_00_00_000,
        value=5_000,
        step=500,
        help="Amount you plan to invest every month",
    )

with sc2:
    sip_rate = st.number_input(
        "Expected annual return (%)",
        min_value=1.0,
        max_value=40.0,
        value=float(round(blended_return, 1)),
        step=0.5,
        help="Your portfolio's blended return is pre-filled from your dashboard",
    )

with sc3:
    sip_years = st.slider(
        "Investment period (years)",
        min_value=1,
        max_value=30,
        value=10,
        help="How long you plan to keep investing",
    )

st.divider()

# ── CALCULATIONS ─────────────────────────────────────────────────────────────
fv_sip       = sip_future_value(sip_amount, sip_rate, sip_years)
invested_sip = sip_amount * sip_years * 12
gain_sip     = fv_sip - invested_sip
growth_pct   = (gain_sip / invested_sip * 100) if invested_sip > 0 else 0.0

# ── METRIC CARDS ─────────────────────────────────────────────────────────────
s1, s2, s3, s4 = st.columns(4)

s1.metric(
    "Monthly SIP",
    f"₹{sip_amount:,.0f}",
)
s2.metric(
    "Total invested",
    f"₹{invested_sip:,.0f}",
)
s3.metric(
    "Future value",
    f"₹{fv_sip:,.0f}",
    delta=f"+₹{gain_sip:,.0f}",
)
s4.metric(
    "Wealth gained",
    f"₹{gain_sip:,.0f}",
    delta=f"+{growth_pct:.1f}%",
)

st.divider()

# ── CHARTS ───────────────────────────────────────────────────────────────────
chart_tab, table_tab, breakdown_tab = st.tabs([
    "📈 Growth chart", "📋 Year-by-year table", "🥧 Breakdown"
])

sip_years_range = list(range(1, sip_years + 1))
sip_values      = [sip_future_value(sip_amount, sip_rate, y) for y in sip_years_range]
sip_invested    = [sip_amount * y * 12 for y in sip_years_range]
sip_gains       = [v - i for v, i in zip(sip_values, sip_invested)]

# ── Growth chart ─────────────────────────────────────────────────────────────
with chart_tab:
    fig = go.Figure()
    fig.add_scatter(
        x=sip_years_range, y=sip_invested,
        name="Amount invested",
        fill="tozeroy",
        line=dict(color="#D3D1C7", width=2),
        fillcolor="rgba(211,209,199,0.4)",
    )
    fig.add_scatter(
        x=sip_years_range, y=sip_values,
        name="Future value",
        fill="tonexty",
        line=dict(color="#1a472a", width=2),
        fillcolor="rgba(26,71,42,0.25)",
    )
    fig.update_layout(
        xaxis_title="Years",
        yaxis_title="₹",
        height=380,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(t=20, b=40),
    )
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("⚠️ Not financial advice. Projections assume a constant annual return.")

# ── Year-by-year table ───────────────────────────────────────────────────────
with table_tab:
    table_df = pd.DataFrame({
        "Year":              sip_years_range,
        "Invested (₹)":      [f"₹{v:,.0f}" for v in sip_invested],
        "Future Value (₹)":  [f"₹{v:,.0f}" for v in sip_values],
        "Gain (₹)":          [f"₹{v:,.0f}" for v in sip_gains],
        "Growth (%)":        [f"{(g / i * 100):.1f}%" for g, i in zip(sip_gains, sip_invested)],
    })
    st.dataframe(table_df, use_container_width=True, hide_index=True)

# ── Breakdown pie ────────────────────────────────────────────────────────────
with breakdown_tab:
    fig_pie = px.pie(
        names=["Amount invested", "Wealth gained"],
        values=[invested_sip, gain_sip],
        hole=0.6,
        color_discrete_sequence=["#D3D1C7", "#1a472a"],
    )
    fig_pie.update_traces(textposition="outside", textinfo="percent+label")
    fig_pie.update_layout(height=360, margin=dict(t=20, b=20))

    col_pie, col_summary = st.columns([1, 1])
    with col_pie:
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_summary:
        st.markdown("### Summary")
        st.markdown(f"- **Monthly SIP:** ₹{sip_amount:,.0f}")
        st.markdown(f"- **Duration:** {sip_years} years ({sip_years * 12} months)")
        st.markdown(f"- **Rate of return:** {sip_rate}% p.a.")
        st.markdown(f"- **Total invested:** ₹{invested_sip:,.0f}")
        st.markdown(f"- **Future value:** ₹{fv_sip:,.0f}")
        st.markdown(f"- **Wealth gained:** ₹{gain_sip:,.0f} ({growth_pct:.1f}%)")

st.divider()

# ── NAVIGATION ───────────────────────────────────────────────────────────────
col_l, col_r = st.columns(2)
with col_l:
    if st.button("← Back to Dashboard", use_container_width=True):
        st.switch_page("pages/3_Dashboard.py")
with col_r:
    if st.button("View my history →", use_container_width=True):
        st.switch_page("pages/5_History.py")