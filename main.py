from fastapi import FastAPI
import pandas as pd
import joblib
import shap
import matplotlib
matplotlib.use("Agg")  # ✅ for server environments (no GUI)
import matplotlib.pyplot as plt
import io, base64
import os

app = FastAPI()

# ✅ Load model at startup
MODEL_PATH = os.path.join("model", "terracred_classifier.joblib")
model = joblib.load(MODEL_PATH)

def return_farmer_outputs(phone_number):
    phone_number = int(phone_number)
    df = pd.read_csv(
        "https://raw.githubusercontent.com/ayanatherate/TerraCred-AI/refs/heads/main/data/Data_with_phone_numbers.csv"
    )
    df['Farmer_Phone_Number'] = [int(str(i)[2:]) for i in df['Farmer_Phone_Number'].values]

    try:
        # Extract farmer row
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

        # Drop identifier + target to get features for prediction
        feature_cols = [c for c in df.columns if c not in ["Farmer_Phone_Number", "loan_approval", "credit_limit"]]
        farmer_features = df_col[feature_cols]

        # ✅ Prediction (probability or class)
        prediction = model.predict(farmer_features)[0]

        # ✅ SHAP explainer
        explainer = shap.Explainer(model, df[feature_cols])
        shap_values = explainer(farmer_features)

        # ✅ Generate SHAP waterfall plot
        plt.figure()
        shap.plots.waterfall(shap_values[0], show=False)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # ✅ Build response JSON
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
                "risk_factors": [
                    "High price volatility",
                    "Distance to market"
                ],
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


# ✅ API 1: GET with phone number in path
@app.get("/api/loan-status/{phone_number}")
async def api_get_loan_status(phone_number: str):
    return return_farmer_outputs(phone_number)


# ✅ API 2: POST with phone number in JSON body
@app.post("/api/loan-status")
async def api_post_loan_status(payload: dict):
    phone_number = payload.get("phone_number")
    return return_farmer_outputs(phone_number)
