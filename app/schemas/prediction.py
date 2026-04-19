"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CourseType(str, Enum):
    ENGINEERING = "Engineering"
    MBA = "MBA"
    NURSING = "Nursing"
    ARTS = "Arts"
    SCIENCE = "Science"
    COMMERCE = "Commerce"
    LAW = "Law"
    MEDICAL = "Medical"
    PHARMACY = "Pharmacy"
    OTHER = "Other"


class InstituteTier(str, Enum):
    TIER_1 = "Tier-1"
    TIER_2 = "Tier-2"
    TIER_3 = "Tier-3"


class Sector(str, Enum):
    IT = "IT"
    BFSI = "BFSI"
    MANUFACTURING = "Manufacturing"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    RETAIL = "Retail"
    TELECOM = "Telecom"
    ENERGY = "Energy"
    OTHER = "Other"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class StudentAcademicData(BaseModel):
    """Student academic and program information"""
    course_type: CourseType
    current_year: int = Field(..., ge=1, le=5, description="Current year of study")
    semester: int = Field(..., ge=1, le=10, description="Current semester")
    cgpa: float = Field(..., ge=0, le=10, description="Cumulative GPA")
    academic_consistency: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Academic consistency score (0-1)"
    )
    internship_count: int = Field(default=0, ge=0, description="Number of internships")
    total_internship_duration_months: float = Field(
        default=0, 
        ge=0, 
        description="Total internship duration in months"
    )
    internship_employer_type: Optional[str] = Field(
        default=None, 
        description="Type of internship employer (MNC, Startup, Government, etc.)"
    )
    internship_performance_score: Optional[float] = Field(
        default=None, 
        ge=0, 
        le=1, 
        description="Internship performance rating (0-1)"
    )
    skill_certifications_count: int = Field(
        default=0, 
        ge=0, 
        description="Number of skill certifications"
    )
    relevant_coursework_count: int = Field(
        default=0, 
        ge=0, 
        description="Number of relevant coursework completed"
    )


class InstituteData(BaseModel):
    """Institute and program-level data"""
    institute_tier: InstituteTier
    historic_placement_rate_3m: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Historic 3-month placement rate"
    )
    historic_placement_rate_6m: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Historic 6-month placement rate"
    )
    historic_placement_rate_12m: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Historic 12-month placement rate"
    )
    historic_avg_salary: float = Field(..., gt=0, description="Historic average salary")
    placement_cell_activity_level: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Placement cell activity level (0-1)"
    )
    recruiter_participation_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Recruiter participation score (0-1)"
    )


class LaborMarketData(BaseModel):
    """Industry and labor-market indicators"""
    field_job_demand_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Job demand score for student's field"
    )
    region_job_density: float = Field(..., ge=0, le=1, description="Regional job density")
    sector_hiring_trend: Sector
    sector_hiring_growth: float = Field(
        ..., 
        ge=-1, 
        le=1, 
        description="Sector hiring growth (-1 to 1)"
    )
    macroeconomic_condition_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Macroeconomic condition score (0-1)"
    )


class RealTimeSignals(BaseModel):
    """Student behavior and real-time signals (optional)"""
    job_portal_applications_count: int = Field(
        default=0, 
        ge=0, 
        description="Number of job applications submitted"
    )
    interview_pipeline_stage: Optional[int] = Field(
        default=None, 
        ge=0, 
        le=5, 
        description="Current interview pipeline stage (0-5)"
    )
    resume_updates_count: int = Field(
        default=0, 
        ge=0, 
        description="Number of resume updates"
    )
    skill_up_events_count: int = Field(
        default=0, 
        ge=0, 
        description="Number of skill-up events"
    )
    institute_placement_progress: Optional[float] = Field(
        default=None, 
        ge=0, 
        le=1, 
        description="Institute-shared placement progress"
    )


class StudentPredictionRequest(BaseModel):
    """Complete prediction request"""
    student_id: str
    academic: StudentAcademicData
    institute: InstituteData
    labor_market: LaborMarketData
    real_time_signals: Optional[RealTimeSignals] = None
    prediction_date: Optional[datetime] = None


class PlacementPrediction(BaseModel):
    """Placement timeline prediction"""
    probability_3_months: float = Field(..., ge=0, le=1)
    probability_6_months: float = Field(..., ge=0, le=1)
    probability_12_months: float = Field(..., ge=0, le=1)
    predicted_timeline: str = Field(
        ..., 
        description="Predicted placement timeline (3/6/12 months or delayed)"
    )


class SalaryPrediction(BaseModel):
    """Salary estimation"""
    expected_salary_min: float
    expected_salary_max: float
    expected_salary_avg: float
    confidence_interval_lower: float
    confidence_interval_upper: float


class RiskAssessment(BaseModel):
    """Risk scoring and classification"""
    placement_risk_score: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    risk_factors: List[str] = Field(
        ..., 
        description="List of risk factors identified"
    )


class Recommendation(BaseModel):
    """AI-generated recommendations"""
    summary: str = Field(..., description="AI-generated summary explaining the risk")
    next_best_actions: List[str] = Field(
        ..., 
        description="Suggested next-best actions"
    )
    recruiter_matches: Optional[List[str]] = Field(
        default=None, 
        description="High-potential recruiter matches"
    )
    is_ai_generated: bool = Field(
        default=False, 
        description="True if recommendations were generated by an LLM"
    )


class StudentPredictionResponse(BaseModel):
    """Complete prediction response"""
    model_config = {"protected_namespaces": ()}
    
    student_id: str
    timestamp: datetime
    placement_prediction: PlacementPrediction
    salary_prediction: SalaryPrediction
    risk_assessment: RiskAssessment
    recommendations: Recommendation
    model_version: str
    explainability_scores: Optional[dict] = Field(
        default=None, 
        description="Feature importance scores for explainability"
    )


class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    students: List[StudentPredictionRequest]
    max_batch_size: int = Field(default=100, ge=1, le=1000)


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    total_requests: int
    successful_predictions: int
    failed_predictions: int
    results: List[StudentPredictionResponse]
    errors: Optional[List[dict]] = None


class SimulationRequest(BaseModel):
    """Request for What-If simulation"""
    base_data: StudentPredictionRequest
    modifications: dict = Field(
        ..., 
        description="Dictionary of fields to modify. Use dot notation for nested fields, e.g., {'academic.cgpa': 9.0}"
    )


class SimulationResponse(BaseModel):
    """Response for What-If simulation"""
    student_id: str
    original_prediction: StudentPredictionResponse
    simulated_prediction: StudentPredictionResponse
    delta_risk_score: float
    delta_placement_probability_6m: float
    impact_summary: str
