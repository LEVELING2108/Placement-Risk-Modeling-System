"""
Comprehensive example of using the Placement-Risk Modeling System
This script demonstrates all major features
"""

import json
from datetime import datetime
from app.services.data_generator import SampleDataGenerator
from app.services.prediction_service import PredictionService
from app.schemas.prediction import (
    StudentPredictionRequest,
    StudentAcademicData,
    InstituteData,
    LaborMarketData,
    RealTimeSignals,
    CourseType,
    InstituteTier,
    Sector
)


def create_custom_student():
    """Create a custom student profile"""
    
    print("\n" + "="*70)
    print("EXAMPLE 1: CREATING CUSTOM STUDENT PROFILE")
    print("="*70)
    
    # Create a student manually
    student = StudentPredictionRequest(
        student_id="CUSTOM_001",
        academic=StudentAcademicData(
            course_type=CourseType.ENGINEERING,
            current_year=4,
            semester=8,
            cgpa=7.8,
            academic_consistency=0.82,
            internship_count=2,
            total_internship_duration_months=5.0,
            internship_employer_type="MNC",
            internship_performance_score=0.85,
            skill_certifications_count=4,
            relevant_coursework_count=8
        ),
        institute=InstituteData(
            institute_tier=InstituteTier.TIER_1,
            historic_placement_rate_3m=0.72,
            historic_placement_rate_6m=0.88,
            historic_placement_rate_12m=0.95,
            historic_avg_salary=750000,
            placement_cell_activity_level=0.85,
            recruiter_participation_score=0.80
        ),
        labor_market=LaborMarketData(
            field_job_demand_score=0.78,
            region_job_density=0.72,
            sector_hiring_trend=Sector.IT,
            sector_hiring_growth=0.18,
            macroeconomic_condition_score=0.75
        ),
        real_time_signals=RealTimeSignals(
            job_portal_applications_count=25,
            interview_pipeline_stage=3,
            resume_updates_count=5,
            skill_up_events_count=4,
            institute_placement_progress=0.68
        )
    )
    
    print("\nCustom Student Created:")
    print(f"  Student ID: {student.student_id}")
    print(f"  Course: {student.academic.course_type.value}")
    print(f"  CGPA: {student.academic.cgpa}")
    print(f"  Institute: {student.institute.institute_tier.value}")
    print(f"  Sector: {student.labor_market.sector_hiring_trend.value}")
    
    return student


def demo_batch_predictions():
    """Demonstrate batch predictions"""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: BATCH PREDICTIONS")
    print("="*70)
    
    generator = SampleDataGenerator(seed=123)
    
    # Generate students with different profiles
    students = []
    for i, profile in enumerate(['low', 'medium', 'high']):
        student = generator.generate_single_student(
            student_id=f"BATCH_{i+1}",
            risk_profile=profile
        )
        students.append(student)
    
    print(f"\nGenerated {len(students)} students for batch prediction")
    print("Risk profiles: Low, Medium, High")
    
    return students


def demo_prediction_service():
    """Demonstrate the prediction service"""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: PREDICTION SERVICE DEMO")
    print("="*70)
    
    # Initialize services
    generator = SampleDataGenerator(seed=42)
    
    # Note: In production, you would load trained models here
    # predictor = PredictionService()
    # predictor.load_models()
    
    print("\n⚠️ Note: This demo shows the data flow without model inference")
    print("   To run actual predictions, first train models with: python train.py")
    
    # Generate sample student
    student = generator.generate_single_student(
        student_id="DEMO_001",
        risk_profile='medium'
    )
    
    print("\nStudent Profile:")
    print(f"  ID: {student.student_id}")
    print(f"  Course: {student.academic.course_type.value}")
    print(f"  CGPA: {student.academic.cgpa}")
    print(f"  Internships: {student.academic.internship_count}")
    print(f"  Institute Tier: {student.institute.institute_tier.value}")
    print(f"  Placement Rate (3m): {student.institute.historic_placement_rate_3m*100:.0f}%")
    
    print("\nExpected Prediction Output Structure:")
    expected_output = {
        "student_id": "DEMO_001",
        "timestamp": datetime.now().isoformat(),
        "placement_prediction": {
            "probability_3_months": 0.65,
            "probability_6_months": 0.82,
            "probability_12_months": 0.93,
            "predicted_timeline": "Placed within 6 months"
        },
        "salary_prediction": {
            "expected_salary_min": 450000,
            "expected_salary_max": 550000,
            "expected_salary_avg": 500000,
            "confidence_interval_lower": 420000,
            "confidence_interval_upper": 580000
        },
        "risk_assessment": {
            "placement_risk_score": 0.42,
            "risk_level": "Medium",
            "risk_factors": [
                "Moderate internship experience",
                "Average field job demand"
            ]
        },
        "recommendations": {
            "summary": "MEDIUM RISK: This student has moderate placement prospects with room for improvement...",
            "next_best_actions": [
                "Apply for more internship opportunities",
                "Complete additional certifications in high-demand skills",
                "Practice mock interviews with placement cell"
            ],
            "recruiter_matches": [
                "Tech Mahindra",
                "Infosys",
                "Wipro",
                "TCS",
                "Accenture"
            ]
        },
        "model_version": "1.0.0",
        "explainability_scores": {
            "internship_quality_score": 0.18,
            "institute_placement_strength": 0.15,
            "cgpa": 0.12,
            "market_opportunity_score": 0.11
        }
    }
    
    print(json.dumps(expected_output, indent=2))


def demo_lender_use_case():
    """Demonstrate lender portfolio use case"""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: LENDER PORTFOLIO RISK ASSESSMENT")
    print("="*70)
    
    generator = SampleDataGenerator(seed=456)
    
    # Simulate a loan portfolio of 20 students
    portfolio_size = 20
    print(f"\nAnalyzing loan portfolio with {portfolio_size} students...")
    
    # Generate portfolio
    portfolio = []
    for i in range(portfolio_size):
        profile = ['low', 'medium', 'high'][i % 3]  # Cycle through profiles
        student = generator.generate_single_student(
            student_id=f"LOAN_{i+1:03d}",
            risk_profile=profile
        )
        portfolio.append(student)
    
    # Simulate risk distribution
    low_risk = sum(1 for s in portfolio if s.institute.historic_placement_rate_3m > 0.6)
    medium_risk = sum(1 for s in portfolio if 0.4 <= s.institute.historic_placement_rate_3m <= 0.6)
    high_risk = sum(1 for s in portfolio if s.institute.historic_placement_rate_3m < 0.4)
    
    print("\nPortfolio Risk Distribution:")
    print(f"  Low Risk:    {low_risk} students ({low_risk/portfolio_size*100:.0f}%)")
    print(f"  Medium Risk: {medium_risk} students ({medium_risk/portfolio_size*100:.0f}%)")
    print(f"  High Risk:   {high_risk} students ({high_risk/portfolio_size*100:.0f}%)")
    
    print("\nLender Actions:")
    print("  ✓ Low Risk: Monitor normally, standard repayment schedule")
    print("  ⚡ Medium Risk: Offer skill development support, career counseling")
    print("  ⚠️ High Risk: Intensive intervention, modified repayment options")
    
    # Calculate portfolio risk score
    avg_placement_rate = sum(s.institute.historic_placement_rate_3m for s in portfolio) / portfolio_size
    portfolio_risk_score = 1 - avg_placement_rate
    
    print(f"\nPortfolio Health Metrics:")
    print(f"  Average 3-Month Placement Rate: {avg_placement_rate*100:.1f}%")
    print(f"  Portfolio Risk Score: {portfolio_risk_score:.2f}")
    
    if portfolio_risk_score < 0.3:
        print(f"  Overall Status: ✅ HEALTHY")
    elif portfolio_risk_score < 0.5:
        print(f"  Overall Status: ⚡ MODERATE RISK")
    else:
        print(f"  Overall Status: ⚠️ HIGH RISK - Action Required")


def demo_api_integration():
    """Demonstrate API integration"""
    
    print("\n" + "="*70)
    print("EXAMPLE 5: API INTEGRATION")
    print("="*70)
    
    print("\nTo integrate with the API:")
    print("\n1. Start the server:")
    print("   python main.py")
    print("\n2. Use the endpoints:")
    
    endpoints = {
        "Single Prediction": "POST /api/v1/predict",
        "Batch Prediction": "POST /api/v1/batch-predict",
        "Risk Score Only": "POST /api/v1/risk-score",
        "Model Info": "GET /api/v1/model-info",
        "Health Check": "GET /api/v1/health"
    }
    
    for name, endpoint in endpoints.items():
        print(f"   {name}: {endpoint}")
    
    print("\n3. Example curl command:")
    print("""
    curl -X POST "http://localhost:8000/api/v1/predict" \\
      -H "Content-Type: application/json" \\
      -d '{
        "student_id": "API_TEST_001",
        "academic": {
          "course_type": "Engineering",
          "current_year": 4,
          "semester": 8,
          "cgpa": 7.5,
          "academic_consistency": 0.75,
          "internship_count": 2,
          "total_internship_duration_months": 4.5,
          "skill_certifications_count": 3,
          "relevant_coursework_count": 6
        },
        "institute": {
          "institute_tier": "Tier-2",
          "historic_placement_rate_3m": 0.55,
          "historic_placement_rate_6m": 0.75,
          "historic_placement_rate_12m": 0.85,
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
          "skill_up_events_count": 3
        }
      }'
    """)


def main():
    """Run all examples"""
    
    print("\n" + "="*70)
    print("PLACEMENT-RISK MODELING SYSTEM - COMPREHENSIVE EXAMPLES")
    print("="*70)
    
    try:
        # Example 1: Custom student
        student = create_custom_student()
        
        # Example 2: Batch predictions
        students = demo_batch_predictions()
        
        # Example 3: Prediction service
        demo_prediction_service()
        
        # Example 4: Lender use case
        demo_lender_use_case()
        
        # Example 5: API integration
        demo_api_integration()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETE!")
        print("="*70)
        
        print("\nNext Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Train models: python train.py")
        print("3. Start API: python main.py")
        print("4. Test system: python test_api.py")
        print("5. View docs: README.md")
        
    except ImportError as e:
        print(f"\n⚠️ Missing dependencies: {e}")
        print("Install them with: pip install -r requirements.txt")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
