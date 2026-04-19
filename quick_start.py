"""
Quick start script to demonstrate the system
"""

import sys
import os

def demo_without_api():
    """Demo the system without running the API"""
    print("="*70)
    print("PLACEMENT-RISK MODELING SYSTEM - DEMO")
    print("="*70)
    
    print("\n1. GENERATING SAMPLE STUDENT DATA")
    print("-" * 70)
    
    from app.services.data_generator import SampleDataGenerator
    
    generator = SampleDataGenerator(seed=42)
    
    # Generate students with different risk profiles
    for profile in ['low', 'medium', 'high']:
        student = generator.generate_single_student(
            student_id=f"DEMO_{profile.upper()}",
            risk_profile=profile
        )
        
        print(f"\n{profile.upper()} RISK STUDENT:")
        print(f"  Course: {student.academic.course_type.value}")
        print(f"  CGPA: {student.academic.cgpa}")
        print(f"  Internships: {student.academic.internship_count}")
        print(f"  Institute: {student.institute.institute_tier.value}")
        print(f"  Placement Rate (3m): {student.institute.historic_placement_rate_3m*100:.0f}%")
        print(f"  Job Demand: {student.labor_market.field_job_demand_score:.2f}")
    
    print("\n" + "="*70)
    print("2. SYSTEM COMPONENTS")
    print("-" * 70)
    
    print("\n✓ Data Preprocessor - Handles raw student data")
    print("✓ Feature Engineer - Creates predictive features")
    print("✓ Placement Model - Predicts 3/6/12 month timelines")
    print("✓ Salary Model - Estimates starting salary")
    print("✓ Risk Scoring - Calculates risk levels & factors")
    print("✓ Recommendation Engine - Generates AI summaries")
    print("✓ API Service - REST endpoints for predictions")
    
    print("\n" + "="*70)
    print("3. HOW TO USE")
    print("-" * 70)
    
    print("\nStep 1: Install dependencies")
    print("  pip install -r requirements.txt")
    
    print("\nStep 2: Train models")
    print("  python train.py")
    
    print("\nStep 3: Start API server")
    print("  python main.py")
    
    print("\nStep 4: Test the system")
    print("  python test_api.py")
    
    print("\n" + "="*70)
    print("4. KEY FEATURES")
    print("-" * 70)
    
    print("\n📊 Placement Prediction")
    print("  • 3-month placement probability")
    print("  • 6-month placement probability")
    print("  • 12-month placement probability")
    print("  • Timeline classification")
    
    print("\n💰 Salary Estimation")
    print("  • Expected salary range")
    print("  • Confidence intervals")
    print("  • Market-adjusted predictions")
    
    print("\n⚠️ Risk Assessment")
    print("  • Risk score (0-1)")
    print("  • Risk level (Low/Medium/High)")
    print("  • Risk factor identification")
    
    print("\n🎯 AI Recommendations")
    print("  • Automated summary generation")
    print("  • Actionable next steps")
    print("  • Recruiter matching")
    
    print("\n" + "="*70)
    print("5. OUTPUT EXAMPLE")
    print("-" * 70)
    
    print("""
{
  "student_id": "DEMO_001",
  "placement_prediction": {
    "probability_3_months": 0.75,
    "probability_6_months": 0.88,
    "probability_12_months": 0.95,
    "predicted_timeline": "Placed within 6 months"
  },
  "salary_prediction": {
    "expected_salary_avg": 500000,
    "confidence_interval_lower": 420000,
    "confidence_interval_upper": 580000
  },
  "risk_assessment": {
    "placement_risk_score": 0.35,
    "risk_level": "Medium",
    "risk_factors": [
      "Limited internship exposure",
      "Low field-wise job demand"
    ]
  },
  "recommendations": {
    "summary": "MEDIUM RISK: This student has moderate...",
    "next_best_actions": [
      "Apply for more internship opportunities",
      "Complete additional certifications"
    ]
  }
}
    """)
    
    print("\n" + "="*70)
    print("DEMO COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    try:
        demo_without_api()
    except ImportError as e:
        print(f"\n⚠️ Missing dependencies: {e}")
        print("Install them with: pip install -r requirements.txt")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
