"""
AI-generated summary and recommendation engine using Gemini
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import os
import json
import re
from app.schemas.prediction import RiskLevel

class RecommendationEngine:
    """
    Generates AI-powered summaries and actionable recommendations
    for students based on their risk profile. Integrates with Gemini for 
    personalized roadmaps if an API key is available.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self._client = None
        
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")

        self.recommendation_templates = {
            'skill_up': [
                "Complete additional certifications in high-demand skills",
                "Enroll in industry-recognized online courses",
                "Focus on technical skills relevant to your field"
            ],
            'resume': [
                "Update resume with recent projects and achievements",
                "Add quantifiable accomplishments to resume"
            ],
            'internship': [
                "Apply for more internship opportunities",
                "Seek longer-duration internships"
            ]
        }
    
    def generate_summary(
        self,
        risk_level: RiskLevel,
        risk_factors: List[str],
        placement_probs: Dict[str, np.ndarray],
        salary_pred: Optional[Dict[str, np.ndarray]] = None,
        features: Optional[pd.DataFrame] = None
    ) -> str:
        """Fallback rule-based summary generator"""
        if risk_level == RiskLevel.HIGH:
            summary = "HIGH RISK: Significant placement challenges. "
        elif risk_level == RiskLevel.MEDIUM:
            summary = "MEDIUM RISK: Moderate placement prospects with room for improvement. "
        else:
            summary = "LOW RISK: Strong placement potential. "
        
        if risk_factors and risk_factors[0] != "No significant risk factors identified":
            summary += f"Key concerns: {', '.join(risk_factors[:2])}. "
        
        prob_6m = placement_probs['6m'][0]
        summary += f"Estimated 6-month placement probability: {prob_6m*100:.0f}%. "
        
        return summary

    def generate_recommendations(
        self,
        risk_level: RiskLevel,
        risk_factors: List[str],
        features: pd.DataFrame
    ) -> List[str]:
        """Fallback rule-based recommendations generator"""
        recs = ["Complete additional certifications", "Update your resume"]
        if risk_level == RiskLevel.HIGH:
            recs.append("Schedule a session with your placement cell")
        return recs

    def generate_advanced_recommendations(
        self,
        student_data: Dict,
        risk_assessment: Dict,
        placement_probs: Dict,
        salary_pred: Dict
    ) -> Dict:
        """
        Main entry point for Phase 3: Try Gemini first, fallback to rules.
        """
        # 1. Try Gemini
        if self._client:
            ai_data = self._generate_gemini_roadmap(
                student_data, risk_assessment, placement_probs, salary_pred
            )
            if ai_data:
                return ai_data

        # 2. Fallback
        risk_level = risk_assessment.get('risk_level', RiskLevel.MEDIUM)
        risk_factors = risk_assessment.get('risk_factors', [])
        
        # We need the features DataFrame for the fallback methods
        # In this context, we might not have it easily, so we use simplified versions
        summary = self.generate_summary(risk_level, risk_factors, placement_probs, salary_pred)
        actions = self.generate_recommendations(risk_level, risk_factors, pd.DataFrame())
        
        return {
            "summary": summary,
            "next_best_actions": actions,
            "is_ai_generated": False
        }

    def _generate_gemini_roadmap(self, student, risk, probs, salary) -> Optional[Dict]:
        """Call Gemini to generate a personalized career roadmap"""
        try:
            academic = student.get('academic', {})
            course = academic.get('course_type', 'Engineering')
            cgpa = academic.get('cgpa', 7.0)
            
            prompt = f"""
            Act as an expert Career Counselor. Analyze this student's placement risk profile and provide a 4-step actionable roadmap.
            
            STUDENT PROFILE:
            - Course: {course}
            - CGPA: {cgpa}
            - Current Risk Score: {risk.get('placement_risk_score')*100:.1f}% ({risk.get('risk_level')})
            - 6-Month Placement Probability: {probs.get('6m')[0]*100:.1f}%
            - Predicted Salary: INR {salary.get('expected_salary_avg')[0]/100000:.2f} Lakhs/yr
            
            RISK FACTORS IDENTIFIED:
            {", ".join(risk.get('risk_factors', []))}
            
            REQUIREMENTS:
            1. Keep it professional and encouraging.
            2. Provide exactly 4 numbered steps.
            3. Each step should be highly specific to the {course} domain.
            4. Start with a 1-sentence "AI Executive Summary".
            
            Format the output as a JSON object with two keys: "summary" (string) and "next_best_actions" (list of 4 strings).
            """
            
            from google.genai import types
            response = self._client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                )
            )
            
            text = response.text
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                data["is_ai_generated"] = True
                return data
                
        except Exception as e:
            print(f"Gemini Error: {e}")
            
        return None

    def get_recruiter_matches(self, course_type: str) -> List[str]:
        """Static list of recruiters"""
        return ["Top Tech Firms", "Management Consulting", "Placement Network Partners"]
