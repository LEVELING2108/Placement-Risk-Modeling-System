"""
Feature engineering module for enhanced model performance
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


class FeatureEngineer:
    """Advanced feature engineering for placement prediction"""
    
    def __init__(self):
        self.feature_names = []
        self.selected_features = []
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply feature engineering transformations
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        # Interaction features
        df = self._create_interaction_features(df)
        
        # Polynomial features (selective)
        df = self._create_polynomial_features(df)
        
        # Binning features
        df = self._create_binned_features(df)
        
        # Time-based features
        df = self._create_temporal_features(df)
        
        # Ratio features
        df = self._create_ratio_features(df)
        
        # Store feature names
        self.feature_names = df.columns.tolist()
        
        return df
    
    def _create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features between key variables"""
        
        # Academic * Institute interaction
        if 'academic_strength' in df.columns and 'institute_placement_strength' in df.columns:
            df['academic_institute_interaction'] = (
                df['academic_strength'] * df['institute_placement_strength']
            )
        
        # Internship * Market interaction
        if 'internship_quality_score' in df.columns and 'market_opportunity_score' in df.columns:
            df['internship_market_interaction'] = (
                df['internship_quality_score'] * df['market_opportunity_score']
            )
        
        # Engagement * Market interaction
        if 'student_engagement_score' in df.columns and 'market_opportunity_score' in df.columns:
            df['engagement_market_interaction'] = (
                df['student_engagement_score'] * df['market_opportunity_score']
            )
        
        # CGPA * Internship interaction
        if 'cgpa' in df.columns and 'internship_quality_score' in df.columns:
            df['cgpa_internship_interaction'] = (
                (df['cgpa'] / 10.0) * df['internship_quality_score']
            )
        
        return df
    
    def _create_polynomial_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create selective polynomial features"""
        
        # Squared terms for important features
        important_features = [
            'cgpa',
            'internship_quality_score',
            'academic_strength',
            'market_opportunity_score'
        ]
        
        for feature in important_features:
            if feature in df.columns:
                df[f'{feature}_squared'] = df[feature] ** 2
        
        return df
    
    def _create_binned_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create binned features for non-linear relationships"""
        
        # CGPA bins
        if 'cgpa' in df.columns:
            df['cgpa_category'] = pd.cut(
                df['cgpa'],
                bins=[0, 5, 6, 7, 8, 9, 10],
                labels=[0, 1, 2, 3, 4, 5],
                include_lowest=True
            ).astype(float)
        
        # Internship count bins
        if 'internship_count' in df.columns:
            df['internship_level'] = pd.cut(
                df['internship_count'],
                bins=[-1, 0, 1, 2, 5, 20],
                labels=[0, 1, 2, 3, 4],
                include_lowest=True
            ).astype(float)
        
        return df
    
    def _create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        
        # Year of study progress
        if all(col in df.columns for col in ['current_year', 'semester']):
            df['study_progress'] = df['semester'] / (df['current_year'] * 2)
        
        # Expected graduation proximity (assuming 4-year program)
        if 'current_year' in df.columns:
            df['years_to_graduation'] = 4 - df['current_year']
            df['is_final_year'] = (df['current_year'] >= 4).astype(int)
        
        # Experience intensity (duration per internship)
        if all(col in df.columns for col in ['internship_count', 'total_internship_duration_months']):
            df['avg_internship_duration'] = np.where(
                df['internship_count'] > 0,
                df['total_internship_duration_months'] / df['internship_count'],
                0
            )
            # Log transformation to reduce skewness of duration
            df['log_total_internship_duration'] = np.log1p(df['total_internship_duration_months'])

        return df

    def _create_ratio_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create ratio-based features"""
        
        # Certification to coursework ratio
        if all(col in df.columns for col in [
            'skill_certifications_count', 
            'relevant_coursework_count'
        ]):
            # Avoid division by zero
            df['certification_coursework_ratio'] = (
                df['skill_certifications_count'] / 
                (df['relevant_coursework_count'] + 1)
            )
        
        # Application to interview conversion
        if all(col in df.columns for col in [
            'job_portal_applications_count',
            'interview_pipeline_stage'
        ]):
            df['application_interview_ratio'] = np.where(
                df['job_portal_applications_count'] > 0,
                df['interview_pipeline_stage'] / 
                (df['job_portal_applications_count'] / 10),
                0
            )
        
        # Academic to market alignment
        if all(col in df.columns for col in [
            'academic_strength',
            'market_opportunity_score'
        ]):
            df['academic_market_alignment'] = (
                df['academic_strength'] * df['market_opportunity_score']
            )

        # CGPA to Institute Tier ratio (relative academic performance within tier)
        if all(col in df.columns for col in ['cgpa', 'institute_tier_encoded']):
             df['cgpa_tier_ratio'] = df['cgpa'] / (df['institute_tier_encoded'] + 1)
        
        return df
    
    def get_feature_importance_ranking(self, importance_scores: Dict[str, float]) -> List[Tuple[str, float]]:
        """
        Rank features by importance
        
        Args:
            importance_scores: Dictionary of feature names and their importance scores
            
        Returns:
            List of (feature_name, importance) tuples sorted by importance
        """
        ranked = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        return ranked
    
    def select_top_features(self, importance_scores: Dict[str, float], top_n: int = 15) -> List[str]:
        """
        Select top N most important features
        
        Args:
            importance_scores: Dictionary of feature names and their importance scores
            top_n: Number of top features to select
            
        Returns:
            List of top feature names
        """
        ranked = self.get_feature_importance_ranking(importance_scores)
        self.selected_features = [feature for feature, _ in ranked[:top_n]]
        return self.selected_features
