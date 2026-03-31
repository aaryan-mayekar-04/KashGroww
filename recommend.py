print("🔥 recommend.py is loading...")
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")  

# ── PATHS ───────────────────────────────────────────────────────────
BASE      = Path(__file__).resolve().parent
MODEL_DIR = Path("model")
DATA_PATH = BASE / "C:\\Users\\AARYAN MAYEKAR\\Downloads\\KashGroww Capstone Project\\KashGroww Dataset File.xlsx"


# ── TRAIN MODEL WHEN MISSING ─────────────────────────────────────────

def train_model():
    global clf, scaler, le_gender, le_horizon, le_risk, models_loaded, dataset

    if dataset is None:
        print("⚠️  No dataset loaded, cannot train model")
        return

    required_columns = ["Age", "Gender", "No_of_Dependents", "Income", "Investment_Amount", "Investment_Horizon", "Risk Level"]
    if not set(required_columns).issubset(dataset.columns):
        print("⚠️  Dataset missing required columns for training")
        return

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder, StandardScaler

    df_train = dataset.copy()
    df_train.columns = df_train.columns.str.strip()

    X = df_train[["Age", "Gender", "No_of_Dependents", "Income", "Investment_Amount", "Investment_Horizon"]].copy()
    y = df_train["Risk Level"].copy()

    le_gender  = LabelEncoder()
    le_horizon = LabelEncoder()
    le_risk    = LabelEncoder()

    X["Gender"] = le_gender.fit_transform(X["Gender"].astype(str))
    X["Investment_Horizon"] = le_horizon.fit_transform(X["Investment_Horizon"].astype(str))
    y_encoded = le_risk.fit_transform(y.astype(str))

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_scaled, y_encoded)

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(clf, MODEL_DIR / "risk_classifier.pkl")
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
    joblib.dump(le_gender, MODEL_DIR / "le_gender.pkl")
    joblib.dump(le_horizon, MODEL_DIR / "le_horizon.pkl")
    joblib.dump(le_risk, MODEL_DIR / "le_risk.pkl")

    models_loaded = True
    print("✅ Model trained and saved successfully")

# ── LOAD SAVED MODEL FILES ──────────────────────────────────────────
try:
    clf        = joblib.load(MODEL_DIR / "risk_classifier.pkl")
    scaler     = joblib.load(MODEL_DIR / "scaler.pkl")
    le_gender  = joblib.load(MODEL_DIR / "le_gender.pkl")
    le_horizon = joblib.load(MODEL_DIR / "le_horizon.pkl")
    le_risk    = joblib.load(MODEL_DIR / "le_risk.pkl")
    models_loaded = True
    print("✅ Models loaded successfully")
except FileNotFoundError as e:
    print(f"⚠️  Models not found: {e}")
    models_loaded = False
    clf = scaler = le_gender = le_horizon = le_risk = None

# ── LOAD DATASET ────────────────────────────────────────────────────
try:
    dataset = pd.read_excel(DATA_PATH)
    dataset.columns = dataset.columns.str.strip()
    dataset["RSI"].fillna(dataset["RSI"].median(), inplace=True)
    print("✅ Dataset loaded successfully")
except Exception as e:
    print(f"⚠️  Dataset error: {e}")
    dataset = None

# If models are not loaded yet, attempt to build from dataset
if not globals().get('models_loaded', False):
    train_model()

def generate_plan(*args, **kwargs):
    return {
        "risk_level": "Low",
        "plan": [],
        "blended_return": 0,
        "total_invested": 0
    }

# ── FEATURE COLUMNS ─────────────────────────────────────────────────
FEATURE_COLS = ["Age", "Gender", "No_of_Dependents",
                "Income", "Investment_Amount", "Investment_Horizon"]

# ── ALLOCATION TABLE ────────────────────────────────────────────────
_ALLOC_MAP = {
    "Stocks":              "Stocks_Percentage",
    "Mutual Funds":        "Mutual_Funds_Percentage",
    "Gold":                "Gold_Percentage",
    "Passive Equity":      "Passive_Equity_Percentage",
    "Active Fixed Income": "Active_Fixed_Income_Percentage",
}

ALLOCATION_TABLE = {}
BEST_ASSETS = {}

if dataset is not None:
    # Find risk column name
    risk_col = 'Risk_Level' if 'Risk_Level' in dataset.columns else 'Risk Level' if 'Risk Level' in dataset.columns else None
    
    if risk_col:
        # Build allocation table
        for risk in ["Low", "Medium", "High"]:
            subset = dataset[dataset[risk_col] == risk]
            if len(subset) > 0:
                ALLOCATION_TABLE[risk] = {
                    asset_type: round(subset[col].mean(), 2)
                    for asset_type, col in _ALLOC_MAP.items()
                    if col in subset.columns
                }

    # Build best assets table
    asset_col = 'Asset Type' if 'Asset Type' in dataset.columns else 'Asset_Type' if 'Asset_Type' in dataset.columns else None
    name_col = 'Asset Name' if 'Asset Name' in dataset.columns else 'Asset_Name' if 'Asset_Name' in dataset.columns else None
    
    if asset_col and name_col:
        for asset_type in dataset[asset_col].unique():
            subset = dataset[dataset[asset_col] == asset_type]
            if len(subset) > 0:
                sort_col = 'Sharpe Ratio' if 'Sharpe Ratio' in subset.columns else 'Sharpe_Ratio' if 'Sharpe_Ratio' in subset.columns else 'Annual Return (%)' if 'Annual Return (%)' in subset.columns else 'Annual_Return'
                best = subset.nlargest(1, sort_col).iloc[0]
                
                return_col = 'Annual Return (%)' if 'Annual Return (%)' in subset.columns else 'Annual_Return'
                ret_val = best.get(return_col, 0) if return_col in best else 0
                if ret_val > 100:
                    ret_val = ret_val * 100
                
                BEST_ASSETS[asset_type] = {
                    "name":          best[name_col] if name_col in best else "---",
                    "annual_return": round(ret_val, 2),
                    "volatility":    round(best.get('Volatility', 0) * 100 if best.get('Volatility', 0) < 1 else best.get('Volatility', 0), 2),
                    "sharpe_ratio":  round(best.get('Sharpe Ratio', best.get('Sharpe_Ratio', 0)), 4),
                    "beta":          round(best.get('Beta', 0), 4),
                    "rsi":           round(best.get('RSI', 0), 2),
                    "ma_20":         round(best.get('MA 20', best.get('MA_20', 0)), 2),
                    "ma_50":         round(best.get('MA 50', best.get('MA_50', 0)), 2),
                }

# Fallback allocations if dataset is missing
if not ALLOCATION_TABLE:
    ALLOCATION_TABLE = {
        "Low":    {"Stocks": 5.0, "Mutual Funds": 15.0, "Gold": 20.0, "Passive Equity": 13.0, "Active Fixed Income": 47.0},
        "Medium": {"Stocks": 21.0, "Mutual Funds": 18.0, "Gold": 18.0, "Passive Equity": 9.0, "Active Fixed Income": 34.0},
        "High":   {"Stocks": 47.0, "Mutual Funds": 19.0, "Gold": 8.0, "Passive Equity": 16.0, "Active Fixed Income": 10.0}
    }

if not BEST_ASSETS:
    BEST_ASSETS = {
        "Stocks": {"name": "Reliance Industries Ltd", "annual_return": 15.0, "volatility": 18.0, "sharpe_ratio": 0.83, "beta": 1.2, "rsi": 65, "ma_20": 1234, "ma_50": 1200},
        "Mutual Funds": {"name": "ICICI Pru Growth Fund", "annual_return": 12.0, "volatility": 12.0, "sharpe_ratio": 1.0, "beta": 0.9, "rsi": 55, "ma_20": 450, "ma_50": 440},
        "Gold": {"name": "ICICI Gold Fund", "annual_return": 8.0, "volatility": 6.0, "sharpe_ratio": 1.33, "beta": -0.1, "rsi": 50, "ma_20": 5200, "ma_50": 5100},
        "Passive Equity": {"name": "Nippon Nifty 50 ETF", "annual_return": 14.0, "volatility": 16.0, "sharpe_ratio": 0.875, "beta": 1.0, "rsi": 60, "ma_20": 25000, "ma_50": 24500},
        "Active Fixed Income": {"name": "Axis Fixed Maturity", "annual_return": 7.0, "volatility": 2.0, "sharpe_ratio": 3.5, "beta": 0.0, "rsi": 50, "ma_20": 100, "ma_50": 100},
    }


def predict_risk(age, gender, dependents, income, amount, horizon):
    """Predict risk level using trained model or fallback rule-based approach."""
    if not globals().get('models_loaded', False) or clf is None:
        # If models not loaded, try training now from dataset
        train_model()

    if globals().get('models_loaded', False) and clf is not None:
        try:
            gender_enc  = le_gender.transform([gender])[0]
            horizon_enc = le_horizon.transform([horizon])[0]

            input_df = pd.DataFrame([{
                "Age": age,
                "Gender": gender_enc,
                "No_of_Dependents": dependents,
                "Income": income,
                "Investment_Amount": amount,
                "Investment_Horizon": horizon_enc,
            }])

            input_scaled = scaler.transform(input_df)
            pred_encoded = clf.predict(input_scaled)[0]
            return le_risk.inverse_transform([pred_encoded])[0]
        except Exception as e:
            print(f"⚠️  Model prediction error: {e}. Falling back to rule-based.")

    risk_score = (age / 100) + (amount / max(income, 1)) + (dependents * 0.1)
    if risk_score < 1.5:
        return "Low"
    elif risk_score < 2.5:
        return "Medium"
    else:
        return "High"
    
    try:
        gender_enc  = le_gender.transform([gender])[0]
        horizon_enc = le_horizon.transform([horizon])[0]
        
        input_df = pd.DataFrame([{
            "Age": age,
            "Gender": gender_enc,
            "No_of_Dependents": dependents,
            "Income": income,
            "Investment_Amount": amount,
            "Investment_Horizon": horizon_enc,
        }])
        
        input_scaled = scaler.transform(input_df)
        pred_encoded = clf.predict(input_scaled)[0]
        risk_label = le_risk.inverse_transform([pred_encoded])[0]
        
        return risk_label
    except Exception as e:
        print(f"⚠️  Prediction error: {e}")
        risk_score = (age / 100) + (amount / max(income, 1)) + (dependents * 0.1)
        if risk_score < 1.5:
            return "Low"
        elif risk_score < 2.5:
            return "Medium"
        else:
            return "High"


def generate_plan(investor_name=None, age=None, gender=None, number_of_dependents=None,
                 annual_income=None, investment_amount=None, horizon=None,
                 preferred_assets=None):   # ← new parameter
    """Generate investment plan filtered to user's preferred asset types."""

    dependents = number_of_dependents if number_of_dependents is not None else 0
    income     = annual_income        if annual_income is not None else 0
    amount     = investment_amount    if investment_amount is not None else 0

    if age is None or gender is None or income is None or amount is None or horizon is None:
        raise ValueError("Missing required parameters: age, gender, annual_income, investment_amount, horizon")

    # Predict risk level
    risk_level = predict_risk(age, gender, dependents, income, amount, horizon)

    # Get base allocation for this risk level
    allocation = ALLOCATION_TABLE.get(risk_level, ALLOCATION_TABLE["Medium"])

    # ── FILTER TO PREFERRED ASSETS ───────────────────────────────────────────
    # If user specified preferences, keep only those asset types
    if preferred_assets and len(preferred_assets) > 0:
        allocation = {
            asset: pct
            for asset, pct in allocation.items()
            if asset in preferred_assets
        }

    # ── RENORMALISE TO 100% ──────────────────────────────────────────────────
    # After filtering, percentages no longer sum to 100 — redistribute evenly
    if allocation:
        total_pct = sum(allocation.values())
        if total_pct > 0:
            allocation = {
                asset: round(pct / total_pct * 100, 2)
                for asset, pct in allocation.items()
            }
    else:
        # Fallback: if filtering removed everything, use full allocation
        allocation = ALLOCATION_TABLE.get(risk_level, ALLOCATION_TABLE["Medium"])

    # ── BUILD PLAN ───────────────────────────────────────────────────────────
    plan = []
    for asset_type, alloc_pct in allocation.items():
        asset      = BEST_ASSETS.get(asset_type, {})
        rupee_amt  = round(amount * alloc_pct / 100, 2)
        annual_ret = asset.get("annual_return", 0)
        exp_gain   = round(rupee_amt * annual_ret / 100, 2)

        plan.append({
            "asset_type":     asset_type,
            "asset_name":     asset.get("name", "---"),
            "allocation_pct": alloc_pct,
            "amount_inr":     rupee_amt,
            "annual_return":  annual_ret,
            "expected_gain":  exp_gain,
            "volatility":     asset.get("volatility", 0),
            "sharpe_ratio":   asset.get("sharpe_ratio", 0),
            "beta":           asset.get("beta", 0),
            "rsi":            asset.get("rsi", 0),
            "ma_20":          asset.get("ma_20", 0),
            "ma_50":          asset.get("ma_50", 0),
        })

    # ── BLENDED RETURN ───────────────────────────────────────────────────────
    blended = round(
        sum(r["allocation_pct"] / 100 * r["annual_return"] for r in plan), 2
    )

    return {
        "investor_name":   investor_name,
        "risk_level":      risk_level,
        "total_invested":  amount,
        "blended_return":  blended,
        "plan":            plan,
        "preferred_assets": preferred_assets,  # pass through for reference
    }


def sip_future_value(monthly_amount, annual_rate_pct, years):
    """SIP calculator using standard formula."""
    r = annual_rate_pct / 100 / 12
    n = years * 12
    if r == 0:
        return round(monthly_amount * n, 2)
    fv = monthly_amount * (((1 + r) ** n - 1) / r) * (1 + r)
    return round(fv, 2)