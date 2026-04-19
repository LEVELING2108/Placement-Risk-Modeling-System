"""
Test script for the placement-risk modeling system (Phase 2 with Auth)
"""

import requests
import json
from app.services.data_generator import SampleDataGenerator

BASE_URL = "http://localhost:8000/api/v1"

def test_system():
    print("="*60)
    print("TESTING PLACEMENT-RISK SYSTEM (PHASE 2)")
    print("="*60)

    # 1. Authentication
    print("\n1. Testing Authentication...")
    login_data = {
        "username": "lender_a",
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            tenant_id = response.json()["tenant_id"]
            print(f"✓ Login successful! Tenant: {tenant_id}")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"✗ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return

    # 2. Model Info (No Auth)
    print("\n2. Testing Model Info & Registry...")
    response = requests.get(f"{BASE_URL}/model-info")
    if response.status_code == 200:
        info = response.json()
        print(f"✓ Model Version: {info['model_version']}")
        if info.get('registry'):
            print(f"✓ Trained at: {info['registry']['trained_at']}")
            print(f"✓ Features: {info['registry']['feature_count']}")
    else:
        print(f"✗ Model info failed: {response.status_code}")

    # 3. Single Prediction
    print("\n3. Testing Single Prediction (Tenant A)...")
    generator = SampleDataGenerator(seed=42)
    student = generator.generate_single_student(student_id="TENANT_A_STU_1", risk_profile='low')
    
    response = requests.post(f"{BASE_URL}/predict", json=student.model_dump(), headers=headers)
    if response.status_code == 200:
        print("✓ Prediction successful!")
        print(f"Risk Score: {response.json()['risk_assessment']['placement_risk_score']*100:.1f}%")
    else:
        print(f"✗ Prediction failed: {response.status_code}")

    # 4. Multi-Tenancy Check
    print("\n4. Testing Multi-Tenancy Isolation...")
    # Login as Lender B
    login_b = {"username": "lender_b", "password": "password123"}
    token_b = requests.post(f"{BASE_URL}/auth/login", data=login_b).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # Portfolio of B should be empty
    port_b = requests.get(f"{BASE_URL}/portfolio", headers=headers_b).json()
    print(f"✓ Lender B Portfolio size: {len(port_b['students'])} (Expected 0)")
    
    # Portfolio of A should have 1
    port_a = requests.get(f"{BASE_URL}/portfolio", headers=headers).json()
    print(f"✓ Lender A Portfolio size: {len(port_a['students'])} (Expected 1)")

    # 5. Simulation
    print("\n5. Testing Simulation...")
    sim_data = {
        "base_data": student.model_dump(),
        "modifications": {"academic.cgpa": 9.9}
    }
    response = requests.post(f"{BASE_URL}/simulate", json=sim_data, headers=headers)
    if response.status_code == 200:
        print(f"✓ Simulation successful! {response.json()['impact_summary']}")
    else:
        print(f"✗ Simulation failed: {response.status_code}")

    print("\n" + "="*60)
    print("PHASE 2 TESTING COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    test_system()
