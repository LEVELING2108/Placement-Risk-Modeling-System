"""
Test script for the placement-risk modeling system
"""

import requests
import json
from app.services.data_generator import SampleDataGenerator
from app.schemas.prediction import StudentPredictionRequest


def test_api_endpoint(base_url: str = "http://localhost:8000"):
    """Test the API endpoints with sample data"""
    
    print("="*60)
    print("TESTING API ENDPOINTS")
    print("="*60)
    
    # Generate sample student
    generator = SampleDataGenerator(seed=42)
    student = generator.generate_single_student(
        student_id="TEST_001",
        risk_profile='medium'
    )
    
    # Test single prediction
    print("\n1. Testing single prediction endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/predict",
            json=student.model_dump()
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Single prediction successful!")
            print(f"\nStudent ID: {result['student_id']}")
            print(f"Placement Timeline: {result['placement_prediction']['predicted_timeline']}")
            print(f"3-Month Probability: {result['placement_prediction']['probability_3_months']*100:.1f}%")
            print(f"6-Month Probability: {result['placement_prediction']['probability_6_months']*100:.1f}%")
            print(f"12-Month Probability: {result['placement_prediction']['probability_12_months']*100:.1f}%")
            print(f"Expected Salary: ₹{result['salary_prediction']['expected_salary_avg']/100000:.2f} Lakhs")
            print(f"Risk Level: {result['risk_assessment']['risk_level']}")
            print(f"Risk Score: {result['risk_assessment']['placement_risk_score']*100:.1f}%")
            print(f"\nSummary: {result['recommendations']['summary'][:150]}...")
        else:
            print(f"✗ Single prediction failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"✗ Could not connect to API: {e}")
    
    # Test risk score endpoint
    print("\n2. Testing risk score endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/risk-score",
            json=student.model_dump()
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Risk score endpoint successful!")
            print(f"Risk Level: {result['risk_assessment']['risk_level']}")
            print(f"Risk Factors: {', '.join(result['risk_assessment']['risk_factors'][:3])}")
        else:
            print(f"✗ Risk score failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Could not connect to API: {e}")
    
    # Test batch prediction
    print("\n3. Testing batch prediction endpoint...")
    try:
        # Generate 5 students
        students = [
            generator.generate_single_student(
                student_id=f"BATCH_{i+1}",
                risk_profile='random'
            )
            for i in range(5)
        ]
        
        batch_request = {
            "students": [s.model_dump() for s in students],
            "max_batch_size": 10
        }
        
        response = requests.post(
            f"{base_url}/api/v1/batch-predict",
            json=batch_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Batch prediction successful!")
            print(f"Total Requests: {result['total_requests']}")
            print(f"Successful: {result['successful_predictions']}")
            print(f"Failed: {result['failed_predictions']}")
        else:
            print(f"✗ Batch prediction failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Could not connect to API: {e}")
    
    # Test model info
    print("\n4. Testing model info endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/model-info")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Model info retrieved!")
            print(f"Model Version: {result['model_version']}")
            print(f"Models Loaded: {result['models_loaded']}")
        else:
            print(f"✗ Model info failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Could not connect to API: {e}")
    
    # Test health check
    print("\n5. Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        
        if response.status_code == 200:
            print("✓ Health check passed!")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Could not connect to API: {e}")

    # Test simulation endpoint
    print("\n6. Testing simulation endpoint...")
    try:
        sim_data = {
            "base_data": student.model_dump(),
            "modifications": {
                "academic.cgpa": 9.5,
                "academic.internship_count": 4
            }
        }
        response = requests.post(
            f"{base_url}/api/v1/simulate",
            json=sim_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Simulation successful!")
            print(f"Impact Summary: {result['impact_summary']}")
            print(f"Original Risk: {result['original_prediction']['risk_assessment']['placement_risk_score']*100:.1f}%")
            print(f"Simulated Risk: {result['simulated_prediction']['risk_assessment']['placement_risk_score']*100:.1f}%")
            print(f"Risk Delta: {result['delta_risk_score']*100:.1f}%")
        else:
            print(f"✗ Simulation failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"✗ Could not connect to API: {e}")


def test_different_risk_profiles():
    """Test predictions for different risk profiles"""
    
    print("\n" + "="*60)
    print("TESTING DIFFERENT RISK PROFILES")
    print("="*60)
    
    generator = SampleDataGenerator(seed=42)
    
    for profile in ['low', 'medium', 'high']:
        print(f"\n{profile.upper()} RISK PROFILE:")
        print("-"*60)
        
        student = generator.generate_single_student(
            student_id=f"TEST_{profile.upper()}",
            risk_profile=profile
        )
        
        print(f"CGPA: {student.academic.cgpa}")
        print(f"Internships: {student.academic.internship_count}")
        print(f"Institute Tier: {student.institute.institute_tier.value}")
        print(f"Placement Rate (3m): {student.institute.historic_placement_rate_3m*100:.0f}%")
        print(f"Job Demand Score: {student.labor_market.field_job_demand_score}")


if __name__ == "__main__":
    print("\nPLACEMENT-RISK MODELING SYSTEM - TEST SUITE\n")
    
    # Test with API (if running)
    test_api_endpoint()
    
    # Test risk profiles
    test_different_risk_profiles()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE!")
    print("="*60)
