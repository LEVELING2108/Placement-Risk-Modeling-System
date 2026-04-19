"""
Salary estimation model using regression techniques
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score
import joblib
import os
from app.core.config import settings


class SalaryPredictionModel:
    """
    Ensemble regression model for predicting starting salary
    Combines multiple regressors for robust predictions
    """
    
    def __init__(self):
        self.models = {
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.05,
                min_samples_split=10,
                min_samples_leaf=5,
                subsample=0.8,
                random_state=42
            ),
            'random_forest': RandomForestRegressor(
                n_estimators=300,
                max_depth=12,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42,
                n_jobs=-1
            ),
            'ridge': Ridge(
                alpha=1.0,
                random_state=42
            )
        }
        
        self.model_weights = {
            'gradient_boosting': 0.5,
            'random_forest': 0.3,
            'ridge': 0.2
        }
        
        self.is_trained = False
        self.feature_names = []
        self.salary_range = (settings.MIN_SALARY, settings.MAX_SALARY)
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, float]:
        """
        Train salary prediction models
        
        Args:
            X_train: Training features
            y_train: Actual salary values
            
        Returns:
            Dictionary of evaluation metrics
        """
        self.feature_names = X_train.columns.tolist()
        metrics = {}
        
        for name, model in self.models.items():
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate with cross-validation
            cv_scores = cross_val_score(
                model, X_train, y_train, cv=5, scoring='r2'
            )
            
            # Get predictions
            y_pred = model.predict(X_train)
            
            # Calculate metrics
            metrics[name] = {
                'mse': mean_squared_error(y_train, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_train, y_pred)),
                'mae': mean_absolute_error(y_train, y_pred),
                'r2': r2_score(y_train, y_pred),
                'cv_r2_mean': cv_scores.mean(),
                'cv_r2_std': cv_scores.std()
            }
        
        self.is_trained = True
        return metrics
    
    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Predict salary with confidence intervals
        
        Args:
            X: Input features
            
        Returns:
            Dictionary with salary predictions including range
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Get predictions from all models
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.predict(X)
        
        # Weighted average prediction
        weighted_pred = np.zeros(X.shape[0])
        for name, pred in predictions.items():
            weighted_pred += self.model_weights[name] * pred
        
        # Calculate prediction spread for confidence intervals
        pred_array = np.array(list(predictions.values()))
        pred_std = np.std(pred_array, axis=0)
        
        # Apply salary bounds
        weighted_pred = np.clip(weighted_pred, self.salary_range[0], self.salary_range[1])
        
        # Confidence intervals (±1.96 * std for 95% CI)
        ci_lower = np.clip(
            weighted_pred - 1.96 * pred_std,
            self.salary_range[0],
            self.salary_range[1]
        )
        ci_upper = np.clip(
            weighted_pred + 1.96 * pred_std,
            self.salary_range[0],
            self.salary_range[1]
        )
        
        return {
            'predicted_salary': weighted_pred,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'std': pred_std
        }
    
    def predict_range(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Predict salary range (min, max, average)
        
        Args:
            X: Input features
            
        Returns:
            Dictionary with salary range predictions
        """
        predictions = self.predict(X)
        
        # Create range (±10% of predicted value)
        avg = predictions['predicted_salary']
        range_pct = 0.10
        
        return {
            'expected_salary_min': avg * (1 - range_pct),
            'expected_salary_max': avg * (1 + range_pct),
            'expected_salary_avg': avg,
            'confidence_interval_lower': predictions['ci_lower'],
            'confidence_interval_upper': predictions['ci_upper']
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get aggregated feature importance across all models
        
        Returns:
            Dictionary of feature names and importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        importance_dict = {}
        
        for name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                importance_dict[name] = model.feature_importances_
            elif hasattr(model, 'coef_'):
                # For ridge regression, use absolute coefficient values
                importance_dict[name] = np.abs(model.coef_)
        
        # Average importance across models
        avg_importance = np.zeros(len(self.feature_names))
        count = 0
        
        for imp in importance_dict.values():
            if len(imp) == len(self.feature_names):
                avg_importance += imp
                count += 1
        
        if count > 0:
            avg_importance /= count
        
        return dict(zip(self.feature_names, avg_importance))
    
    def save_models(self, filepath: str):
        """Save trained models to disk"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            'models': self.models,
            'model_weights': self.model_weights,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'salary_range': self.salary_range
        }, filepath)
    
    def load_models(self, filepath: str):
        """Load trained models from disk"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        data = joblib.load(filepath)
        self.models = data['models']
        self.model_weights = data['model_weights']
        self.feature_names = data['feature_names']
        self.is_trained = data['is_trained']
        self.salary_range = data['salary_range']
