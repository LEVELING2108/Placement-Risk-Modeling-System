import requests
import json
from app.services.data_generator import SampleDataGenerator

BASE_URL = "http://localhost:8000/api/v1"

def test_shap_data():
    # 1. Login
    login_data = {"username": "lender_a", "password": "password123"}
    token = requests.post(f"{BASE_URL}/auth/login", data=login_data).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Run Prediction
    generator = SampleDataGenerator(seed=42)
    student = generator.generate_single_student(student_id="SHAP_TEST")
    
    print("Requesting prediction...")
    response = requests.post(f"{BASE_URL}/predict", json=student.model_dump(), headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        shap_scores = data.get("explainability_scores")
        print(f"Explainability Scores received: {type(shap_scores)}")
        if shap_scores:
            print(f"Number of features: {len(shap_scores)}")
            # Print top 5
            top_5 = dict(list(shap_scores.items())[:5])
            print(f"Top 5 SHAP values: {top_5}")
        else:
            print("❌ explainability_scores is EMPTY or None")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_shap_data()
