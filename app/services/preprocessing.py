"""
Data preprocessing pipeline for the placement-risk modeling system
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from app.core.config import settings


class DataPreprocessor:
    """Preprocesses student data for model input"""
    
    def __init__(self):
        self.is_fitted = False
        
    def preprocess_student_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Preprocess raw student data into model-ready format
        
        Args:
            data: Dictionary containing student academic, institute, labor market, 
                  and real-time signal data
            
        Returns:
            DataFrame with preprocessed features
        """
        # Flatten the nested dictionary structure
        flat_data = self._flatten_data(data)
        
        # Convert to DataFrame
        df = pd.DataFrame([flat_data])
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Encode categorical variables
        df = self._encode_categoricals(df)
        
        # Create derived features
        df = self._create_derived_features(df)
        
        return df
    
    def _flatten_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested dictionary structure"""
        flat = {}
        
        # Extract academic data
        if 'academic' in data:
            academic = data['academic']
            flat['course_type'] = academic.get('course_type')
            flat['current_year'] = academic.get('current_year')
            flat['semester'] = academic.get('semester')
            flat['cgpa'] = academic.get('cgpa')
            flat['academic_consistency'] = academic.get('academic_consistency')
            flat['internship_count'] = academic.get('internship_count', 0)
            flat['total_internship_duration_months'] = academic.get(
                'total_internship_duration_months', 0
            )
            flat['internship_employer_type'] = academic.get('internship_employer_type')
            flat['internship_performance_score'] = academic.get(
                'internship_performance_score'
            )
            flat['skill_certifications_count'] = academic.get(
                'skill_certifications_count', 0
            )
            flat['relevant_coursework_count'] = academic.get(
                'relevant_coursework_count', 0
            )
        
        # Extract institute data
        if 'institute' in data:
            institute = data['institute']
            flat['institute_tier'] = institute.get('institute_tier')
            flat['historic_placement_rate_3m'] = institute.get(
                'historic_placement_rate_3m'
            )
            flat['historic_placement_rate_6m'] = institute.get(
                'historic_placement_rate_6m'
            )
            flat['historic_placement_rate_12m'] = institute.get(
                'historic_placement_rate_12m'
            )
            flat['historic_avg_salary'] = institute.get('historic_avg_salary')
            flat['placement_cell_activity_level'] = institute.get(
                'placement_cell_activity_level'
            )
            flat['recruiter_participation_score'] = institute.get(
                'recruiter_participation_score'
            )
        
        # Extract labor market data
        if 'labor_market' in data:
            labor_market = data['labor_market']
            flat['field_job_demand_score'] = labor_market.get('field_job_demand_score')
            flat['region_job_density'] = labor_market.get('region_job_density')
            flat['sector_hiring_trend'] = labor_market.get('sector_hiring_trend')
            flat['sector_hiring_growth'] = labor_market.get('sector_hiring_growth')
            flat['macroeconomic_condition_score'] = labor_market.get(
                'macroeconomic_condition_score'
            )
        
        # Extract real-time signals (optional)
        if 'real_time_signals' in data and data['real_time_signals']:
            signals = data['real_time_signals']
            flat['job_portal_applications_count'] = signals.get(
                'job_portal_applications_count', 0
            )
            flat['interview_pipeline_stage'] = signals.get('interview_pipeline_stage')
            flat['resume_updates_count'] = signals.get('resume_updates_count', 0)
            flat['skill_up_events_count'] = signals.get('skill_up_events_count', 0)
            flat['institute_placement_progress'] = signals.get(
                'institute_placement_progress'
            )
        else:
            # Set defaults for missing real-time signals
            flat['job_portal_applications_count'] = 0
            flat['interview_pipeline_stage'] = None
            flat['resume_updates_count'] = 0
            flat['skill_up_events_count'] = 0
            flat['institute_placement_progress'] = None
        
        return flat
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values and outliers with appropriate strategies"""
        # Known numeric columns that may have object dtype due to None values
        numeric_object_cols = [
            'internship_performance_score',
            'interview_pipeline_stage',
            'institute_placement_progress'
        ]
        
        for col in numeric_object_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                if df[col].isnull().any():
                    df[col] = df[col].fillna(0)
        
        # Fill remaining numeric missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                if 'score' in col.lower() or 'rate' in col.lower() or 'cgpa' in col.lower():
                    df[col] = df[col].fillna(0)
                else:
                    df[col] = df[col].fillna(df[col].median() if df[col].notna().any() else 0)
        
        # Clip outliers for key numeric features to ensure model stability
        if 'cgpa' in df.columns:
            df['cgpa'] = df['cgpa'].clip(0, 10)
        
        if 'internship_count' in df.columns:
            df['internship_count'] = df['internship_count'].clip(0, 10)
            
        if 'total_internship_duration_months' in df.columns:
            df['total_internship_duration_months'] = df['total_internship_duration_months'].clip(0, 24)

        # Fill categorical/object missing values
        object_cols = df.select_dtypes(include=['object', 'string']).columns
        for col in object_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna('Unknown')
        
        return df
    
    def _encode_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables"""
        # Encode course type
        if 'course_type' in df.columns:
            df['course_type_encoded'] = df['course_type'].map(
                settings.COURSE_ENCODINGS
            ).fillna(settings.COURSE_ENCODINGS['Other'])
            df.drop('course_type', axis=1, inplace=True)
        
        # Encode institute tier
        if 'institute_tier' in df.columns:
            df['institute_tier_encoded'] = df['institute_tier'].map(
                settings.INSTITUTE_TIER_ENCODINGS
            ).fillna(1)  # Default to Tier-2
            df.drop('institute_tier', axis=1, inplace=True)
        
        # Encode sector
        if 'sector_hiring_trend' in df.columns:
            df['sector_hiring_trend_encoded'] = df['sector_hiring_trend'].map(
                settings.SECTOR_ENCODINGS
            ).fillna(settings.SECTOR_ENCODINGS['Other'])
            df.drop('sector_hiring_trend', axis=1, inplace=True)
        
        # Encode internship employer type (simple encoding)
        if 'internship_employer_type' in df.columns:
            employer_mapping = {
                'MNC': 3,
                'Large Corporate': 2,
                'Mid-size': 2,
                'Startup': 1,
                'Government': 2,
                'NGO': 1,
                'Unknown': 0
            }
            df['internship_employer_type_encoded'] = df['internship_employer_type'].map(
                employer_mapping
            ).fillna(0)
            df.drop('internship_employer_type', axis=1, inplace=True)
        
        return df
    
    def _create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features for better predictions"""
        # Internship quality score
        if all(col in df.columns for col in [
            'internship_count', 
            'total_internship_duration_months',
            'internship_employer_type_encoded'
        ]):
            df['internship_quality_score'] = (
                df['internship_count'] * 0.3 +
                df['total_internship_duration_months'] * 0.3 +
                df['internship_employer_type_encoded'] * 0.4
            ) / 3.0
        
        # Academic strength composite
        if all(col in df.columns for col in ['cgpa', 'academic_consistency']):
            df['academic_strength'] = (
                df['cgpa'] / 10.0 * 0.6 +
                df['academic_consistency'] * 0.4
            )
        
        # Institute placement strength
        if all(col in df.columns for col in [
            'historic_placement_rate_3m',
            'historic_placement_rate_6m',
            'historic_placement_rate_12m',
            'recruiter_participation_score'
        ]):
            df['institute_placement_strength'] = (
                df['historic_placement_rate_3m'] * 0.4 +
                df['historic_placement_rate_6m'] * 0.3 +
                df['historic_placement_rate_12m'] * 0.15 +
                df['recruiter_participation_score'] * 0.15
            )
        
        # Market opportunity score
        if all(col in df.columns for col in [
            'field_job_demand_score',
            'region_job_density',
            'sector_hiring_growth',
            'macroeconomic_condition_score'
        ]):
            df['market_opportunity_score'] = (
                df['field_job_demand_score'] * 0.35 +
                df['region_job_density'] * 0.25 +
                ((df['sector_hiring_growth'] + 1) / 2) * 0.2 +
                df['macroeconomic_condition_score'] * 0.2
            )
        
        # Student engagement score (from real-time signals)
        if all(col in df.columns for col in [
            'job_portal_applications_count',
            'resume_updates_count',
            'skill_up_events_count'
        ]):
            # Normalize application count (cap at 50)
            df['normalized_applications'] = df['job_portal_applications_count'].clip(0, 50) / 50.0
            df['normalized_resumes'] = df['resume_updates_count'].clip(0, 10) / 10.0
            df['normalized_skills'] = df['skill_up_events_count'].clip(0, 10) / 10.0
            
            df['student_engagement_score'] = (
                df['normalized_applications'] * 0.4 +
                df['normalized_resumes'] * 0.3 +
                df['normalized_skills'] * 0.3
            )
            
            # Drop intermediate columns
            df.drop(['normalized_applications', 'normalized_resumes', 'normalized_skills'], 
                    axis=1, inplace=True)
        
        # Interview progress indicator
        if 'interview_pipeline_stage' in df.columns:
            df['interview_progress'] = df['interview_pipeline_stage'].fillna(0) / 5.0
        
        return df
