"""
Training script for the placement-risk models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
import json
from datetime import datetime

from app.services.data_generator import SampleDataGenerator
from app.services.preprocessing import DataPreprocessor
from app.services.feature_engineering import FeatureEngineer
from app.models.placement_model import PlacementPredictionModel
from app.models.salary_model import SalaryPredictionModel
from app.core.config import settings


class ModelTrainer:
    """
    Orchestrates the complete model training pipeline
    """
    
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.placement_model = PlacementPredictionModel()
        self.salary_model = SalaryPredictionModel()
    
    def generate_training_data(
        self, 
        n_samples: int = 2000,
        save_path: str = 'data/training_data.csv'
    ) -> pd.DataFrame:
        """
        Generate synthetic training data
        
        Args:
            n_samples: Number of samples to generate
            save_path: Path to save the data
            
        Returns:
            DataFrame with training data
        """
        print(f"Generating {n_samples} training samples...")
        
        generator = SampleDataGenerator(seed=42)
        df = generator.generate_dataset(n_students=n_samples, include_outcomes=True)
        
        # Save to disk
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"Training data saved to {save_path}")
        
        return df
    
    def prepare_features(
        self, 
        df: pd.DataFrame
    ) -> tuple:
        """
        Prepare features and targets from raw data
        
        Args:
            df: Raw training data DataFrame
            
        Returns:
            Tuple of (X, y_3m, y_6m, y_12m, y_salary)
        """
        print("Preparing features...")
        
        # Convert DataFrame to list of dictionaries for preprocessing
        records = df.to_dict('records')
        
        # Process each record
        processed_records = []
        for record in records:
            # Structure the data properly for preprocessing
            structured_data = {
                'academic': {
                    'course_type': record.get('course_type'),
                    'current_year': record.get('current_year'),
                    'semester': record.get('semester'),
                    'cgpa': record.get('cgpa'),
                    'academic_consistency': record.get('academic_consistency'),
                    'internship_count': record.get('internship_count', 0),
                    'total_internship_duration_months': record.get('total_internship_duration_months', 0),
                    'internship_employer_type': record.get('internship_employer_type'),
                    'internship_performance_score': record.get('internship_performance_score'),
                    'skill_certifications_count': record.get('skill_certifications_count', 0),
                    'relevant_coursework_count': record.get('relevant_coursework_count', 0)
                },
                'institute': {
                    'institute_tier': record.get('institute_tier'),
                    'historic_placement_rate_3m': record.get('historic_placement_rate_3m'),
                    'historic_placement_rate_6m': record.get('historic_placement_rate_6m'),
                    'historic_placement_rate_12m': record.get('historic_placement_rate_12m'),
                    'historic_avg_salary': record.get('historic_avg_salary'),
                    'placement_cell_activity_level': record.get('placement_cell_activity_level'),
                    'recruiter_participation_score': record.get('recruiter_participation_score')
                },
                'labor_market': {
                    'field_job_demand_score': record.get('field_job_demand_score'),
                    'region_job_density': record.get('region_job_density'),
                    'sector_hiring_trend': record.get('sector_hiring_trend'),
                    'sector_hiring_growth': record.get('sector_hiring_growth'),
                    'macroeconomic_condition_score': record.get('macroeconomic_condition_score')
                },
                'real_time_signals': {
                    'job_portal_applications_count': record.get('job_portal_applications_count', 0),
                    'interview_pipeline_stage': record.get('interview_pipeline_stage'),
                    'resume_updates_count': record.get('resume_updates_count', 0),
                    'skill_up_events_count': record.get('skill_up_events_count', 0),
                    'institute_placement_progress': record.get('institute_placement_progress')
                }
            }
            
            # Preprocess
            processed = self.preprocessor.preprocess_student_data(structured_data)
            processed_records.append(processed)
        
        # Combine all processed records
        df_processed = pd.concat(processed_records, ignore_index=True)
        
        # Feature engineering
        df_engineered = self.feature_engineer.engineer_features(df_processed)
        
        # Extract targets
        y_3m = df['placed_3m']
        y_6m = df['placed_6m']
        y_12m = df['placed_12m']
        y_salary = df['actual_salary']
        
        # Only include salary for placed students
        y_salary = y_salary.where(y_salary > 0).dropna()
        
        print(f"Feature engineering complete. {df_engineered.shape[1]} features created.")
        print(f"Features: {df_engineered.columns.tolist()}")
        
        return df_engineered, y_3m, y_6m, y_12m, y_salary
    
    def train_models(
        self,
        X: pd.DataFrame,
        y_3m: pd.Series,
        y_6m: pd.Series,
        y_12m: pd.Series,
        X_salary: pd.DataFrame,
        y_salary: pd.Series
    ) -> dict:
        """
        Train placement and salary models
        
        Args:
            X: Features
            y_3m, y_6m, y_12m: Binary placement targets
            y_salary: Salary target
            
        Returns:
            Dictionary of training metrics
        """
        print("\n" + "="*60)
        print("TRAINING PLACEMENT MODELS")
        print("="*60)
        
        # Train placement models
        placement_metrics = self.placement_model.train(X, y_3m, y_6m, y_12m)
        
        # Print metrics
        for timeline, metrics in placement_metrics.items():
            print(f"\n{timeline} Placement:")
            for model_name, metric_values in metrics.items():
                print(f"  {model_name}:")
                print(f"    Accuracy: {metric_values['accuracy']:.3f}")
                print(f"    F1 Score: {metric_values['f1']:.3f}")
                print(f"    ROC-AUC: {metric_values['roc_auc']:.3f}")
        
        print("\n" + "="*60)
        print("TRAINING SALARY MODEL")
        print("="*60)
        
        # Train salary model
        salary_metrics = self.salary_model.train(X_salary, y_salary)
        
        # Print metrics
        for model_name, metrics in salary_metrics.items():
            print(f"\n{model_name}:")
            print(f"    RMSE: {metrics['rmse']:,.2f}")
            print(f"    MAE: {metrics['mae']:,.2f}")
            print(f"    R² Score: {metrics['r2']:.3f}")
        
        all_metrics = {
            'placement': placement_metrics,
            'salary': salary_metrics
        }
        
        return all_metrics
    
    def save_models(
        self,
        placement_path: str = None,
        salary_path: str = None
    ):
        """
        Save trained models to disk
        
        Args:
            placement_path: Path to save placement model
            salary_path: Path to save salary model
        """
        if placement_path is None:
            placement_path = settings.PLACEMENT_MODEL_PATH
        
        if salary_path is None:
            salary_path = settings.SALARY_MODEL_PATH
        
        print(f"\nSaving placement model to {placement_path}...")
        self.placement_model.save_models(placement_path)
        
        print(f"Saving salary model to {salary_path}...")
        self.salary_model.save_models(salary_path)
        
        print("Models saved successfully!")
    
    def run_complete_training(
        self,
        n_samples: int = 2000,
        test_size: float = 0.2,
        save_data: bool = True,
        save_models_flag: bool = True
    ) -> dict:
        """
        Run complete training pipeline
        
        Args:
            n_samples: Number of training samples
            test_size: Proportion for testing
            save_data: Whether to save training data
            save_models_flag: Whether to save models
            
        Returns:
            Training metrics
        """
        print("="*60)
        print("PLACEMENT-RISK MODEL TRAINING")
        print("="*60)
        
        # Step 1: Generate data
        df = self.generate_training_data(
            n_samples=n_samples,
            save_path='data/training_data.csv' if save_data else None
        )
        
        # Step 2: Prepare features
        X, y_3m, y_6m, y_12m, y_salary = self.prepare_features(df)
        
        # Step 3: Train-test split (for evaluation)
        X_train, X_test, y_3m_train, y_3m_test, y_6m_train, y_6m_test, y_12m_train, y_12m_test = train_test_split(
            X, y_3m, y_6m, y_12m, test_size=test_size, random_state=42
        )
        
        # Align salary data with training set
        y_salary_train = y_salary.reindex(X_train.index).dropna()
        X_salary_train = X_train.loc[y_salary_train.index]
        y_salary_train = y_salary_train[y_salary_train > 0]
        X_salary_train = X_train.loc[y_salary_train.index]
        
        print(f"\nTraining set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        print(f"Salary training set: {X_salary_train.shape[0]} samples")
        
        # Step 4: Train models
        metrics = self.train_models(X_train, y_3m_train, y_6m_train, y_12m_train, X_salary_train, y_salary_train)
        
        # Step 5: Save models
        if save_models_flag:
            self.save_models()
        
        # Step 6: Save metrics
        if save_data:
            os.makedirs('data', exist_ok=True)
            with open('data/training_metrics.json', 'w') as f:
                # Convert numpy types to Python types for JSON serialization
                json_metrics = self._convert_metrics(metrics)
                json.dump(json_metrics, f, indent=2)
            print(f"\nTraining metrics saved to data/training_metrics.json")
        
        # Save metadata to registry
        registry_path = "models/registry.json"
        os.makedirs(os.path.dirname(registry_path), exist_ok=True)
        registry_entry = {
            "version": settings.APP_VERSION,
            "trained_at": datetime.now().isoformat(),
            "metrics": self._convert_metrics(metrics),
            "feature_count": len(X.columns)
        }
        with open(registry_path, 'w') as f:
            json.dump(registry_entry, f, indent=4)

        print(f"Model registry updated at {registry_path}")

        print("\n" + "="*60)
        print("TRAINING COMPLETE!")
        print("="*60)
        return metrics
    
    def _convert_metrics(self, metrics: dict) -> dict:
        """Convert numpy types to Python types for JSON serialization"""
        converted = {}
        for key, value in metrics.items():
            if isinstance(value, dict):
                converted[key] = self._convert_metrics(value)
            elif hasattr(value, 'item'):
                converted[key] = value.item()
            else:
                converted[key] = value
        return converted


if __name__ == "__main__":
    # Run training
    trainer = ModelTrainer()
    
    metrics = trainer.run_complete_training(
        n_samples=2000,
        test_size=0.2,
        save_data=True,
        save_models_flag=True
    )
