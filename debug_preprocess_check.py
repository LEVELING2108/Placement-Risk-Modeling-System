"""
Check what the preprocessing produces
"""
import sys
sys.path.insert(0, "C:\\Users\\suman\\Downloads\\PERSONAL PROJECT\\Placement-Risk Modeling system")

from app.services.preprocessing import DataPreprocessor
from app.services.feature_engineering import FeatureEngineer
import json

test_data = {
    "student_id": "DEBUG_001",
    "academic": {
        "course_type": "Engineering",
        "current_year": 4,
        "semester": 8,
        "cgpa": 7.5,
        "academic_consistency": 0.75,
        "internship_count": 2,
        "total_internship_duration_months": 4.0,
        "internship_employer_type": "MNC",
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

preprocessor = DataPreprocessor()
df_processed = preprocessor.preprocess_student_data(test_data)

print("After preprocessing:")
print(f"Columns: {df_processed.columns.tolist()}")
print(f"Dtypes:\n{df_processed.dtypes}")
print()

# Check for object columns
obj_cols = df_processed.select_dtypes(include=['object']).columns
if len(obj_cols) > 0:
    print(f"⚠️ Object columns found: {obj_cols.tolist()}")
    for col in obj_cols:
        print(f"  {col}: {df_processed[col].values}")
else:
    print("✅ No object columns")

# Now feature engineering
fe = FeatureEngineer()
df_engineered = fe.engineer_features(df_processed)

print(f"\nAfter feature engineering:")
print(f"Columns: {df_engineered.columns.tolist()}")
print(f"Dtypes:\n{df_engineered.dtypes}")

# Check for object columns again
obj_cols = df_engineered.select_dtypes(include=['object']).columns
if len(obj_cols) > 0:
    print(f"\n⚠️ Object columns found: {obj_cols.tolist()}")
    for col in obj_cols:
        print(f"  {col}: {df_engineered[col].values}")
else:
    print("\n✅ No object columns after feature engineering")
