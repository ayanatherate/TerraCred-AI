from fastapi import FastAPI
import pandas as pd

app = FastAPI()

def return_farmer_outputs(phone_number):
    phone_number = int(phone_number)
    df = pd.read_csv(
        "https://raw.githubusercontent.com/ayanatherate/TerraCred-AI/refs/heads/main/data/Data_with_phone_numbers.csv"
    )
    df['Farmer_Phone_Number'] = [int(str(i)[2:]) for i in df['Farmer_Phone_Number'].values]

    try:
        df_col = df.loc[df['Farmer_Phone_Number'] == int(phone_number)]
        cred_lim = df_col['credit_limit'].values[0]
        loan_approved = df_col['loan_approval'].values[0]

        if loan_approved == 1:
            return {"phone_number": phone_number, "status": "approved", "credit_limit": int(cred_lim)}
        else:
            return {"phone_number": phone_number, "status": "rejected", "credit_limit": None}
    except:
        return {"phone_number": phone_number, "status": "not_found", "credit_limit": None}


# ✅ API 1: GET with phone number in path
@app.get("/api/loan-status/{phone_number}")
async def api_get_loan_status(phone_number: str):
    return return_farmer_outputs(phone_number)


# ✅ API 2: POST with phone number in JSON body
@app.post("/api/loan-status")
async def api_post_loan_status(payload: dict):
    phone_number = payload.get("phone_number")
    return return_farmer_outputs(phone_number)
