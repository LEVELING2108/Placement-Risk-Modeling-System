
import requests
import random
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsZW5kZXJfYSIsInRlbmFudF9pZCI6InRlbmFudF9hIiwicm9sZSI6ImxlbmRlciIsImV4cCI6MTc3ODA4ODUzNX0.Tr86tZ_2pS_59Z3TfQd04de2oJZH08PX49Qs9heCb6s"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Configuration for realistic data generation
COURSES = [
    {"type": "Engineering", "weight": 0.30, "salary_base": 500000, "salary_range": 400000},
    {"type": "MBA", "weight": 0.15, "salary_base": 700000, "salary_range": 500000},
    {"type": "Nursing", "weight": 0.08, "salary_base": 350000, "salary_range": 150000},
    {"type": "Science", "weight": 0.10, "salary_base": 400000, "salary_range": 250000},
    {"type": "Commerce", "weight": 0.12, "salary_base": 450000, "salary_range": 200000},
    {"type": "Arts", "weight": 0.08, "salary_base": 300000, "salary_range": 150000},
    {"type": "Law", "weight": 0.05, "salary_base": 550000, "salary_range": 350000},
    {"type": "Medical", "weight": 0.07, "salary_base": 800000, "salary_range": 500000},
    {"type": "Pharmacy", "weight": 0.05, "salary_base": 380000, "salary_range": 180000}
]

INSTITUTE_TIERS = [
    {"tier": "Tier-1", "weight": 0.25, "placement_3m": (0.65, 0.85), "salary_mult": 1.4, "activity": (0.75, 0.95)},
    {"tier": "Tier-2", "weight": 0.45, "placement_3m": (0.40, 0.65), "salary_mult": 1.0, "activity": (0.55, 0.80)},
    {"tier": "Tier-3", "weight": 0.30, "placement_3m": (0.20, 0.45), "salary_mult": 0.7, "activity": (0.30, 0.60)}
]

SECTORS = ["IT", "BFSI", "Manufacturing", "Healthcare", "Education", "Retail", "Telecom", "Energy"]
EMPLOYER_TYPES = ["MNC", "Large Corporate", "Mid-size", "Startup", "Government"]


def weighted_choice(options):
    weights = [opt.get('weight', 1) for opt in options]
    return random.choices(options, weights=weights, k=1)[0]

def generate_student(index, risk_profile=None):
    course_config = weighted_choice(COURSES)
    course_type = course_config["type"]
    tier_config = weighted_choice(INSTITUTE_TIERS)
    tier = tier_config["tier"]
    
    if risk_profile == "low":
        cgpa = round(random.uniform(7.5, 9.5), 1)
        internship_count = random.randint(2, 5)
    elif risk_profile == "medium":
        cgpa = round(random.uniform(6.0, 7.8), 1)
        internship_count = random.randint(1, 3)
    else:
        cgpa = round(random.uniform(4.0, 6.5), 1)
        internship_count = random.randint(0, 2)
    
    placement_3m = round(random.uniform(*tier_config["placement_3m"]), 2)
    avg_salary = int((course_config["salary_base"] + random.uniform(-100000, 100000)) * tier_config["salary_mult"])
    
    return {
        "student_id": f"STU_{index:04d}",
        "academic": {
            "course_type": course_type,
            "current_year": 4,
            "semester": 8,
            "cgpa": cgpa,
            "academic_consistency": 0.8,
            "internship_count": internship_count,
            "total_internship_duration_months": internship_count * 2,
            "internship_employer_type": "MNC" if internship_count > 0 else None,
            "internship_performance_score": 0.85 if internship_count > 0 else None,
            "skill_certifications_count": 2,
            "relevant_coursework_count": 5
        },
        "institute": {
            "institute_tier": tier,
            "historic_placement_rate_3m": placement_3m,
            "historic_placement_rate_6m": placement_3m + 0.1,
            "historic_placement_rate_12m": placement_3m + 0.15,
            "historic_avg_salary": avg_salary,
            "placement_cell_activity_level": 0.8,
            "recruiter_participation_score": 0.85
        },
        "labor_market": {
            "field_job_demand_score": 0.8,
            "region_job_density": 0.7,
            "sector_hiring_trend": "IT",
            "sector_hiring_growth": 0.1,
            "macroeconomic_condition_score": 0.75
        },
        "real_time_signals": {
            "job_portal_applications_count": 20,
            "interview_pipeline_stage": 2,
            "resume_updates_count": 5,
            "skill_up_events_count": 3,
            "institute_placement_progress": 0.6
        }
    }

def main():
    print("Generating and seeding students...")
    students = []
    for i in range(1, 51):
        profile = random.choice(["low", "medium", "high"])
        students.append(generate_student(i, profile))
    
    success = 0
    for s in students:
        try:
            r = requests.post(f"{BASE_URL}/api/v1/predict", json=s, headers=HEADERS)
            if r.status_code == 200:
                success += 1
        except:
            pass
    print(f"Successfully seeded {success} students.")

if __name__ == "__main__":
    main()
