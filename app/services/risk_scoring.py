"""
Risk scoring and classification system
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from app.core.config import settings
from app.schemas.prediction import RiskLevel


class RiskScoringSystem:
    """
    Calculates placement risk scores and identifies risk factors
    Provides explainable risk assessments for lenders
    """
    
    def __init__(self):
        self.risk_factors_config = {
            'academic_risk': {
                'weight': 0.20,
                'factors': ['cgpa', 'academic_consistency']
            },
            'internship_risk': {
                'weight': 0.25,
                'factors': [
                    'internship_count',
                    'total_internship_duration_months',
                    'internship_performance_score'
                ]
            },
            'institute_risk': {
                'weight': 0.20,
                'factors': [
                    'institute_tier_encoded',
                    'historic_placement_rate_3m',
                    'recruiter_participation_score'
                ]
            },
            'market_risk': {
                'weight': 0.20,
                'factors': [
                    'field_job_demand_score',
                    'region_job_density',
                    'sector_hiring_growth',
                    'macroeconomic_condition_score'
                ]
            },
            'engagement_risk': {
                'weight': 0.15,
                'factors': [
                    'job_portal_applications_count',
                    'interview_pipeline_stage',
                    'skill_up_events_count'
                ]
            }
        }
    
    def calculate_risk_score(
        self, 
        features: pd.DataFrame,
        placement_probs: Dict[str, np.ndarray],
        salary_pred: Optional[Dict[str, np.ndarray]] = None
    ) -> Tuple[float, RiskLevel, List[str]]:
        """
        Calculate comprehensive risk score
        
        Args:
            features: Preprocessed feature DataFrame
            placement_probs: Placement probabilities for 3/6/12 months
            salary_pred: Salary prediction (optional)
            
        Returns:
            Tuple of (risk_score, risk_level, risk_factors)
        """
        # Calculate sub-scores for each risk category
        sub_scores = {}
        
        # Academic risk
        sub_scores['academic_risk'] = self._calculate_academic_risk(features)
        
        # Internship risk
        sub_scores['internship_risk'] = self._calculate_internship_risk(features)
        
        # Institute risk
        sub_scores['institute_risk'] = self._calculate_institute_risk(features)
        
        # Market risk
        sub_scores['market_risk'] = self._calculate_market_risk(features)
        
        # Engagement risk
        sub_scores['engagement_risk'] = self._calculate_engagement_risk(features)
        
        # Placement probability risk (inverse)
        placement_risk = self._calculate_placement_probability_risk(placement_probs)
        
        # Combine all risks
        weighted_risk = 0.0
        for category, config in self.risk_factors_config.items():
            weighted_risk += sub_scores[category] * config['weight']
        
        # Add placement probability risk (very important)
        weighted_risk += placement_risk * 0.30
        
        # Normalize to 0-1 range
        risk_score = np.clip(weighted_risk, 0, 1)
        
        # Ensure risk_score is a scalar for classification and return
        if hasattr(risk_score, "__len__"):
            risk_score_scalar = float(risk_score[0])
        else:
            risk_score_scalar = float(risk_score)
            
        # Classify risk level
        risk_level = self._classify_risk(risk_score_scalar)
        
        # Identify top risk factors
        risk_factors = self._identify_risk_factors(
            features, sub_scores, placement_probs
        )
        
        return risk_score_scalar, risk_level, risk_factors
    
    def _calculate_academic_risk(self, features: pd.DataFrame) -> np.ndarray:
        """Calculate academic-related risk"""
        risk = np.zeros(len(features))
        
        if 'cgpa' in features.columns:
            # Lower CGPA = higher risk
            cgpa_risk = 1 - (features['cgpa'] / 10.0)
            risk += cgpa_risk.values * 0.6
        
        if 'academic_consistency' in features.columns:
            # Lower consistency = higher risk
            consistency_risk = 1 - features['academic_consistency']
            risk += consistency_risk.values * 0.4
        
        return risk
    
    def _calculate_internship_risk(self, features: pd.DataFrame) -> np.ndarray:
        """Calculate internship-related risk"""
        risk = np.zeros(len(features))
        
        if 'internship_count' in features.columns:
            # No internships = high risk
            internship_count_risk = np.where(
                features['internship_count'] == 0, 1.0,
                np.where(features['internship_count'] == 1, 0.6, 0.2)
            )
            risk += internship_count_risk * 0.4
        
        if 'total_internship_duration_months' in features.columns:
            # Short duration = higher risk
            duration = features['total_internship_duration_months'].values
            duration_risk = np.clip(1 - (duration / 6.0), 0, 1)
            risk += duration_risk * 0.3
        
        if 'internship_performance_score' in features.columns:
            # Lower performance = higher risk
            perf_risk = 1 - features['internship_performance_score'].fillna(0.5)
            risk += perf_risk.values * 0.3
        
        return risk
    
    def _calculate_institute_risk(self, features: pd.DataFrame) -> np.ndarray:
        """Calculate institute-related risk"""
        risk = np.zeros(len(features))
        
        if 'institute_tier_encoded' in features.columns:
            # Higher tier number = higher risk
            tier_risk = features['institute_tier_encoded'].values / 2.0
            risk += tier_risk * 0.4
        
        if 'historic_placement_rate_3m' in features.columns:
            # Lower placement rate = higher risk
            placement_rate_risk = 1 - features['historic_placement_rate_3m'].values
            risk += placement_rate_risk * 0.35
        
        if 'recruiter_participation_score' in features.columns:
            # Lower participation = higher risk
            recruiter_risk = 1 - features['recruiter_participation_score'].values
            risk += recruiter_risk * 0.25
        
        return risk
    
    def _calculate_market_risk(self, features: pd.DataFrame) -> np.ndarray:
        """Calculate market-related risk"""
        risk = np.zeros(len(features))
        
        if 'field_job_demand_score' in features.columns:
            # Lower demand = higher risk
            demand_risk = 1 - features['field_job_demand_score'].values
            risk += demand_risk * 0.35
        
        if 'region_job_density' in features.columns:
            # Lower density = higher risk
            density_risk = 1 - features['region_job_density'].values
            risk += density_risk * 0.25
        
        if 'sector_hiring_growth' in features.columns:
            # Negative growth = higher risk
            growth = features['sector_hiring_growth'].values
            growth_risk = np.clip((1 - growth) / 2, 0, 1)
            risk += growth_risk * 0.2
        
        if 'macroeconomic_condition_score' in features.columns:
            # Worse conditions = higher risk
            macro_risk = 1 - features['macroeconomic_condition_score'].values
            risk += macro_risk * 0.2
        
        return risk
    
    def _calculate_engagement_risk(self, features: pd.DataFrame) -> np.ndarray:
        """Calculate engagement-related risk"""
        risk = np.zeros(len(features))
        
        if 'job_portal_applications_count' in features.columns:
            # Very low applications = higher risk
            apps = features['job_portal_applications_count'].values
            app_risk = np.where(
                apps < 5, 0.8,
                np.where(apps < 15, 0.4, 0.2)
            )
            risk += app_risk * 0.4
        
        if 'interview_pipeline_stage' in features.columns:
            # Lower stage = higher risk
            stage = features['interview_pipeline_stage'].fillna(0).values
            stage_risk = 1 - (stage / 5.0)
            risk += stage_risk * 0.4
        
        if 'skill_up_events_count' in features.columns:
            # Fewer skill-ups = higher risk
            skills = features['skill_up_events_count'].values
            skill_risk = np.clip(1 - (skills / 5.0), 0, 1)
            risk += skill_risk * 0.2
        
        return risk
    
    def _calculate_placement_probability_risk(
        self, 
        placement_probs: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """Calculate risk based on placement probabilities"""
        prob_3m = placement_probs['3m']
        prob_6m = placement_probs['6m']
        prob_12m = placement_probs['12m']
        
        # Weighted risk (lower probability = higher risk)
        risk = (
            (1 - prob_3m) * 0.5 +
            (1 - prob_6m) * 0.3 +
            (1 - prob_12m) * 0.2
        )
        
        return risk
    
    def _classify_risk(self, risk_score: float) -> RiskLevel:
        """Classify risk level based on score"""
        if risk_score >= settings.HIGH_RISK_THRESHOLD:
            return RiskLevel.HIGH
        elif risk_score >= settings.MEDIUM_RISK_THRESHOLD:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _identify_risk_factors(
        self,
        features: pd.DataFrame,
        sub_scores: Dict[str, np.ndarray],
        placement_probs: Dict[str, np.ndarray]
    ) -> List[str]:
        """Identify top risk factors for a student"""
        risk_factors = []
        
        # Check academic factors
        if 'cgpa' in features.columns and features['cgpa'].values[0] < 6.5:
            risk_factors.append("Low CGPA (<6.5)")
        
        if 'academic_consistency' in features.columns:
            if features['academic_consistency'].values[0] < 0.5:
                risk_factors.append("Poor academic consistency")
        
        # Check internship factors
        if 'internship_count' in features.columns:
            if features['internship_count'].values[0] == 0:
                risk_factors.append("No internship experience")
            elif features['internship_count'].values[0] < 2:
                risk_factors.append("Limited internship exposure")
        
        if 'total_internship_duration_months' in features.columns:
            if features['total_internship_duration_months'].values[0] < 2:
                risk_factors.append("Short internship duration")
        
        # Check institute factors
        if 'institute_tier_encoded' in features.columns:
            if features['institute_tier_encoded'].values[0] >= 2:
                risk_factors.append("Tier-3 institute")
        
        if 'historic_placement_rate_3m' in features.columns:
            if features['historic_placement_rate_3m'].values[0] < 0.4:
                risk_factors.append("Weak institute placement record")
        
        # Check market factors
        if 'field_job_demand_score' in features.columns:
            if features['field_job_demand_score'].values[0] < 0.4:
                risk_factors.append("Low field-wise job demand")
        
        if 'region_job_density' in features.columns:
            if features['region_job_density'].values[0] < 0.3:
                risk_factors.append("Low regional job opportunities")
        
        if 'sector_hiring_growth' in features.columns:
            if features['sector_hiring_growth'].values[0] < 0:
                risk_factors.append("Declining sector hiring trends")
        
        # Check engagement factors
        if 'job_portal_applications_count' in features.columns:
            if features['job_portal_applications_count'].values[0] < 5:
                risk_factors.append("Low job application activity")
        
        if 'interview_pipeline_stage' in features.columns:
            stage = features['interview_pipeline_stage'].values[0]
            if pd.notna(stage) and stage < 2:
                risk_factors.append("Early interview pipeline stage")
        
        if 'skill_up_events_count' in features.columns:
            if features['skill_up_events_count'].values[0] < 2:
                risk_factors.append("Limited skill development activity")
        
        # Check placement probability
        if placement_probs['3m'][0] < 0.3:
            risk_factors.append("Low 3-month placement probability")
        
        if placement_probs['6m'][0] < 0.4:
            risk_factors.append("Low 6-month placement probability")
        
        return risk_factors if risk_factors else ["No significant risk factors identified"]
