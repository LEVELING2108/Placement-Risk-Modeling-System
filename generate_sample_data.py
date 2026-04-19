"""
Generate and load 100 sample students into the portfolio
Creates diverse profiles across different risk levels, courses, and institute tiers
"""

import requests
import random
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

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
    """Choose from list of dicts with 'weight' key"""
    weights = [opt.get('weight', 1) for opt in options]
    return random.choices(options, weights=weights, k=1)[0]


def random_range(low, high):
    """Get random value in range"""
    return round(random.uniform(low, high), 2)


def generate_student(index, risk_profile=None):
    """Generate a realistic student profile"""
    
    # Select course
    course_config = weighted_choice(COURSES)
    course_type = course_config["type"]
    
    # Select institute tier
    tier_config = weighted_choice(INSTITUTE_TIERS)
    tier = tier_config["tier"]
    
    # If risk_profile is specified, bias the selection
    if risk_profile:
        if risk_profile == "low":
            # Bias towards Tier-1, high CGPA, more internships
            if random.random() < 0.7:
                tier_config = INSTITUTE_TIERS[0]  # Tier-1
                tier = tier_config["tier"]
            cgpa = round(random.uniform(7.5, 9.5), 1)
            academic_consistency = round(random.uniform(0.75, 0.98), 2)
            internship_count = random.randint(2, 5)
            internship_duration = round(random.uniform(3.0, 8.0), 1)
            certifications = random.randint(3, 8)
            coursework = random.randint(8, 15)
            job_demand = round(random.uniform(0.65, 0.95), 2)
            job_density = round(random.uniform(0.60, 0.90), 2)
            sector_growth = round(random.uniform(0.05, 0.35), 2)
            macro_score = round(random.uniform(0.65, 0.90), 2)
            apps_count = random.randint(15, 40)
            interview_stage = random.randint(2, 5)
            resume_updates = random.randint(3, 8)
            skill_events = random.randint(3, 8)
            
        elif risk_profile == "medium":
            cgpa = round(random.uniform(6.0, 7.8), 1)
            academic_consistency = round(random.uniform(0.55, 0.78), 2)
            internship_count = random.randint(1, 3)
            internship_duration = round(random.uniform(1.0, 4.0), 1)
            certifications = random.randint(1, 4)
            coursework = random.randint(4, 9)
            job_demand = round(random.uniform(0.40, 0.70), 2)
            job_density = round(random.uniform(0.40, 0.65), 2)
            sector_growth = round(random.uniform(-0.05, 0.15), 2)
            macro_score = round(random.uniform(0.50, 0.70), 2)
            apps_count = random.randint(8, 20)
            interview_stage = random.randint(1, 3)
            resume_updates = random.randint(2, 5)
            skill_events = random.randint(1, 4)
            
        else:  # high risk
            if random.random() < 0.6:
                tier_config = INSTITUTE_TIERS[2]  # Tier-3
                tier = tier_config["tier"]
            cgpa = round(random.uniform(4.0, 6.5), 1)
            academic_consistency = round(random.uniform(0.25, 0.60), 2)
            internship_count = random.randint(0, 2)
            internship_duration = round(random.uniform(0, 2.0), 1)
            certifications = random.randint(0, 2)
            coursework = random.randint(1, 5)
            job_demand = round(random.uniform(0.15, 0.45), 2)
            job_density = round(random.uniform(0.15, 0.45), 2)
            sector_growth = round(random.uniform(-0.20, 0.05), 2)
            macro_score = round(random.uniform(0.25, 0.55), 2)
            apps_count = random.randint(0, 10)
            interview_stage = random.randint(0, 2)
            resume_updates = random.randint(0, 3)
            skill_events = random.randint(0, 2)
    else:
        # Random profile
        cgpa = round(random.uniform(4.5, 9.2), 1)
        academic_consistency = round(random.uniform(0.30, 0.95), 2)
        internship_count = random.randint(0, 4)
        internship_duration = round(random.uniform(0, 6.0), 1)
        certifications = random.randint(0, 6)
        coursework = random.randint(2, 12)
        job_demand = round(random.uniform(0.20, 0.90), 2)
        job_density = round(random.uniform(0.20, 0.85), 2)
        sector_growth = round(random.uniform(-0.15, 0.30), 2)
        macro_score = round(random.uniform(0.30, 0.90), 2)
        apps_count = random.randint(2, 35)
        interview_stage = random.randint(0, 5)
        resume_updates = random.randint(0, 7)
        skill_events = random.randint(0, 7)
    
    # Calculate institute-specific values
    placement_3m_range = tier_config["placement_3m"]
    placement_3m = round(random.uniform(*placement_3m_range), 2)
    placement_6m = round(min(0.95, placement_3m + random.uniform(0.10, 0.20)), 2)
    placement_12m = round(min(0.98, placement_6m + random.uniform(0.05, 0.12)), 2)
    
    salary_base = course_config["salary_base"]
    salary_range = course_config["salary_range"]
    salary_mult = tier_config["salary_mult"]
    avg_salary = int((salary_base + random.uniform(-salary_range/2, salary_range/2)) * salary_mult)
    
    activity_range = tier_config["activity"]
    activity = round(random.uniform(*activity_range), 2)
    recruiter_score = round(random.uniform(activity - 0.15, activity + 0.05), 2)
    recruiter_score = max(0.2, min(0.95, recruiter_score))
    
    student = {
        "student_id": f"STU_{index:04d}",
        "academic": {
            "course_type": course_type,
            "current_year": random.choice([3, 3, 4, 4, 4, 5]),
            "semester": random.randint(5, 10),
            "cgpa": cgpa,
            "academic_consistency": academic_consistency,
            "internship_count": internship_count,
            "total_internship_duration_months": internship_duration,
            "internship_employer_type": random.choice(EMPLOYER_TYPES) if internship_count > 0 else None,
            "internship_performance_score": round(random.uniform(0.5, 0.95), 2) if internship_count > 0 else None,
            "skill_certifications_count": certifications,
            "relevant_coursework_count": coursework
        },
        "institute": {
            "institute_tier": tier,
            "historic_placement_rate_3m": placement_3m,
            "historic_placement_rate_6m": placement_6m,
            "historic_placement_rate_12m": placement_12m,
            "historic_avg_salary": avg_salary,
            "placement_cell_activity_level": activity,
            "recruiter_participation_score": recruiter_score
        },
        "labor_market": {
            "field_job_demand_score": job_demand,
            "region_job_density": job_density,
            "sector_hiring_trend": random.choice(SECTORS),
            "sector_hiring_growth": sector_growth,
            "macroeconomic_condition_score": macro_score
        },
        "real_time_signals": {
            "job_portal_applications_count": apps_count,
            "interview_pipeline_stage": interview_stage,
            "resume_updates_count": resume_updates,
            "skill_up_events_count": skill_events,
            "institute_placement_progress": round(random.uniform(0.2, 0.85), 2)
        }
    }
    
    return student


def load_students_to_api(students, batch_size=20):
    """Load students to the API in batches"""
    results = {
        "total": len(students),
        "success": 0,
        "failed": 0,
        "errors": []
    }
    
    print(f"\nLoading {len(students)} students to API in batches of {batch_size}...")
    
    for i in range(0, len(students), batch_size):
        batch = students[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1}: Students {i+1}-{min(i+batch_size, len(students))}")
        
        for student in batch:
            try:
                response = requests.post(
                    f"{BASE_URL}/api/v1/predict",
                    json=student,
                    timeout=30
                )
                
                if response.status_code == 200:
                    results["success"] += 1
                    if results["success"] % 10 == 0:
                        print(f"  ✓ Loaded {results['success']} students so far...")
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "student_id": student["student_id"],
                        "status": response.status_code,
                        "error": response.text[:100]
                    })
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "student_id": student["student_id"],
                    "error": str(e)[:100]
                })
    
    return results


def print_summary(students, api_results):
    """Print summary of generated data"""
    print("\n" + "="*70)
    print("  SAMPLE DATA GENERATION SUMMARY")
    print("="*70)
    
    # Count by course
    course_counts = {}
    for s in students:
        course = s["academic"]["course_type"]
        course_counts[course] = course_counts.get(course, 0) + 1
    
    # Count by tier
    tier_counts = {}
    for s in students:
        tier = s["institute"]["institute_tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    print(f"\n📊 Total Students Generated: {len(students)}")
    print(f"✅ Successfully Loaded: {api_results['success']}")
    print(f"❌ Failed: {api_results['failed']}")
    
    print(f"\n📚 Distribution by Course:")
    for course, count in sorted(course_counts.items(), key=lambda x: -x[1]):
        pct = count / len(students) * 100
        print(f"  {course:15s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\n🏛️ Distribution by Institute Tier:")
    for tier, count in sorted(tier_counts.items()):
        pct = count / len(students) * 100
        print(f"  {tier:15s}: {count:3d} ({pct:5.1f}%)")
    
    # Salary range
    salaries = [s["institute"]["historic_avg_salary"] for s in students]
    print(f"\n💰 Historic Salary Range:")
    print(f"  Minimum: ₹{min(salaries)/100000:.2f} Lakhs")
    print(f"  Average: ₹{sum(salaries)/len(salaries)/100000:.2f} Lakhs")
    print(f"  Maximum: ₹{max(salaries)/100000:.2f} Lakhs")
    
    # CGPA range
    cgpas = [s["academic"]["cgpa"] for s in students]
    print(f"\n📈 CGPA Range:")
    print(f"  Minimum: {min(cgpas):.1f}")
    print(f"  Average: {sum(cgpas)/len(cgpas):.1f}")
    print(f"  Maximum: {max(cgpas):.1f}")
    
    # Internship stats
    internships = [s["academic"]["internship_count"] for s in students]
    print(f"\n💼 Internship Stats:")
    print(f"  Students with 0 internships: {sum(1 for i in internships if i == 0)}")
    print(f"  Students with 1-2 internships: {sum(1 for i in internships if 1 <= i <= 2)}")
    print(f"  Students with 3+ internships: {sum(1 for i in internships if i >= 3)}")
    
    if api_results["errors"]:
        print(f"\n⚠️ Errors ({len(api_results['errors'])}):")
        for err in api_results["errors"][:5]:
            print(f"  - {err.get('student_id', 'unknown')}: {err.get('error', 'unknown')}")
    
    print("\n" + "="*70)
    print("  ✅ SAMPLE DATA LOADED SUCCESSFULLY!")
    print("="*70)
    print(f"\n  View in dashboard: http://localhost:8000")
    print(f"  Check portfolio: GET http://localhost:8000/api/v1/portfolio")
    print(f"  View stats: GET http://localhost:8000/api/v1/portfolio/stats")
    print()


def main():
    """Generate and load 100 sample students"""
    print("\n" + "="*70)
    print("  PLACEMENT-RISK MODELING SYSTEM")
    print("  Sample Data Generator - 100 Students")
    print("="*70)
    print(f"\n  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Generate 100 students with balanced risk profiles
    students = []
    
    # Generate 35 low risk students
    print("\nGenerating 35 Low Risk students...")
    for i in range(35):
        students.append(generate_student(len(students)+1, risk_profile="low"))
    
    # Generate 40 medium risk students
    print("Generating 40 Medium Risk students...")
    for i in range(40):
        students.append(generate_student(len(students)+1, risk_profile="medium"))
    
    # Generate 25 high risk students
    print("Generating 25 High Risk students...")
    for i in range(25):
        students.append(generate_student(len(students)+1, risk_profile="high"))
    
    # Shuffle to mix risk profiles
    random.shuffle(students)
    
    # Re-number sequentially after shuffle
    for i, student in enumerate(students):
        student["student_id"] = f"STU_{i+1:04d}"
    
    print(f"\n✅ Generated {len(students)} students")
    
    # Check if API is available
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is available, loading students...")
            results = load_students_to_api(students, batch_size=20)
            print_summary(students, results)
        else:
            print("⚠️ API health check failed, saving to file only")
            save_to_file(students)
    except requests.exceptions.ConnectionError:
        print("⚠️ API is not running, saving to file only")
        save_to_file(students)
    except Exception as e:
        print(f"⚠️ Error checking API: {e}")
        save_to_file(students)


def save_to_file(students):
    """Save students to JSON file"""
    filename = "sample_students_100.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(students)} students to {filename}")
    print("\nYou can load them later when the API is running using:")
    print(f"  python load_sample_data.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Generation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
