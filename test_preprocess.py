"""
Test prediction directly to debug the issue
"""
import sys
import os

# Add the project root to sys.path using relative path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.preprocessing import DataPreprocessor

preprocessor = DataPreprocessor()

test_data = {
    "student_id": "TEST_001",
    "academic": {
        "course_type": "Engineering",
        "current_year": 4,
        "semester": 8,
        "cgpa": 7.5,
        "academic_consistency": 0.75,
        "internship_count": 2,
        "total_internship_duration_months": 4.0,
        "skill_certifications_count": 3,
        "relevant_coursework_count": 6
    },
    "institute": {
        "institute_tier": "Tier-2",
        "historic_placement_rate_3m": 0.55,
        "historic_placement_rate_6m": 0.75,
        "historic_placement_rate_12m": 0.90,
        "historic_avg_salary": 500000,
        "placement_cell_activity_level": 0.7,
        "recruiter_participation_score": 0.65
    },
    "labor_market": {
        "field_job_demand_score": 0.7,
        "region_job_density": 0.6,
        "sector_hiring_trend": "IT",
        "sector_hiring_growth": 0.15,
        "macroeconomic_condition_score": 0.75
    },
    "real_time_signals": {
        "job_portal_applications_count": 20,
        "interview_pipeline_stage": 3,
        "resume_updates_count": 4,
        "skill_up_events_count": 3,
        "institute_placement_progress": 0.6
    }
}

try:
    result = preprocessor.preprocess_student_data(test_data)
    print("✅ Preprocessing succeeded!")
    print(f"Columns: {result.columns.tolist()}")
    print(f"Shape: {result.shape}")
    print(result.head())
except Exception as e:
    print(f"❌ Preprocessing failed: {e}")
    import traceback
    traceback.print_exc()
