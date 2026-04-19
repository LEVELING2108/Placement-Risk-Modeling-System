"""
Placement prediction models for 3/6/12 month timelines
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import cross_val_score
import joblib
import os
from app.core.config import settings


class PlacementPredictionModel:
    """
    Ensemble model for predicting placement timelines (3/6/12 months)
    Uses multiple classifiers for robust predictions
    """
    
    def __init__(self):
        # We need separate models for each timeline
        self.timelines = ['3m', '6m', '12m']
        self.models = {}
        
        for timeline in self.timelines:
            self.models[timeline] = {
                'gradient_boosting': GradientBoostingClassifier(
                    n_estimators=200,
                    max_depth=5,
                    learning_rate=0.1,
                    min_samples_split=10,
                    min_samples_leaf=5,
                    subsample=0.8,
                    random_state=42
                ),
                'random_forest': RandomForestClassifier(
                    n_estimators=200,
                    max_depth=10,
                    min_samples_split=10,
                    min_samples_leaf=5,
                    random_state=42,
                    n_jobs=-1
                ),
                'logistic_regression': LogisticRegression(
                    max_iter=1000,
                    C=1.0,
                    random_state=42
                )
            }
        
        self.model_weights = {
            'gradient_boosting': 0.5,
            'random_forest': 0.3,
            'logistic_regression': 0.2
        }
        
        self.is_trained = False
        self.feature_names = []
        self._explainer = None  # Cache for SHAP explainer
    
    def get_shap_explanations(self, X: pd.DataFrame) -> Dict[str, float]:
        """
        Get SHAP explanations for a single instance using the ensemble
        
        Args:
            X: Input features (single row)
            
        Returns:
            Dictionary of feature names and their SHAP contribution values
        """
        import shap
        
        if not self.is_trained:
            raise ValueError("Model must be trained first")
            
        # For simplicity and performance, we'll use the 6m Random Forest model 
        # as a proxy for the entire ensemble's behavior
        model = self.models['6m']['random_forest']
        
        if self._explainer is None:
            self._explainer = shap.TreeExplainer(model)
            
        shap_values = self._explainer.shap_values(X)
        
        # shap_values for classification is a list [neg_class_probs, pos_class_probs]
        # or just an array for regression. For RF classifier, it's a list.
        if isinstance(shap_values, list):
            # Index 1 is the positive class (placed)
            contributions = shap_values[1][0]
        else:
            contributions = shap_values[0]
            
        return dict(zip(self.feature_names, contributions))
    
    def train(
        self, 
        X_train: pd.DataFrame, 
        y_train_3m: pd.Series,
        y_train_6m: pd.Series,
        y_train_12m: pd.Series
    ) -> Dict[str, Dict[str, float]]:
        """
        Train all models for different time horizons
        
        Args:
            X_train: Training features
            y_train_3m: Binary labels for 3-month placement
            y_train_6m: Binary labels for 6-month placement
            y_train_12m: Binary labels for 12-month placement
            
        Returns:
            Dictionary of evaluation metrics for each model and timeline
        """
        self.feature_names = X_train.columns.tolist()
        metrics = {}
        
        # Train models for each timeline
        timeline_targets = {
            '3m': y_train_3m,
            '6m': y_train_6m,
            '12m': y_train_12m
        }
        
        for timeline, y_train in timeline_targets.items():
            metrics[timeline] = {}
            
            for name, model in self.models[timeline].items():
                # Train model
                model.fit(X_train, y_train)
                
                # Evaluate with cross-validation
                cv_scores = cross_val_score(
                    model, X_train, y_train, cv=5, scoring='roc_auc'
                )
                
                # Get predictions
                y_pred = model.predict(X_train)
                y_prob = model.predict_proba(X_train)[:, 1]
                
                # Calculate metrics
                metrics[timeline][name] = {
                    'accuracy': accuracy_score(y_train, y_pred),
                    'precision': precision_score(y_train, y_pred, zero_division=0),
                    'recall': recall_score(y_train, y_pred, zero_division=0),
                    'f1': f1_score(y_train, y_pred, zero_division=0),
                    'roc_auc': roc_auc_score(y_train, y_prob),
                    'cv_roc_auc_mean': cv_scores.mean(),
                    'cv_roc_auc_std': cv_scores.std()
                }
            
        self.is_trained = True
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Predict placement probabilities for all timelines
        
        Args:
            X: Input features
            
        Returns:
            Dictionary with probabilities for each timeline
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        probabilities = {}
        
        # Predict for each timeline
        for timeline in self.timelines:
            weighted_probs = np.zeros(X.shape[0])
            
            for name, model in self.models[timeline].items():
                probs = model.predict_proba(X)[:, 1]
                weighted_probs += self.model_weights[name] * probs
            
            probabilities[timeline] = weighted_probs
        
        return probabilities
    
    def predict_timeline(self, probabilities: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Determine predicted timeline based on probabilities and thresholds
        
        Args:
            probabilities: Dictionary of probabilities for each timeline
            
        Returns:
            Array of predicted timelines (3, 6, 12, or 24 for delayed)
        """
        prob_3m = probabilities['3m']
        prob_6m = probabilities['6m']
        prob_12m = probabilities['12m']
        
        predictions = np.full(len(prob_3m), 24)  # Default to delayed (24 months)
        
        # Apply thresholds
        predictions[prob_3m >= settings.PLACEMENT_3M_THRESHOLD] = 3
        predictions[
            (prob_6m >= settings.PLACEMENT_6M_THRESHOLD) & 
            (prob_3m < settings.PLACEMENT_3M_THRESHOLD)
        ] = 6
        predictions[
            (prob_12m >= settings.PLACEMENT_12M_THRESHOLD) & 
            (prob_6m < settings.PLACEMENT_6M_THRESHOLD) &
            (prob_3m < settings.PLACEMENT_3M_THRESHOLD)
        ] = 12
        
        return predictions
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get aggregated feature importance across all models
        
        Returns:
            Dictionary of feature names and importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        importance_list = []
        
        for timeline in self.timelines:
            for name, model in self.models[timeline].items():
                if hasattr(model, 'feature_importances_'):
                    importance_list.append(model.feature_importances_)
                elif hasattr(model, 'coef_'):
                    # For logistic regression, use absolute coefficient values
                    importance_list.append(np.abs(model.coef_[0]))
        
        # Average importance across all models and timelines
        avg_importance = np.zeros(len(self.feature_names))
        count = 0
        
        for imp in importance_list:
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
            'is_trained': self.is_trained
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
