"""
Model evaluation and validation metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, mean_squared_error,
    mean_absolute_error, r2_score, classification_report
)
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from app.core.config import settings


class ModelEvaluator:
    """
    Comprehensive model evaluation and validation
    """
    
    def __init__(self):
        self.metrics = {}
    
    def evaluate_placement_model(
        self,
        y_true_3m: pd.Series,
        y_pred_3m: np.ndarray,
        y_prob_3m: np.ndarray,
        y_true_6m: pd.Series,
        y_pred_6m: np.ndarray,
        y_prob_6m: np.ndarray,
        y_true_12m: pd.Series,
        y_pred_12m: np.ndarray,
        y_prob_12m: np.ndarray
    ) -> Dict:
        """
        Evaluate placement prediction models
        
        Args:
            y_true_*: Ground truth labels
            y_pred_*: Predicted labels
            y_prob_*: Prediction probabilities
            
        Returns:
            Dictionary of evaluation metrics
        """
        evaluation = {}
        
        for timeline, y_true, y_pred, y_prob in [
            ('3m', y_true_3m, y_pred_3m, y_prob_3m),
            ('6m', y_true_6m, y_pred_6m, y_prob_6m),
            ('12m', y_true_12m, y_pred_12m, y_prob_12m)
        ]:
            metrics = {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, zero_division=0),
                'recall': recall_score(y_true, y_pred, zero_division=0),
                'f1': f1_score(y_true, y_pred, zero_division=0),
                'roc_auc': roc_auc_score(y_true, y_prob),
                'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
            }
            
            evaluation[timeline] = metrics
        
        return evaluation
    
    def evaluate_salary_model(
        self,
        y_true: pd.Series,
        y_pred: np.ndarray
    ) -> Dict:
        """
        Evaluate salary prediction model
        
        Args:
            y_true: Actual salaries
            y_pred: Predicted salaries
            
        Returns:
            Dictionary of evaluation metrics
        """
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        }
    
    def evaluate_risk_scoring(
        self,
        predicted_risk_scores: np.ndarray,
        actual_risk_labels: pd.Series
    ) -> Dict:
        """
        Evaluate risk scoring system
        
        Args:
            predicted_risk_scores: Predicted risk scores (0-1)
            actual_risk_labels: Actual risk labels (Low/Medium/High)
            
        Returns:
            Dictionary of evaluation metrics
        """
        # Convert scores to labels
        predicted_labels = []
        for score in predicted_risk_scores:
            if score >= settings.HIGH_RISK_THRESHOLD:
                predicted_labels.append('High')
            elif score >= settings.MEDIUM_RISK_THRESHOLD:
                predicted_labels.append('Medium')
            else:
                predicted_labels.append('Low')
        
        # Calculate metrics
        accuracy = accuracy_score(actual_risk_labels, predicted_labels)
        report = classification_report(
            actual_risk_labels, 
            predicted_labels,
            output_dict=True,
            zero_division=0
        )
        
        return {
            'accuracy': accuracy,
            'classification_report': report
        }
    
    def generate_evaluation_report(
        self,
        placement_eval: Dict,
        salary_eval: Dict,
        risk_eval: Dict = None
    ) -> str:
        """
        Generate human-readable evaluation report
        
        Args:
            placement_eval: Placement model evaluation
            salary_eval: Salary model evaluation
            risk_eval: Risk scoring evaluation (optional)
            
        Returns:
            Report string
        """
        report = "="*60 + "\n"
        report += "MODEL EVALUATION REPORT\n"
        report += "="*60 + "\n\n"
        
        # Placement metrics
        report += "PLACEMENT PREDICTION METRICS:\n"
        report += "-"*60 + "\n"
        for timeline, metrics in placement_eval.items():
            report += f"\n{timeline} Placement:\n"
            report += f"  Accuracy:  {metrics['accuracy']:.3f}\n"
            report += f"  Precision: {metrics['precision']:.3f}\n"
            report += f"  Recall:    {metrics['recall']:.3f}\n"
            report += f"  F1 Score:  {metrics['f1']:.3f}\n"
            report += f"  ROC-AUC:   {metrics['roc_auc']:.3f}\n"
        
        # Salary metrics
        report += "\n\nSALARY PREDICTION METRICS:\n"
        report += "-"*60 + "\n"
        report += f"  RMSE:  ₹{salary_eval['rmse']:,.2f}\n"
        report += f"  MAE:   ₹{salary_eval['mae']:,.2f}\n"
        report += f"  R²:    {salary_eval['r2']:.3f}\n"
        report += f"  MAPE:  {salary_eval['mape']:.2f}%\n"
        
        # Risk scoring metrics
        if risk_eval:
            report += "\n\nRISK SCORING METRICS:\n"
            report += "-"*60 + "\n"
            report += f"  Accuracy: {risk_eval['accuracy']:.3f}\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report
    
    def plot_confusion_matrices(
        self,
        placement_eval: Dict,
        save_path: str = 'models/confusion_matrices.png'
    ):
        """
        Plot confusion matrices for placement predictions
        
        Args:
            placement_eval: Placement model evaluation
            save_path: Path to save the plot
        """
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for idx, (timeline, metrics) in enumerate(placement_eval.items()):
            cm = np.array(metrics['confusion_matrix'])
            sns.heatmap(
                cm, 
                annot=True, 
                fmt='d', 
                cmap='Blues',
                ax=axes[idx],
                xticklabels=['Not Placed', 'Placed'],
                yticklabels=['Not Placed', 'Placed']
            )
            axes[idx].set_title(f'{timeline} Placement')
            axes[idx].set_ylabel('Actual')
            axes[idx].set_xlabel('Predicted')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def validate_model_robustness(
        self,
        model,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Dict:
        """
        Validate model robustness with different metrics
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test targets
            
        Returns:
            Dictionary of robustness metrics
        """
        predictions = model.predict(X_test)
        
        # Check prediction distribution
        if isinstance(predictions, dict):
            probs = predictions.get('3m', predictions.get('probability_3_months', None))
            if probs is not None:
                robustness = {
                    'mean_probability': float(np.mean(probs)),
                    'std_probability': float(np.std(probs)),
                    'min_probability': float(np.min(probs)),
                    'max_probability': float(np.max(probs)),
                    'percentile_25': float(np.percentile(probs, 25)),
                    'percentile_75': float(np.percentile(probs, 75))
                }
            else:
                robustness = {}
        else:
            robustness = {}
        
        return robustness
