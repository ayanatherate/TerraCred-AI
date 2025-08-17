# TerraCred™: End-to-End Predictive Credit Scoring for Smallholder Farmers

## 1. Problem Statement
Smallholder farmers in India often face **limited access to timely credit**, especially during crucial agricultural windows.  
Traditional credit evaluation methods depend on:
- Lengthy paperwork  
- Collateral requirements  
- Outdated credit bureau scores that ignore ground realities like crop health or weather risks  

As a result, farmers miss the **optimal time for Kisan Credit Card (KCC) top-ups**, affecting yield and income.

**TerraCred™** aims to solve this by:
- Leveraging publicly available, zero-cost datasets (NDVI, IMD rainfall, Soil Health Cards, govt. beneficiary lists).  
- Using an **AI-powered model** that predicts an instant, explainable credit limit recommendation.  
- Running entirely on **low-cost hardware (₹2,500 Raspberry Pi Zero)** for offline, rural environments.  
- Returning results in the **farmer’s native language** via missed call, SMS, WhatsApp, or chatbot.  

---

## 2. Data Features

TerraCred™ combines **environmental, socio-economic, market, and risk indicators**.  
Each feature is chosen to reflect **real-world agricultural finance determinants**.

| Feature | Meaning | Why it Matters |
|---------|---------|----------------|
| `ndvi_max` | Max NDVI in last month | Crop vigor & vegetation health |
| `ndvi_trend_30d` | NDVI growth rate over 30 days | Indicates crop improvement/decline |
| `rain_7d` | Rainfall in past 7 days (mm) | Recent water availability |
| `rain_forecast_14d` | Forecasted rainfall next 14 days | Early warning for drought/flood |
| `dry_spell` | Consecutive dry days | Long dry spells reduce yield |
| `soil_N`, `soil_K` | Nitrogen & Potassium | Key macronutrients for growth |
| `soil_pH` | Soil acidity/alkalinity | Extreme values reduce nutrient uptake |
| `price_volatility` | Std. dev. of crop prices | High volatility → uncertain income |
| `avg_crop_price_last_3m` | Avg. price of primary crop | Higher prices → more income potential |
| `pmkisan_beneficiary` | Govt. PM-Kisan support (0/1) | Ongoing financial aid |
| `plot_size_acres` | Cultivated land size | Larger plots → higher income |
| `irrigation` | Irrigation access (0/1) | Reduces dependency on rainfall |
| `past_default` | Loan default history (0/1) | Strong negative signal |
| `past_repayment_rate` | Timely repayment fraction | Consistent repayment → creditworthy |
| `yield_variability_3y` | 3-year yield variability | High variability = unstable income |
| `loan_tenure_months` | Avg. repayment duration | Longer → higher exposure risk |
| `market_access_score` | Road/mandi/transport index | Better access = better returns |
| `mobile_penetration_score` | Proxy for digital literacy | Enables digital repayment |
| `fpo_membership` | FPO membership (0/1) | Improves bargaining & resilience |
| `fertilizer_subsidy` | Subsidy beneficiary (0/1) | Lowers input burden |
| `crop_insurance` | Has crop insurance (0/1) | Mitigates disaster risk |
| `crop_type` | Primary crop grown | Each crop has unique cycles/risks |
| `distance_to_market_km` | Distance to market | Longer = lower net returns |

---

## 3. Data Transformations
Domain-driven transformations mimic real-world farming & finance dynamics:
1. **Scaling & clipping** → Ensure NDVI, nutrients, rainfall stay realistic.  
2. **Penalties for extremes** → Soil pH deviation from 6.5 reduces credit score.  
3. **Non-linear effects** → Rainfall impact diminishes beyond optimal threshold.  
4. **Interaction effects** → Example: Rainfall forecast × NDVI trend = seasonal boost.  
5. **Risk integration** → Defaults, poor repayment, unstable yields = downward penalty.  
6. **Social boosts** → Govt. schemes (PM-Kisan, FPO, subsidies, insurance) give positive credit.  

---

## 4. Target Variable: Credit Limit and a binary indicator indicating whether the farmer will be eligible or not


- **Base Potential** = NDVI, soil nutrients, irrigation, soil pH  
- **Seasonal Factor** = Rainfall, dry spells, NDVI trend, forecast  
- **Market Factor** = Market access, crop prices, volatility  
- **Social Factor** = Govt. aid, subsidies, insurance, FPO membership  
- **Size Factor** = Plot size scaling  
- **Risk Penalty** = Defaults, repayment rate, yield variability, distance to market  
- **Noise** = Random natural variation  

All values are clipped to **₹0 – ₹100,000**.  

---

## 5. Model Choice: LightGBM
We use **LightGBM** because it:
- Handles mixed feature types (continuous, categorical, binary).  
- Efficient on **3,000+ row datasets** (synthetic or real).  
- Captures **non-linear feature interactions** automatically.  
- Provides **feature importance** natively.  
- Integrates seamlessly with **SHAP explainability**.  

Fallback: **RandomForestRegressor** if LightGBM is unavailable.  

---

## 6. Explainability: SHAP Values
We apply **SHAP** post-training to:
- Quantify each feature’s effect on predictions.  
- Show **positive vs. negative contributions** for each farmer.  
- Highlight **top drivers** (e.g., NDVI health ↑, price volatility ↓).  

Example SHAP outputs:
<img width="1280" height="1280" alt="permutation_importance_top25" src="https://github.com/user-attachments/assets/5e26f41f-e160-4620-8ae5-cae0df76b3e3" />



