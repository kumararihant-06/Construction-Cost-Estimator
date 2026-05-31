from pydantic import BaseModel, Field
from typing import Optional

class EstimationRequest(BaseModel):
    project_type: str = Field(..., description="Residential, Commercial, or Industrial")
    location_tier: str = Field(..., description="Tier1, Tier2, or Tier3")
    size_sqft: float = Field(..., gt=0, description="Total area in square feet")
    num_floors: int = Field(..., ge=1, description="Number of floors")
    material_grade: str = Field(..., description="Budget, Standard, or Premium")
    duration_weeks: int = Field(..., ge=1, description="Project duration in weeks")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "project_type": "Commercial",
                    "location_tier": "Tier1",
                    "size_sqft": 25000,
                    "num_floors": 5,
                    "material_grade": "Premium",
                    "duration_weeks": 40
                }
            ]
        }
    }

class EstimationResponse(BaseModel):
    estimated_cost: float
    cost_low: float
    cost_high: float
    currency: str = "INR"
    risk_flags: list
    model_used: str
    confidence_note: str = "±15% prediction band based on model variance"

class ProjectCompareRequest(BaseModel):
    projects: list[EstimationRequest] = Field(..., max_length=5)

class RiskSummary(BaseModel):
    total_flags: int
    high_severity: int
    medium_severity: int
    low_severity: int