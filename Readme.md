# Construction Cost Estimator API

ML-powered REST API for estimating construction project costs and flagging operational risks for the Indian market. Built with FastAPI and scikit-learn, calibrated to Indian Tier1/Tier2/Tier3 city cost structures.

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.9 | Runtime |
| FastAPI | API framework |
| scikit-learn | ML model (Linear Regression + Random Forest) |
| Pandas | Data pipeline and feature engineering |
| Pydantic v2 | Request validation |
| Uvicorn | ASGI server |
| Uvicorn | Local Development Server |

## How It Works

1. **Data Pipeline** — 500-row synthetic dataset of Indian construction projects processed with Pandas. Categorical columns (project type, location tier, material grade) one-hot encoded for ML input.
2. **Model Training** — Linear Regression and Random Forest trained on startup. Better model selected automatically by R2 score.
3. **API Endpoints** — FastAPI exposes estimation, comparison, and risk analysis endpoints with auto-generated Swagger docs.

## How to Run Locally

```bash
git clone https://github.com/kumararihant-06/construction-cost-api.git
cd construction-cost-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | / | Health check |
| POST | /estimate | Estimate project cost in INR with risk flags |
| POST | /compare | Compare up to 5 project configs ranked by cost |
| GET | /project-types | Valid project type values |
| GET | /location-tiers | Valid tiers with Indian city examples |
| GET | /material-grades | Material grade descriptions |
| GET | /risk-categories | All possible risk flag types |
| GET | /dataset-stats | Training data statistics |
| GET | /cost-breakdown/{project_type} | Average labor/material cost breakdown |

## Sample Request

`POST /estimate`

```json
{
  "project_type": "Commercial",
  "location_tier": "Tier1",
  "size_sqft": 25000,
  "num_floors": 5,
  "material_grade": "Premium",
  "duration_weeks": 40
}
```

## Sample Response

```json
{
  "estimated_cost": 5466484.36,
  "cost_low": 4646511.71,
  "cost_high": 6286457.01,
  "currency": "INR",
  "risk_flags": [
    {
      "flag": "Labor Escalation Risk",
      "severity": "Medium",
      "description": "Tier1 cities like Mumbai and Delhi have high labor cost volatility.",
      "mitigation": "Lock in labor contracts early. Add 15% labor cost buffer to budget."
    }
  ],
  "model_used": "LinearRegression",
  "confidence_note": "±15% prediction band based on model variance"
}
```

## Notes

- Costs are in INR, calibrated to Indian construction market rates
- Trained on synthetic data demonstrating the full ML pipeline; production deployment would retrain on real historical project data
- Risk engine based on NBC 2016 compliance rules and Indian construction industry standards