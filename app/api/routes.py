"""
API routes for the placement-risk modeling system (Database-Driven)
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.schemas.prediction import (
    StudentPredictionRequest,
    StudentPredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    SimulationRequest,
    SimulationResponse,
    PlacementPrediction,
    SalaryPrediction,
    RiskAssessment,
    Recommendation
)
from app.services.prediction_service import PredictionService
from app.core.config import settings
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models import User, StudentProfile, PredictionResult, ModelRegistry

router = APIRouter()

# Initialize prediction service
prediction_service = PredictionService()


@router.post("/predict", response_model=StudentPredictionResponse)
async def predict_placement(
    request: StudentPredictionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict placement timeline, salary, and risk for a single student and save to DB
    """
    tenant_id = current_user["tenant_id"]
    try:
        response = prediction_service.predict_single(request)
        
        # 1. Save Student Profile
        student = StudentProfile(
            student_id=request.student_id,
            tenant_id=tenant_id,
            academic_data=request.academic.model_dump(),
            institute_data=request.institute.model_dump(),
            labor_market_data=request.labor_market.model_dump(),
            real_time_signals=request.real_time_signals.model_dump() if request.real_time_signals else {}
        )
        db.add(student)
        db.flush() # Get student ID
        
        # 2. Save Prediction Result
        prediction = PredictionResult(
            student_profile_id=student.id,
            lender_id=current_user["id"],
            tenant_id=tenant_id,
            placement_risk_score=response.risk_assessment.placement_risk_score,
            risk_level=response.risk_assessment.risk_level.value,
            predicted_timeline=response.placement_prediction.predicted_timeline,
            expected_salary_avg=response.salary_prediction.expected_salary_avg,
            full_prediction=response.model_dump()
        )
        db.add(prediction)
        db.commit()
        
        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch-predict", response_model=BatchPredictionResponse)
async def batch_predict(
    request: BatchPredictionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict placements for multiple students in batch and save to DB
    """
    tenant_id = current_user["tenant_id"]
    try:
        students = request.students[:request.max_batch_size]
        results = prediction_service.predict_batch(students)
        
        results_map = {r.student_id: r for r in results}
        
        for stu_req in students:
            if stu_req.student_id in results_map:
                res = results_map[stu_req.student_id]
                
                # Save Profile
                student = StudentProfile(
                    student_id=stu_req.student_id,
                    tenant_id=tenant_id,
                    academic_data=stu_req.academic.model_dump(),
                    institute_data=stu_req.institute.model_dump(),
                    labor_market_data=stu_req.labor_market.model_dump(),
                    real_time_signals=stu_req.real_time_signals.model_dump() if stu_req.real_time_signals else {}
                )
                db.add(student)
                db.flush()
                
                # Save Prediction
                prediction = PredictionResult(
                    student_profile_id=student.id,
                    lender_id=current_user["id"],
                    tenant_id=tenant_id,
                    placement_risk_score=res.risk_assessment.placement_risk_score,
                    risk_level=res.risk_assessment.risk_level.value,
                    predicted_timeline=res.placement_prediction.predicted_timeline,
                    expected_salary_avg=res.salary_prediction.expected_salary_avg,
                    full_prediction=res.model_dump()
                )
                db.add(prediction)
        
        db.commit()
        
        return BatchPredictionResponse(
            total_requests=len(students),
            successful_predictions=len(results),
            failed_predictions=len(students) - len(results),
            results=results,
            errors=None
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_impact(
    request: SimulationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Simulate what-if scenarios (Transient, not saved to DB)
    """
    try:
        original = prediction_service.predict_single(request.base_data)
        simulated = prediction_service.simulate(request.base_data, request.modifications)
        
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
async def get_model_info(db: Session = Depends(get_db)):
    """Get information about the loaded models and registry from DB"""
    latest_registry = db.query(ModelRegistry).filter(ModelRegistry.is_active == True).order_by(ModelRegistry.trained_at.desc()).first()
    
    registry_data = {}
    if latest_registry:
        registry_data = {
            "version": latest_registry.version,
            "trained_at": latest_registry.trained_at.isoformat(),
            "metrics": latest_registry.metrics,
            "feature_count": latest_registry.feature_count
        }
            
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


# Portfolio Management Endpoints (Tenant-Aware & DB-Powered)

@router.get("/portfolio")
async def get_portfolio(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all students in portfolio for current tenant from DB"""
    tenant_id = current_user["tenant_id"]
    
    # Query joined profiles and predictions
    results = db.query(StudentProfile, PredictionResult).join(
        PredictionResult, StudentProfile.id == PredictionResult.student_profile_id
    ).filter(StudentProfile.tenant_id == tenant_id).all()
    
    students = []
    for profile, pred in results:
        students.append({
            "student_id": profile.student_id,
            "academic": profile.academic_data,
            "institute": profile.institute_data,
            "labor_market": profile.labor_market_data,
            "real_time_signals": profile.real_time_signals,
            "prediction": pred.full_prediction,
            "timestamp": pred.created_at.isoformat()
        })
        
    return {
        "total_students": len(students),
        "students": students
    }


@router.get("/portfolio/stats")
async def get_portfolio_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio statistics using SQL aggregations"""
    tenant_id = current_user["tenant_id"]
    
    # Total count
    total = db.query(PredictionResult).filter(PredictionResult.tenant_id == tenant_id).count()
    
    if total == 0:
        return {
            "total_students": 0,
            "risk_distribution": {"Low": 0, "Medium": 0, "High": 0},
            "average_risk_score": 0,
            "average_salary": 0,
            "portfolio_health_score": 1.0
        }
    
    # Risk Distribution
    risk_counts = db.query(
        PredictionResult.risk_level, func.count(PredictionResult.id)
    ).filter(PredictionResult.tenant_id == tenant_id).group_by(PredictionResult.risk_level).all()
    
    risk_dist = {"Low": 0, "Medium": 0, "High": 0}
    for level, count in risk_counts:
        if level in risk_dist:
            risk_dist[level] = count
            
    # Average Stats
    avg_stats = db.query(
        func.avg(PredictionResult.placement_risk_score),
        func.avg(PredictionResult.expected_salary_avg)
    ).filter(PredictionResult.tenant_id == tenant_id).first()
    
    avg_risk = avg_stats[0] or 0
    avg_salary = avg_stats[1] or 0
    
    return {
        "total_students": total,
        "risk_distribution": risk_dist,
        "average_risk_score": round(avg_risk, 3),
        "average_salary": round(avg_salary, 2),
        "portfolio_health_score": round(1 - avg_risk, 3)
    }


@router.get("/analytics/risk-by-course")
async def analytics_risk_by_course(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get risk distribution by course type using joined query"""
    tenant_id = current_user["tenant_id"]
    
    # This is a bit more complex in SQL but much faster
    results = db.query(StudentProfile, PredictionResult).join(
        PredictionResult, StudentProfile.id == PredictionResult.student_profile_id
    ).filter(StudentProfile.tenant_id == tenant_id).all()
    
    course_risk = {}
    for profile, pred in results:
        course = profile.academic_data.get('course_type')
        if not course: continue
        
        if course not in course_risk:
            course_risk[course] = {"Low": 0, "Medium": 0, "High": 0, "total": 0}
            
        level = pred.risk_level
        if level in course_risk[course]:
            course_risk[course][level] += 1
            course_risk[course]["total"] += 1
            
    return course_risk


@router.get("/analytics/risk-by-tier")
async def analytics_risk_by_tier(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get risk distribution by institute tier using joined query"""
    tenant_id = current_user["tenant_id"]
    
    results = db.query(StudentProfile, PredictionResult).join(
        PredictionResult, StudentProfile.id == PredictionResult.student_profile_id
    ).filter(StudentProfile.tenant_id == tenant_id).all()
    
    tier_risk = {}
    for profile, pred in results:
        tier = profile.institute_data.get('institute_tier')
        if not tier: continue
        
        if tier not in tier_risk:
            tier_risk[tier] = {"Low": 0, "Medium": 0, "High": 0, "total": 0}
            
        level = pred.risk_level
        if level in tier_risk[tier]:
            tier_risk[tier][level] += 1
            tier_risk[tier]["total"] += 1
            
    return tier_risk
