from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

def return_farmer_outputs(phone_number):
    phone_number=int(phone_number)
    print(phone_number)
    df = pd.read_csv(r"https://raw.githubusercontent.com/ayanatherate/TerraCred-AI/refs/heads/main/data/Data_with_phone_numbers.csv")
    df['Farmer_Phone_Number']=[int(str(i)[2:]) for i in df['Farmer_Phone_Number'].values]
    print(df['Farmer_Phone_Number'].values[0])
    
    try:
        df_col = df.loc[df['Farmer_Phone_Number'] == int(phone_number)]
        cred_lim = df_col['credit_limit'].values[0]
        loan_approved = df_col['loan_approval'].values[0]
        
        if loan_approved == 1:
            return f'Congrats you can have a loan and your credit_limit is {cred_lim}'
        else:
            return f'Sorry! Your loan cannot be approved'
    except:
        return 'Farmer Phone Number not registered in the Database.'

@app.get("/", response_class=HTMLResponse)
async def get_form():
    """Interactive form to input phone number"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Farmer Loan Check</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .form-container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
            input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
            input[type="submit"] { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
            input[type="submit"]:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>Farmer Loan Status Check</h2>
            <form action="/check-loan" method="post">
                <label for="phone_number">Enter Farmer's Phone Number:</label>
                <input type="text" id="phone_number" name="phone_number" required>
                <input type="submit" value="Check Loan Status">
            </form>
        </div>
    </body>
    </html>
    """
    return html_content

@app.post("/check-loan", response_class=HTMLResponse)
async def check_loan_status(phone_number: str = Form(...)):
    """Process form submission and return result"""
    result = return_farmer_outputs(phone_number)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loan Status Result</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .result-container {{ background: #f5f5f5; padding: 30px; border-radius: 10px; }}
            .result {{ padding: 15px; background: #e9ecef; border-radius: 5px; margin: 20px 0; }}
            .back-btn {{ background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            .back-btn:hover {{ background: #545b62; }}
        </style>
    </head>
    <body>
        <div class="result-container">
            <h2>Loan Status Result</h2>
            <p><strong>Phone Number:</strong> {phone_number}</p>
            <div class="result">
                <strong>Status:</strong> {result}
            </div>
            <a href="/" class="back-btn">Check Another Number</a>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/farmer/{phone_number}")
async def get_farmer_loan_status(phone_number: str):
    return {"message": return_farmer_outputs(phone_number)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)