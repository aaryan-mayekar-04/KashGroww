### Importing Required Libraries
import pandas as pd        # to read the Excel dataset
import numpy  as np        # to create arrays for the model
import joblib              # to load the saved .pkl model files
from pathlib import Path   # to build file paths 
import os

# Base directory - path of THIS file
BASE = Path(__file__).resolve().parent

# Paths
MODEL_DIR = BASE / "model"
DATA_DIR = BASE / "data"

### Load Model and Encoders
clf        = joblib.load(MODEL_DIR / "risk_classifier.pkl")
scaler     = joblib.load(MODEL_DIR / "scaler.pkl")
le_gender  = joblib.load(MODEL_DIR / "le_gender.pkl")
le_horizon = joblib.load(MODEL_DIR / "le_horizon.pkl")
le_risk    = joblib.load(MODEL_DIR / "le_risk.pkl")

### Loading Dataset
dataset = pd.read_excel(DATA_DIR / "KashGroww Dataset File.xlsx")

### STEP 1: Build Allocation Table
# This dictionary stores the average allocation % per risk level
# Computed from your REAL dataset numbers:
#
#   Low Risk:    Stocks=4.89%, MutualFunds=18.47%, Gold=19.8%,
#                PassiveEquity=13.0%, FixedIncome=62.31%
#   Medium Risk: Stocks=21.22%, MutualFunds=18.47%, Gold=17.9%,
#                PassiveEquity=9.0%,  FixedIncome=34.99%
#   High Risk:   Stocks=47.10%, MutualFunds=19.0%, Gold=8.0%,
#                PassiveEquity=16.0%, FixedIncome=10.05%

_ALLOC_COLS = {
    'Stocks':              'Stocks_Percentage',
    'Mutual Funds':        'Mutual_Funds_Percentage',
    'Gold':                'Gold_Percentage',
    'Passive Equity':      'Passive_Equity_Percentage',
    'Active Fixed Income': 'Active_Fixed_Income_Percentage',
}

# STEP 2: GET ALLOCATION PERCENTAGES
def get_allocation(risk_level):
    subset = dataset[dataset['Risk_Level'] == risk_level]

    return {
        'Stocks': round(subset['Stocks_Percentage'].mean(), 1),
        'Mutual Funds': round(subset['Mutual_Funds_Percentage'].mean(), 1),
        'Gold': round(subset['Gold_Percentage'].mean(), 1),
        'Passive Equity': round(subset['Passive_Equity_Percentage'].mean(), 1),
        'Active Fixed Income': round(subset['Active_Fixed_Income_Percentage'].mean(), 1),
    }

# Loop over each risk level and compute averages
ALLOCATION_TABLE = {}
for risk in ['Low', 'Medium', 'High']:
    subset = dataset[dataset['Risk_Level'] == risk]  # filter rows for this risk
    ALLOCATION_TABLE[risk] = {
        asset_type: round(subset[col].mean(), 2)
        for asset_type, col in _ALLOC_COLS.items()
    }

# ── STEP 3: SELECT BEST ASSETS PER TYPE
# For each asset type, find the ONE best asset
# "Best" = highest Sharpe Ratio (best return per unit of risk)
#
# From your actual dataset the best assets are:
#   Stocks:              Reliance Industries Ltd (NSE) — sharpe=4.6955
#   Gold:                ICICI Prudential Gold Fund    — sharpe=4.6184
#   Active Fixed Income: Axis Fixed Maturity Plan      — sharpe=4.1324
#   Passive Equity:      Nippon India ETF Nifty 50     — sharpe=4.5966
#   Mutual Funds:        ICICI Prudential ELSS Fund    — sharpe=4.6049
def get_best_assets(risk_level, top_n=1):
    """Returns the best asset per type based on the Sharpe Ratio."""
    subset = dataset[dataset['Risk_Level'] == risk_level]
    best_assets = {}
    for asset_type in subset['Asset Type'].unique():
        best = subset[subset['Asset Type']==asset_type]\
                     .nlargest(top_n, 'Sharpe_Ratio')\
                     .iloc[0]
        best_assets[asset_type] = {
            'name':          best['Asset_Name'],
            'annual_return': round(best['Annual_Return'] * 100, 4),
            'volatility':    round(best['Volatility']    * 100, 4),
            'sharpe_ratio':  round(best['Sharpe_Ratio'], 4),
            'beta':          round(best['Beta'], 4),
            'rsi':           round(best['RSI'],  2),
            'ma_20':         round(best['MA_20'], 2),
            'ma_50':         round(best['MA_50'], 2),
        }
    return best_assets

# STEP 4: PREDICT RISK LEVEL
def predict_risk(investor_name, age, gender, annual_income, number_of_dependents, investment_amount, horizon):
    """Takes investor inputs → returns predicted Risk_Level string."""
    
    print(f"Prediction for {investor_name}")
    
    features = np.array([[
        age,
        le_gender.transform([gender])[0],
        number_of_dependents,   
        annual_income,         
        investment_amount,
        le_horizon.transform([horizon])[0]
    ]])
    
    scaled = scaler.transform(features)
    encoded = clf.predict(scaled)[0]
    
    return le_risk.inverse_transform([encoded])[0]

def generate_plan(investor_name, age, gender, annual_income, number_of_dependents, investment_amount, horizon):
    """Main function — call this from Streamlit pages."""

    # Step 1: Predict risk
    risk_level = predict_risk(
        investor_name,
        age,
        gender,
        annual_income,
        number_of_dependents,
        investment_amount,
        horizon
    )

    # Step 2: Allocation + assets
    allocation = ALLOCATION_TABLE[risk_level]
    assets     = get_best_assets(risk_level)

    # Step 3: Build plan
    plan = []

    for asset_type, pct in allocation.items():
        rupees = round(investment_amount * pct / 100)

        asset_info = assets.get(asset_type, {})
        annual_return = asset_info.get('annual_return', 0)

        expected_gain = round(rupees * annual_return / 100)

        plan.append({
            'asset_type':     asset_type,
            'asset_name':     asset_info.get('name', '—'),
            'allocation_pct': pct,
            'amount':         rupees,
            'annual_return':  annual_return,
            'expected_gain':  expected_gain,
            'volatility':     asset_info.get('volatility', 0),
            'sharpe_ratio':   asset_info.get('sharpe_ratio', 0),
            'beta':           asset_info.get('beta', 0),
            'rsi':            asset_info.get('rsi', 0),
        })

    # Step 4: Blended return
    blended_return = sum(
        r['allocation_pct']/100 * r['annual_return'] for r in plan
    )

    # Step 5: Final output
    return {
        'investor_name':  investor_name,
        'risk_level':     risk_level,
        'plan':           plan,
        'blended_return': round(blended_return, 2),
        'total_invested': investment_amount,
    }

#  FUNCTION 3: sip_future_value
#  Used by the SIP Calculator page
#  Formula: FV = P × [((1+r)^n - 1) / r] × (1+r)
# ════════════════════════════════════════════════════════════════
def sip_future_value(monthly_amount, annual_rate_pct, years):
    # r = monthly interest rate (annual rate ÷ 12)
    r = annual_rate_pct / 100 / 12
    # n = total number of monthly payments
    n = years * 12
    if r == 0:
        return monthly_amount * n
    fv = monthly_amount * (((1 + r) ** n - 1) / r) * (1 + r)
    return round(fv, 2)