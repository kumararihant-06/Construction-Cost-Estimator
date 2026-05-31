from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import Literal
import pandas as pd

from models import EstimationRequest, EstimationResponse, ProjectCompareRequest
from estimator import train, predict, confidence_interval, get_model_name
from risk_engine import calculate_risk_flags
from data_pipeline import get_feature_stats

#Valid values for categorical inputs
VALID_PROJECT_TYPES = ['Residential', 'Commercial', 'Industrial']
VALID_LOCATION_TIERS = ['Tier1', 'Tier2', 'Tier3']
VALID_MATERIAL_GRADES = ['Budget', 'Standard', 'Premium']

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Train model once on startup - stays in memory
    print("Training ML model on startup...")
    train()
    print("Model ready.")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Construction Cost Estimator API",
    description="""
    ## India Construction Cost Estimator

    ML-powered REST API for estimating construction project costs and flagging operational risks.
    Built for Indian Tier1/Tier2/Tier3 city cost structures.

    ### Features
    - **Cost Estimation** — Predict total project cost in INR with confidence band
    - **Risk Analysis** — Domain-driven risk flags based on NBC 2016 and industry standards  
    - **Project Comparison** — Rank multiple project configurations by cost
    - **Dataset Insights** — Explore training data statistics""",
    version="1.0.0",
    contact={
        "name": "Arihant Kumar",
        "url": "https://github.com/kumararihant-06"
    },
    lifespan=lifespan
)

def validate_inputs(data: EstimationRequest):
    """Validate categorical inputs against allowed values."""
    if data.project_type not in VALID_PROJECT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"project_type must be one of {VALID_PROJECT_TYPES}"
        )
    if data.location_tier not in VALID_LOCATION_TIERS:
        raise HTTPException(
            status_code=422,
            detail=f"location_tier must be one of {VALID_LOCATION_TIERS}"
        )
    if data.material_grade not in VALID_MATERIAL_GRADES:
        raise HTTPException(
            status_code=422,
            detail=f"material_grade must be one of {VALID_MATERIAL_GRADES}"
        )
    
def run_estimation(data: EstimationRequest) -> dict:
    """Core estimation logic - reused by /estimate and /compare."""
    validate_inputs(data)

    input_dict = {
        'project_type': data.project_type,
        'location_tier': data.location_tier,
        'size_sqft': data.size_sqft,
        'num_floors': data.num_floors,
        'material_grade': data.material_grade,
        'duration_weeks': data.duration_weeks,
    }
    prediction = predict(input_dict)
    interval = confidence_interval(prediction)
    risks = calculate_risk_flags(input_dict)

    return {
        "estimated_cost": prediction,
        "cost_low": interval["low"],
        "cost_high": interval["high"],
        "currency": "INR",
        "risk_flags": risks,
        "model_used": get_model_name(),
        "confidence_note": "±15% prediction band based on model variance"
    }

#----- Endpoints ----------

@app.get("/", tags=["Health"])
async def health_check():
    """API health check."""
    return {"status": "healthy", "service": "Construction Cost Estimator API"}

@app.post("/estimate", response_model = EstimationResponse, tags=["Estimation"])
async def estimate(data: EstimationRequest):
    """
    Estimate total construction cost in INR with confidence band and risk flags.
    """
    return run_estimation(data)

@app.post("/compare", tags=["Analytics"])
async def compare(request: ProjectCompareRequest):
    """
    Compare up to 5 project configurations ranked by estimated cost ascending.
    Useful for choosing between project specs or material grades.
    """
    if len(request.projects) < 2:
        raise HTTPException(status_code=422, detail="Send at least 2 projects to compare.")

    results = []
    for i, project in enumerate(request.projects):
        estimation = run_estimation(project)
        results.append({
            "rank": 0,  # assigned after sorting
            "project_index": i + 1,
            "project_type": project.project_type,
            "location_tier": project.location_tier,
            "material_grade": project.material_grade,
            "size_sqft": project.size_sqft,
            "estimated_cost": estimation["estimated_cost"],
            "cost_low": estimation["cost_low"],
            "cost_high": estimation["cost_high"],
            "risk_flag_count": len(estimation["risk_flags"]),
            "high_severity_count": sum(1 for f in estimation["risk_flags"] if f["severity"] == "High")
        })

    # Sort by cost ascending and assign ranks
    results.sort(key=lambda x: x["estimated_cost"])
    for i, r in enumerate(results):
        r["rank"] = i + 1

    return {"projects_compared": len(results), "ranked_results": results}

@app.get("/project-types", tags=["Reference"])
async def project_types():
    """Returns valid project type values."""
    return {"types": VALID_PROJECT_TYPES}

@app.get("/location-tiers", tags=["Reference"])
async def location_tiers():
    """Returns valid location tier values with Indian city examples."""
    return {
        "tiers": {
            "Tier1": ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Hyderabad"],
            "Tier2": ["Pune", "Ahmedabad", "Jaipur", "Lucknow", "Bhopal"],
            "Tier3": ["Patna", "Ranchi", "Agra", "Vadodara", "Coimbatore"]
        }
    }

@app.get("/material-grades", tags=["Reference"])
async def material_grades():
    """Returns valid material grade values with descriptions."""
    return {
        "grades": {
            "Budget": "Local materials, meets minimum standards. 20% cost saving.",
            "Standard": "Standard market materials. BIS certified. Recommended baseline.",
            "Premium": "Imported or high-end materials. 35% cost premium."
        }
    }

@app.get("/risk-categories", tags=["Reference"])
async def risk_categories():
    """Returns all possible risk flag types with descriptions."""
    return {
        "risk_categories": [
            {"name": "Schedule Risk", "severity": "High",
             "description": "Project duration exceeds 52 weeks."},
            {"name": "Quality Risk", "severity": "High",
             "description": "Budget materials on Commercial projects risk non-compliance."},
            {"name": "Labor Escalation Risk", "severity": "Medium",
             "description": "Tier1 cities have high labor cost volatility."},
            {"name": "Complexity Risk", "severity": "Medium",
             "description": "Projects above 50,000 sqft need advanced management."},
            {"name": "Structural Risk", "severity": "High",
             "description": "Buildings above 10 floors require NBC 2016 compliance."}
        ]
    }

@app.get("/dataset-stats", tags=["Insights"])
async def dataset_stats():
    """Returns min/max/mean statistics from the training dataset."""
    return get_feature_stats()

@app.get("/cost-breakdown/{project_type}", tags=["Insights"])
async def cost_breakdown(project_type: str):
    """
    Returns average labor and material cost percentages for a given project type.
    """
    if project_type not in VALID_PROJECT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"project_type must be one of {VALID_PROJECT_TYPES}"
        )

    df = pd.read_csv('data/construction_data.csv')
    filtered = df[df['project_type'] == project_type]

    avg_labor_pct = round((filtered['labor_cost'] / filtered['total_cost']).mean() * 100, 1)
    avg_material_pct = round((filtered['material_cost'] / filtered['total_cost']).mean() * 100, 1)
    avg_other_pct = round(100 - avg_labor_pct - avg_material_pct, 1)

    return {
        "project_type": project_type,
        "sample_size": len(filtered),
        "average_cost_breakdown": {
            "labor_pct": avg_labor_pct,
            "material_pct": avg_material_pct,
            "other_pct": avg_other_pct
        },
        "note": "Other includes overhead, permits, equipment rental, and profit margin."
    }