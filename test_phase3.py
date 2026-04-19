"""
Test script for Phase 3: External Data & AI Recommendations
"""

import os
import json
from app.services.market_data import MarketDataService
from app.services.recommendation import RecommendationEngine
from app.services.prediction_service import PredictionService
from app.schemas.prediction import StudentPredictionRequest
from app.services.data_generator import SampleDataGenerator

def test_market_data():
    print("\n--- Testing Market Data Service ---")
    service = MarketDataService()
    
    # Test with fallback (keys are likely missing in test env)
    stats = service.get_sector_demand("IT")
    print(f"Sector: IT, Demand: {stats['field_job_demand_score']}, Live: {stats['live_data']}")
    
    stats_mba = service.get_sector_demand("MBA")
    print(f"Sector: MBA, Demand: {stats_mba['field_job_demand_score']}, Live: {stats_mba['live_data']}")

def test_recommendation_ai():
    print("\n--- Testing Recommendation Engine ---")
    engine = RecommendationEngine()
    
    # Mock data
    student = {"academic": {"course_type": "Engineering", "cgpa": 8.5}}
    risk = {"risk_level": "Low", "placement_risk_score": 0.15, "risk_factors": []}
    probs = {"6m": [0.85]}
    salary = {"expected_salary_avg": [650000]}
    
    recs = engine.generate_advanced_recommendations(student, risk, probs, salary)
    print(f"Summary: {recs['summary']}")
    print(f"Is AI Generated: {recs['is_ai_generated']}")
    print(f"Actions: {len(recs['next_best_actions'])} items")

def test_full_prediction_flow():
    print("\n--- Testing Full Prediction Flow (Phase 3) ---")
    service = PredictionService()
    generator = SampleDataGenerator(seed=42)
    student_req = generator.generate_single_student(student_id="PHASE3_TEST")
    
    response = service.predict_single(student_req)
    print(f"Student: {response.student_id}")
    print(f"Risk: {response.risk_assessment.risk_level}")
    print(f"AI Summary: {response.recommendations.summary[:100]}...")

if __name__ == "__main__":
    test_market_data()
    test_recommendation_ai()
    try:
        test_full_prediction_flow()
    except Exception as e:
        print(f"Flow test failed (models might not be loaded): {e}")
