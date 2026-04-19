"""
Main prediction service that orchestrates all components
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import os

from app.services.preprocessing import DataPreprocessor
from app.services.feature_engineering import FeatureEngineer
from app.models.placement_model import PlacementPredictionModel
from app.models.salary_model import SalaryPredictionModel
from app.services.risk_scoring import RiskScoringSystem
from app.services.recommendation import RecommendationEngine
from app.services.market_data import MarketDataService
from app.schemas.prediction import (
    StudentPredictionRequest,
    StudentPredictionResponse,
    PlacementPrediction,
    SalaryPrediction,
    RiskAssessment,
    Recommendation,
    StudentAcademicData,
    InstituteData,
    LaborMarketData
)
from app.core.config import settings


class PredictionService:
    """
    Main service that orchestrates the complete prediction pipeline
    """
    
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.placement_model = PlacementPredictionModel()
        self.salary_model = SalaryPredictionModel()
        self.risk_scoring = RiskScoringSystem()
        self.recommendation_engine = RecommendationEngine()
        self.market_data = MarketDataService()
        
        self.models_loaded = False
        # Try to load models on initialization
        self.load_models()
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            if os.path.exists(settings.PLACEMENT_MODEL_PATH):
                self.placement_model.load_models(settings.PLACEMENT_MODEL_PATH)
            
            if os.path.exists(settings.SALARY_MODEL_PATH):
                self.salary_model.load_models(settings.SALARY_MODEL_PATH)
            
            self.models_loaded = True
        except Exception as e:
            print(f"Warning: Could not load models: {e}")
            print("Models will need to be trained before use.")
    
    def predict_single(self, request: StudentPredictionRequest) -> StudentPredictionResponse:
        """
        Generate complete prediction for a single student
        """
        # Step 0: Enrich with Market Data (Phase 3)
        sector = request.academic.course_type.value
        market_stats = self.market_data.get_sector_demand(sector)
        
        # Merge market stats into request dict for model consumption
        data = request.model_dump()
        if market_stats.get("live_data"):
            data["labor_market"]["field_job_demand_score"] = market_stats["field_job_demand_score"]
            data["labor_market"]["sector_hiring_growth"] = market_stats["sector_hiring_growth"]
        
        # Step 1: Preprocess data
        df_processed = self.preprocessor.preprocess_student_data(data)
        
        # Step 2: Feature engineering
        df_engineered = self.feature_engineer.engineer_features(df_processed)
        
        # Step 3: Get placement probabilities
        placement_probs = self.placement_model.predict(df_engineered)
        
        # Step 4: Predict timeline
        timeline = self.placement_model.predict_timeline(placement_probs)
        timeline_str = self._format_timeline(timeline[0])
        
        # Step 5: Predict salary
        salary_pred = self.salary_model.predict_range(df_engineered)
        
        # Step 6: Calculate risk score
        risk_score, risk_level, risk_factors = self.risk_scoring.calculate_risk_score(
            df_engineered, placement_probs, salary_pred
        )
        
        # Step 7: Generate advanced AI recommendations (Phase 3)
        ai_recommendations = self.recommendation_engine.generate_advanced_recommendations(
            data, 
            {"risk_level": risk_level, "placement_risk_score": risk_score, "risk_factors": risk_factors},
            placement_probs,
            salary_pred
        )
        
        # Get recruiter matches
        recruiter_matches = self.recommendation_engine.get_recruiter_matches(sector)
        
        # Step 8: Get explainability data (SHAP values)
        try:
            shap_values = self.placement_model.get_shap_explanations(df_engineered)
            explainability_scores = {
                k: float(v) for k, v in 
                sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:15]
            }
        except:
            explainability_scores = {}
        
        # Build response
        placement_prediction = PlacementPrediction(
            probability_3_months=float(placement_probs['3m'][0]),
            probability_6_months=float(placement_probs['6m'][0]),
            probability_12_months=float(placement_probs['12m'][0]),
            predicted_timeline=timeline_str
        )
        
        salary_prediction = SalaryPrediction(
            expected_salary_min=float(salary_pred['expected_salary_min'][0]),
            expected_salary_max=float(salary_pred['expected_salary_max'][0]),
            expected_salary_avg=float(salary_pred['expected_salary_avg'][0]),
            confidence_interval_lower=float(salary_pred['confidence_interval_lower'][0]),
            confidence_interval_upper=float(salary_pred['confidence_interval_upper'][0])
        )
        
        risk_assessment = RiskAssessment(
            placement_risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors
        )
        
        # Map AI recommendations to response schema
        recommendations = Recommendation(
            summary=ai_recommendations.get("summary", ""),
            next_best_actions=ai_recommendations.get("next_best_actions", []),
            recruiter_matches=recruiter_matches[:5]
        )
        
        response = StudentPredictionResponse(
            student_id=request.student_id,
            timestamp=datetime.now(),
            placement_prediction=placement_prediction,
            salary_prediction=salary_prediction,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            model_version=settings.APP_VERSION,
            explainability_scores=explainability_scores
        )
        
        return response
    
    def predict_batch(self, requests: List[StudentPredictionRequest]) -> List[StudentPredictionResponse]:
        results = []
        for request in requests:
            try:
                result = self.predict_single(request)
                results.append(result)
            except Exception as e:
                print(f"Error predicting for student {request.student_id}: {e}")
        return results

    def simulate(self, base_request: StudentPredictionRequest, modifications: Dict[str, any]) -> StudentPredictionResponse:
        request_dict = base_request.model_dump()
        for key, value in modifications.items():
            self._set_nested_value(request_dict, key, value)
            
        from app.schemas.prediction import StudentPredictionRequest as SPR
        new_request = SPR(**request_dict)
        return self.predict_single(new_request)

    def _set_nested_value(self, d, key, value):
        parts = key.split('.')
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value

    def _format_timeline(self, months: int) -> str:
        if months <= 3: return "Placed within 3 months"
        elif months <= 6: return "Placed within 6 months"
        elif months <= 12: return "Placed within 12 months"
        else: return "High risk of delayed placement"
