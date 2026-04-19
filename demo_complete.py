"""
Complete End-to-End Demo Script
Showcases all features of the Placement-Risk Modeling System
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_subsection(title):
    """Print a formatted subsection header"""
    print(f"\n--- {title} ---")


def test_system_health():
    """Test 1: System Health Check"""
    print_section("TEST 1: SYSTEM HEALTH CHECK")
    
    response = requests.get(f"{BASE_URL}/api/v1/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ Service: {data['service']}")
        print(f"✅ Timestamp: {data['timestamp']}")
        return True
    else:
        print("❌ System health check failed")
        return False


def check_model_info():
    """Test 2: Model Information"""
    print_section("TEST 2: MODEL INFORMATION")
    
    response = requests.get(f"{BASE_URL}/api/v1/model-info")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Model Version: {data['model_version']}")
        print(f"✅ Models Loaded: {data['models_loaded']}")
        print(f"✅ Placement Thresholds:")
        print(f"   - 3 Months: {data['placement_thresholds']['3_months']}")
        print(f"   - 6 Months: {data['placement_thresholds']['6_months']}")
        print(f"   - 12 Months: {data['placement_thresholds']['12_months']}")
        return True
    else:
        print("❌ Model info check failed")
        return False


def single_prediction_demo():
    """Test 3: Single Student Prediction"""
    print_section("TEST 3: SINGLE STUDENT PREDICTION")
    
    student_data = {
        "student_id": "DEMO_STU_001",
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
    
    print_subsection("Student Profile")
    print(f"  Student ID: {student_data['student_id']}")
    print(f"  Course: {student_data['academic']['course_type']}")
    print(f"  CGPA: {student_data['academic']['cgpa']}")
    print(f"  Internships: {student_data['academic']['internship_count']}")
    print(f"  Institute: {student_data['institute']['institute_tier']}")
    
    print_subsection("Making Prediction...")
    response = requests.post(
        f"{BASE_URL}/api/v1/predict",
        json=student_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print_subsection("Prediction Results")
        print(f"\n📊 Placement Prediction:")
        print(f"  Timeline: {result['placement_prediction']['predicted_timeline']}")
        print(f"  3-Month Probability: {result['placement_prediction']['probability_3_months']*100:.1f}%")
        print(f"  6-Month Probability: {result['placement_prediction']['probability_6_months']*100:.1f}%")
        print(f"  12-Month Probability: {result['placement_prediction']['probability_12_months']*100:.1f}%")
        
        print(f"\n💰 Salary Estimation:")
        print(f"  Expected: ₹{result['salary_prediction']['expected_salary_avg']/100000:.2f} Lakhs")
        print(f"  Range: ₹{result['salary_prediction']['expected_salary_min']/100000:.2f}L - ₹{result['salary_prediction']['expected_salary_max']/100000:.2f}L")
        
        print(f"\n⚠️ Risk Assessment:")
        print(f"  Risk Level: {result['risk_assessment']['risk_level']}")
        print(f"  Risk Score: {result['risk_assessment']['placement_risk_score']*100:.1f}%")
        print(f"  Risk Factors:")
        for factor in result['risk_assessment']['risk_factors'][:3]:
            print(f"    - {factor}")
        
        print(f"\n🎯 Recommendations:")
        print(f"  Summary: {result['recommendations']['summary'][:100]}...")
        print(f"  Next Steps:")
        for action in result['recommendations']['next_best_actions'][:3]:
            print(f"    • {action}")
        
        return True
    else:
        print(f"❌ Prediction failed: {response.text}")
        return False


def different_risk_profiles():
    """Test 4: Different Risk Profiles"""
    print_section("TEST 4: DIFFERENT RISK PROFILES")
    
    profiles = [
        {
            "name": "LOW RISK STUDENT",
            "data": {
                "student_id": "LOW_RISK_001",
                "academic": {
                    "course_type": "Engineering",
                    "current_year": 4,
                    "semester": 8,
                    "cgpa": 8.5,
                    "academic_consistency": 0.9,
                    "internship_count": 3,
                    "total_internship_duration_months": 6.0,
                    "skill_certifications_count": 5,
                    "relevant_coursework_count": 10
                },
                "institute": {
                    "institute_tier": "Tier-1",
                    "historic_placement_rate_3m": 0.75,
                    "historic_placement_rate_6m": 0.88,
                    "historic_placement_rate_12m": 0.95,
                    "historic_avg_salary": 800000,
                    "placement_cell_activity_level": 0.85,
                    "recruiter_participation_score": 0.85
                },
                "labor_market": {
                    "field_job_demand_score": 0.85,
                    "region_job_density": 0.8,
                    "sector_hiring_trend": "IT",
                    "sector_hiring_growth": 0.25,
                    "macroeconomic_condition_score": 0.85
                },
                "real_time_signals": {
                    "job_portal_applications_count": 30,
                    "interview_pipeline_stage": 4,
                    "resume_updates_count": 5,
                    "skill_up_events_count": 6,
                    "institute_placement_progress": 0.8
                }
            }
        },
        {
            "name": "HIGH RISK STUDENT",
            "data": {
                "student_id": "HIGH_RISK_001",
                "academic": {
                    "course_type": "Arts",
                    "current_year": 3,
                    "semester": 6,
                    "cgpa": 5.5,
                    "academic_consistency": 0.4,
                    "internship_count": 0,
                    "total_internship_duration_months": 0,
                    "skill_certifications_count": 0,
                    "relevant_coursework_count": 2
                },
                "institute": {
                    "institute_tier": "Tier-3",
                    "historic_placement_rate_3m": 0.25,
                    "historic_placement_rate_6m": 0.45,
                    "historic_placement_rate_12m": 0.65,
                    "historic_avg_salary": 250000,
                    "placement_cell_activity_level": 0.35,
                    "recruiter_participation_score": 0.30
                },
                "labor_market": {
                    "field_job_demand_score": 0.3,
                    "region_job_density": 0.25,
                    "sector_hiring_trend": "Education",
                    "sector_hiring_growth": -0.1,
                    "macroeconomic_condition_score": 0.4
                },
                "real_time_signals": {
                    "job_portal_applications_count": 3,
                    "interview_pipeline_stage": 0,
                    "resume_updates_count": 1,
                    "skill_up_events_count": 0,
                    "institute_placement_progress": 0.15
                }
            }
        }
    ]
    
    all_success = True
    for profile in profiles:
        print_subsection(profile['name'])
        
        response = requests.post(
            f"{BASE_URL}/api/v1/predict",
            json=profile['data']
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Timeline: {result['placement_prediction']['predicted_timeline']}")
            print(f"  ✅ Risk: {result['risk_assessment']['risk_level']} ({result['risk_assessment']['placement_risk_score']*100:.0f}%)")
            print(f"  ✅ Salary: ₹{result['salary_prediction']['expected_salary_avg']/100000:.2f}L")
        else:
            print(f"  ❌ Failed")
            all_success = False
    
    return all_success


def portfolio_management():
    """Test 5: Portfolio Management"""
    print_section("TEST 5: PORTFOLIO MANAGEMENT")
    
    print_subsection("Getting Portfolio Statistics")
    response = requests.get(f"{BASE_URL}/api/v1/portfolio/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"  ✅ Total Students: {stats.get('total_students', 0)}")
        
        if 'risk_distribution' in stats:
            print(f"  ✅ Risk Distribution:")
            print(f"     Low: {stats['risk_distribution'].get('Low', 0)}")
            print(f"     Medium: {stats['risk_distribution'].get('Medium', 0)}")
            print(f"     High: {stats['risk_distribution'].get('High', 0)}")
        
        if 'portfolio_health_score' in stats:
            print(f"  ✅ Portfolio Health: {stats['portfolio_health_score']*100:.1f}%")
        
        return True
    else:
        print("  ❌ Failed to get portfolio stats")
        return False


def batch_analysis():
    """Test 6: Batch Analysis"""
    print_section("TEST 6: BATCH ANALYSIS")
    
    print_subsection("Analyzing 5 Students in Batch")
    
    students = []
    for i in range(5):
        students.append({
            "student_id": f"BATCH_{i+1}",
            "academic": {
                "course_type": ["Engineering", "MBA", "Science", "Commerce", "Nursing"][i],
                "current_year": 4,
                "semester": 8,
                "cgpa": 6.0 + i * 0.5,
                "academic_consistency": 0.6 + i * 0.05,
                "internship_count": i,
                "total_internship_duration_months": i * 1.5,
                "skill_certifications_count": i,
                "relevant_coursework_count": 3 + i
            },
            "institute": {
                "institute_tier": ["Tier-1", "Tier-1", "Tier-2", "Tier-2", "Tier-3"][i],
                "historic_placement_rate_3m": 0.7 - i * 0.1,
                "historic_placement_rate_6m": 0.85 - i * 0.08,
                "historic_placement_rate_12m": 0.95 - i * 0.05,
                "historic_avg_salary": 600000 - i * 80000,
                "placement_cell_activity_level": 0.8 - i * 0.1,
                "recruiter_participation_score": 0.75 - i * 0.1
            },
            "labor_market": {
                "field_job_demand_score": 0.7 + i * 0.03,
                "region_job_density": 0.6,
                "sector_hiring_trend": "IT",
                "sector_hiring_growth": 0.15,
                "macroeconomic_condition_score": 0.7
            },
            "real_time_signals": {
                "job_portal_applications_count": 10 + i * 5,
                "interview_pipeline_stage": i,
                "resume_updates_count": 2 + i,
                "skill_up_events_count": i,
                "institute_placement_progress": 0.5 + i * 0.05
            }
        })
    
    response = requests.post(
        f"{BASE_URL}/api/v1/batch-predict",
        json={"students": students, "max_batch_size": 10}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ Total Requests: {result['total_requests']}")
        print(f"  ✅ Successful: {result['successful_predictions']}")
        print(f"  ✅ Failed: {result['failed_predictions']}")
        
        if result['results']:
            print_subsection("Batch Results Summary")
            for r in result['results'][:5]:
                print(f"  • {r['student_id']}: {r['risk_assessment']['risk_level']} Risk - {r['placement_prediction']['predicted_timeline']}")
        
        return True
    else:
        print(f"  ❌ Batch analysis failed: {response.text}")
        return False


def analytics_demo():
    """Test 7: Analytics"""
    print_section("TEST 7: ANALYTICS")
    
    print_subsection("Risk by Course Type")
    response = requests.get(f"{BASE_URL}/api/v1/analytics/risk-by-course")
    if response.status_code == 200:
        try:
            data = response.json()
            if data and isinstance(data, dict) and 'message' not in data:
                for course, counts in data.items():
                    print(f"  {course}: {counts}")
                return True
            else:
                print("  ⚠️ No course data available yet")
                return True  # Not a failure, just no data
        except:
            print("  ⚠️ Analytics endpoint error")
            return False
    else:
        print(f"  ⚠️ Analytics returned {response.status_code}")
        return False
    
    print_subsection("Risk by Institute Tier")
    response = requests.get(f"{BASE_URL}/api/v1/analytics/risk-by-tier")
    if response.status_code == 200:
        try:
            data = response.json()
            if data and isinstance(data, dict) and 'message' not in data:
                for tier, counts in data.items():
                    print(f"  {tier}: {counts}")
                return True
            else:
                print("  ⚠️ No tier data available yet")
                return True  # Not a failure, just no data
        except:
            print("  ⚠️ Analytics endpoint error")
            return False
    else:
        print(f"  ⚠️ Analytics returned {response.status_code}")
        return False


def dashboard_access():
    """Test 8: Dashboard Access"""
    print_section("TEST 8: DASHBOARD ACCESS")
    
    print(f"  🌐 Dashboard URL: http://localhost:8000")
    print(f"  📚 API Documentation: http://localhost:8000/docs")
    
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200 and "DOCTYPE" in response.text:
        print(f"  ✅ Dashboard is accessible")
        print(f"  ✅ HTML content served correctly")
        return True
    else:
        print(f"  ❌ Dashboard access failed")
        return False


def export_demo():
    """Test 9: Data Export"""
    print_section("TEST 9: DATA EXPORT")
    
    print_subsection("Exporting Portfolio")
    response = requests.get(f"{BASE_URL}/api/v1/portfolio/export")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Export Date: {data.get('export_date', 'N/A')}")
        print(f"  ✅ Total Students: {data.get('total_students', 0)}")
        print(f"  ✅ Export format: JSON")
        return True
    else:
        print(f"  ⚠️ Export failed or portfolio empty")
        return False


def main():
    """Run complete end-to-end demo"""
    print("\n" + "="*70)
    print("  PLACEMENT-RISK MODELING SYSTEM")
    print("  Complete End-to-End Demonstration")
    print("="*70)
    print(f"\n  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: System Health
    results.append(("System Health", test_system_health()))
    time.sleep(0.5)
    
    # Test 2: Model Info
    results.append(("Model Information", check_model_info()))
    time.sleep(0.5)
    
    # Test 3: Single Prediction
    results.append(("Single Prediction", single_prediction_demo()))
    time.sleep(0.5)
    
    # Test 4: Different Profiles
    results.append(("Risk Profiles", different_risk_profiles()))
    time.sleep(0.5)
    
    # Test 5: Portfolio
    results.append(("Portfolio Management", portfolio_management()))
    time.sleep(0.5)
    
    # Test 6: Batch Analysis
    results.append(("Batch Analysis", batch_analysis()))
    time.sleep(0.5)
    
    # Test 7: Analytics
    results.append(("Analytics", analytics_demo()))
    time.sleep(0.5)
    
    # Test 8: Dashboard
    results.append(("Dashboard Access", dashboard_access()))
    time.sleep(0.5)
    
    # Test 9: Export
    results.append(("Data Export", export_demo()))
    
    # Summary
    print_section("DEMO SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n  Total Tests: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")
    print(f"  Success Rate: {passed/total*100:.1f}%\n")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print("\n" + "="*70)
    if passed == total:
        print("  🎉 ALL TESTS PASSED! System is fully operational!")
    else:
        print(f"  ⚠️  {total - passed} test(s) need attention")
    print("="*70)
    
    print(f"\n  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n  Next Steps:")
    print("  1. Open dashboard: http://localhost:8000")
    print("  2. View API docs: http://localhost:8000/docs")
    print("  3. Start making predictions!")
    print()


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("   Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
