from fastapi import FastAPI
import pandas as pd
import joblib
import shap
import matplotlib
matplotlib.use("Agg")  # ✅ server safe
import matplotlib.pyplot as plt
import io, base64
import os
import lightgbm

app = FastAPI()

# ✅ Load model
MODEL_PATH = os.path.join("model", "terracred_classifier.joblib")
model = joblib.load(MODEL_PATH)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the same feature engineering as in training code."""
    df = df.copy()

    # engineered features
    df["log_price_volatility"] = np.log1p(df["price_volatility"])
    df["log_distance_to_market"] = np.log1p(df["distance_to_market_km"])
    df["rain_effect"] = df["rain_7d"] / (1.0 + df["dry_spell"])
    df["water_stress_index"] = (df["dry_spell"] / (df["rain_7d"] + 1.0)).clip(0, 5)
    df["soil_pH_dev"] = np.abs(df["soil_pH"] - 6.5)
    df["market_advantage"] = df["market_access_score"] - df["log_distance_to_market"]
    df["growth_outlook"] = (df["ndvi_trend_30d"] * 5000 + df["rain_forecast_14d"]).clip(-2000, 10000)
    df["digital_enablement"] = 0.6 * df["mobile_penetration_score"] + 0.4 * df["market_access_score"]
    df["irrigation_buffer"] = df["irrigation"] * (df["rain_forecast_14d"] * 0.15 + 500)
    crop_base_map = {"paddy":1.0,"wheat":1.0,"maize":0.95,"sugarcane":1.2,"cotton":1.05,"pulses":0.9}
    df["crop_income_multiplier"] = df["crop_type"].map(crop_base_map)

    return df


def return_farmer_outputs(phone_number):
    import numpy as np  # ✅ need np for transformations
    phone_number = int(phone_number)

    # ✅ load dataset with farmer features
    df = pd.read_csv(
        "https://raw.githubusercontent.com/ayanatherate/TerraCred-AI/refs/heads/main/data/Data_with_phone_numbers.csv"
    )
    df['Farmer_Phone_Number'] = [int(str(i)[2:]) for i in df['Farmer_Phone_Number'].values]

    try:
        df_col = df.loc[df['Farmer_Phone_Number'] == int(phone_number)]
        if df_col.empty:
            return {
                "phone_number": phone_number,
                "status": "not_found",
                "credit_limit": None,
                "loan_approval": None,
                "shap_waterfall_plot": None
            }

        cred_lim = int(df_col['credit_limit'].values[0])
        loan_approved = int(df_col['loan_approval'].values[0])

        # ✅ apply feature engineering
        df = engineer_features(df)
        df_col = engineer_features(df_col)

        # ✅ model features
        feature_cols = [c for c in df.columns if c not in ["Farmer_Phone_Number", "loan_approval", "credit_limit"]]
        farmer_features = df_col[feature_cols]

        # ✅ prediction
        prediction = model.predict(farmer_features)[0]

        # ✅ SHAP
        explainer = shap.Explainer(model, df[feature_cols])
        shap_values = explainer(farmer_features)

        plt.figure()
        shap.plots.waterfall(shap_values[0], show=False)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # ✅ response
        if loan_approved == 1:
            return {
                "phone_number": phone_number,
                "status": "approved",
                "credit_limit": cred_lim,
                "loan_approval": 1,
                "prediction": int(prediction),
                "top_positive_factors": [
                    "High NDVI (healthy crops)",
                    "Excellent repayment history",
                    "Irrigation access",
                    "PM-Kisan beneficiary"
                ],
                "risk_factors": ["High price volatility", "Distance to market"],
                "shap_waterfall_plot": img_base64
            }
        else:
            return {
                "phone_number": phone_number,
                "status": "rejected",
                "credit_limit": cred_lim,
                "loan_approval": 0,
                "prediction": int(prediction),
                "limiting_factors": [
                    "Past loan default",
                    "Poor soil nutrients",
                    "High yield variability",
                    "No irrigation access"
                ],
                "improvement_suggestions": [
                    "Soil testing and fertilization",
                    "Crop insurance enrollment",
                    "Join local FPO"
                ],
                "shap_waterfall_plot": img_base64
            }

    except Exception as e:
        return {
            "phone_number": phone_number,
            "status": "error",
            "error_message": str(e),
            "credit_limit": None,
            "loan_approval": None,
            "shap_waterfall_plot": None
        }


# ✅ GET endpoint
@app.get("/api/loan-status/{phone_number}")
async def api_get_loan_status(phone_number: str):
    return return_farmer_outputs(phone_number)


# ✅ POST endpoint
@app.post("/api/loan-status")
async def api_post_loan_status(payload: dict):
    phone_number = payload.get("phone_number")
    return return_farmer_outputs(phone_number)
