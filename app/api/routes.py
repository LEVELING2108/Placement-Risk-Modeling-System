"""
API routes for the placement-risk modeling system
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List, Dict
from datetime import datetime
import json
import os

from app.schemas.prediction import (
    StudentPredictionRequest,
    StudentPredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    SimulationRequest,
    SimulationResponse
)
from app.services.prediction_service import PredictionService
from app.core.config import settings
from app.api.deps import get_current_user

router = APIRouter()

# Initialize prediction service
prediction_service = PredictionService()

# Portfolio store with tenant isolation: {"tenant_id": {"student_id": data}}
portfolio_store: Dict[str, Dict[str, dict]] = {}

# Portfolio persistence helper
def save_portfolio():
    """Save portfolio store to file"""
    try:
        os.makedirs(os.path.dirname(settings.PORTFOLIO_PATH), exist_ok=True)
        with open(settings.PORTFOLIO_PATH, "w") as f:
            json.dump(portfolio_store, f)
    except Exception as e:
        print(f"Error saving portfolio: {e}")

def load_portfolio():
    """Load portfolio store from file"""
    global portfolio_store
    if os.path.exists(settings.PORTFOLIO_PATH):
        try:
            with open(settings.PORTFOLIO_PATH, "r") as f:
                portfolio_store = json.load(f)
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            portfolio_store = {}
    else:
        portfolio_store = {}

# Initialize portfolio storage
load_portfolio()


@router.post("/predict", response_model=StudentPredictionResponse)
async def predict_placement(
    request: StudentPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Predict placement timeline, salary, and risk for a single student
    """
    tenant_id = current_user["tenant_id"]
    try:
        response = prediction_service.predict_single(request)
        
        # Store in tenant's portfolio with FULL data for simulator
        if tenant_id not in portfolio_store:
            portfolio_store[tenant_id] = {}
            
        portfolio_store[tenant_id][request.student_id] = {
            "student_id": request.student_id,
            "academic": request.academic.model_dump(),
            "institute": request.institute.model_dump(),
            "labor_market": request.labor_market.model_dump(),
            "real_time_signals": request.real_time_signals.model_dump() if request.real_time_signals else {},
            "prediction": response.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        save_portfolio()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch-predict", response_model=BatchPredictionResponse)
async def batch_predict(
    request: BatchPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Predict placements for multiple students in batch
    """
    tenant_id = current_user["tenant_id"]
    try:
        students = request.students[:request.max_batch_size]
        results = prediction_service.predict_batch(students)
        
        # Store in tenant's portfolio
        if tenant_id not in portfolio_store:
            portfolio_store[tenant_id] = {}
            
        # Map requests to results to save full profiles
        results_map = {r.student_id: r for r in results}
        for stu_req in students:
            if stu_req.student_id in results_map:
                res = results_map[stu_req.student_id]
                portfolio_store[tenant_id][stu_req.student_id] = {
                    "student_id": stu_req.student_id,
                    "academic": stu_req.academic.model_dump(),
                    "institute": stu_req.institute.model_dump(),
                    "labor_market": stu_req.labor_market.model_dump(),
                    "real_time_signals": stu_req.real_time_signals.model_dump() if stu_req.real_time_signals else {},
                    "prediction": res.model_dump(),
                    "timestamp": datetime.now().isoformat()
                }
        
        save_portfolio()
        
        response = BatchPredictionResponse(
            total_requests=len(students),
            successful_predictions=len(results),
            failed_predictions=len(students) - len(results),
            results=results,
            errors=None
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_impact(
    request: SimulationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Simulate what-if scenarios
    """
    try:
        # Get base prediction
        original = prediction_service.predict_single(request.base_data)
        
        # Get simulated prediction
        simulated = prediction_service.simulate(request.base_data, request.modifications)
        
        # Calculate impact
        delta_risk = simulated.risk_assessment.placement_risk_score - original.risk_assessment.placement_risk_score
        delta_prob = simulated.placement_prediction.probability_6_months - original.placement_prediction.probability_6_months
        
        if delta_risk < -0.05:
            impact = "Significant risk reduction"
        elif delta_risk < 0:
            impact = "Minor risk reduction"
        elif delta_risk > 0.05:
            impact = "Significant risk increase"
        elif delta_risk > 0:
            impact = "Minor risk increase"
        else:
            impact = "No significant risk change"
            
        impact += f" and placement probability {'improved' if delta_prob > 0 else 'declined'} by {abs(delta_prob)*100:.1f}%."
        
        return SimulationResponse(
            student_id=request.base_data.student_id,
            original_prediction=original,
            simulated_prediction=simulated,
            delta_risk_score=round(delta_risk, 4),
            delta_placement_probability_6m=round(delta_prob, 4),
            impact_summary=impact
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/model-info")
async def get_model_info():
    """Get information about the loaded models and registry"""
    registry_path = "models/registry.json"
    registry_data = {}
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            registry_data = json.load(f)
            
    return {
        "model_version": settings.APP_VERSION,
        "models_loaded": prediction_service.models_loaded,
        "registry": registry_data,
        "placement_thresholds": {
            "3_months": settings.PLACEMENT_3M_THRESHOLD,
            "6_months": settings.PLACEMENT_6M_THRESHOLD,
            "12_months": settings.PLACEMENT_12M_THRESHOLD
        },
        "risk_thresholds": {
            "high_risk": settings.HIGH_RISK_THRESHOLD,
            "medium_risk": settings.MEDIUM_RISK_THRESHOLD
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "Placement-Risk Modeling System"
    }


# Portfolio Management Endpoints (Tenant-Aware)

@router.get("/portfolio")
async def get_portfolio(current_user: dict = Depends(get_current_user)):
    """Get all students in portfolio for current tenant"""
    tenant_id = current_user["tenant_id"]
    tenant_portfolio = portfolio_store.get(tenant_id, {})
    return {
        "total_students": len(tenant_portfolio),
        "students": list(tenant_portfolio.values())
    }


@router.get("/portfolio/stats")
async def get_portfolio_stats(current_user: dict = Depends(get_current_user)):
    """Get portfolio statistics for current tenant"""
    tenant_id = current_user["tenant_id"]
    tenant_portfolio = portfolio_store.get(tenant_id, {})
    
    if not tenant_portfolio:
        return {
            "total_students": 0,
            "risk_distribution": {"Low": 0, "Medium": 0, "High": 0},
            "average_risk_score": 0,
            "average_salary": 0,
            "timeline_distribution": {},
            "portfolio_health_score": 0
        }
    
    students = list(tenant_portfolio.values())
    
    # Risk distribution
    risk_dist = {"Low": 0, "Medium": 0, "High": 0}
    for s in students:
        pred = s.get('prediction', {})
        risk_assessment = pred.get('risk_assessment', {})
        risk_level = risk_assessment.get('risk_level')
        if risk_level in risk_dist:
            risk_dist[risk_level] += 1
    
    # Average risk score
    risk_scores = []
    salaries = []
    timelines = []
    
    for s in students:
        pred = s.get('prediction', {})
        risk_assessment = pred.get('risk_assessment', {})
        salary_pred = pred.get('salary_prediction', {})
        placement_pred = pred.get('placement_prediction', {})
        
        if 'placement_risk_score' in risk_assessment:
            risk_scores.append(risk_assessment['placement_risk_score'])
        if 'expected_salary_avg' in salary_pred:
            salaries.append(salary_pred['expected_salary_avg'])
        if 'predicted_timeline' in placement_pred:
            timelines.append(placement_pred['predicted_timeline'])
    
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    avg_salary = sum(salaries) / len(salaries) if salaries else 0
    
    from collections import Counter
    timeline_dist = dict(Counter(timelines))
    
    return {
        "total_students": len(students),
        "risk_distribution": risk_dist,
        "average_risk_score": round(avg_risk, 3),
        "average_salary": round(avg_salary, 2),
        "timeline_distribution": timeline_dist,
        "portfolio_health_score": round(1 - avg_risk, 3)
    }


@router.get("/analytics/risk-by-course")
async def analytics_risk_by_course(current_user: dict = Depends(get_current_user)):
    """Get risk distribution by course type for current tenant"""
    tenant_id = current_user["tenant_id"]
    tenant_portfolio = portfolio_store.get(tenant_id, {})
    
    course_risk = {}
    
    for student_id, s in tenant_portfolio.items():
        try:
            academic = s.get('academic', {})
            pred = s.get('prediction', {})
            course = academic.get('course_type') if isinstance(academic, dict) else None
            
            risk_assessment = pred.get('risk_assessment', {})
            risk_level = risk_assessment.get('risk_level') if isinstance(risk_assessment, dict) else None
            
            if course:
                if course not in course_risk:
                    course_risk[course] = {"Low": 0, "Medium": 0, "High": 0, "total": 0}
                
                if risk_level and risk_level in course_risk[course]:
                    course_risk[course][risk_level] += 1
                    course_risk[course]["total"] += 1
        except:
            continue
    
    return course_risk


@router.get("/analytics/risk-by-tier")
async def analytics_risk_by_tier(current_user: dict = Depends(get_current_user)):
    """Get risk distribution by institute tier for current tenant"""
    tenant_id = current_user["tenant_id"]
    tenant_portfolio = portfolio_store.get(tenant_id, {})
    
    tier_risk = {}
    
    for student_id, s in tenant_portfolio.items():
        try:
            institute = s.get('institute', {})
            pred = s.get('prediction', {})
            tier = institute.get('institute_tier') if isinstance(institute, dict) else None
            
            risk_assessment = pred.get('risk_assessment', {})
            risk_level = risk_assessment.get('risk_level') if isinstance(risk_assessment, dict) else None
            
            if tier:
                if tier not in tier_risk:
                    tier_risk[tier] = {"Low": 0, "Medium": 0, "High": 0, "total": 0}
                
                if risk_level and risk_level in tier_risk[tier]:
                    tier_risk[tier][risk_level] += 1
                    tier_risk[tier]["total"] += 1
        except:
            continue
    
    return tier_risk
