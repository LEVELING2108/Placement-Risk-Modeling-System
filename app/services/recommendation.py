"""
AI-generated summary and recommendation engine using Gemini & Groq
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import os
import json
import re
from app.schemas.prediction import RiskLevel
from app.db.models import TenantSettings
from sqlalchemy.orm import Session

class RecommendationEngine:
    """
    Generates AI-powered summaries and actionable recommendations.
    Uses a priority system: Gemini -> Groq (Fallback) -> Static Rules (Final Fallback).
    Now supports dynamic API keys from database settings.
    """
    
    def __init__(self):
        # Default keys from environment (fallbacks)
        self.default_gemini_key = os.getenv("GEMINI_API_KEY")
        self.default_groq_key = os.getenv("GROQ_API_KEY")

    def generate_advanced_recommendations(
        self,
        student_data: Dict,
        risk_assessment: Dict,
        placement_probs: Dict,
        salary_pred: Dict,
        tenant_id: str = "default",
        db: Optional[Session] = None
    ) -> Dict:
        """
        Main entry point: Tries Gemini, then Groq, then Fallback rules.
        Fetches tenant-specific keys from DB if provided.
        """
        # 1. Resolve API Keys (DB has priority over Env)
        gemini_key = self.default_gemini_key
        groq_key = self.default_groq_key
        
        if db and tenant_id:
            settings = db.query(TenantSettings).filter(TenantSettings.tenant_id == tenant_id).first()
            if settings:
                if settings.gemini_api_key: gemini_key = settings.gemini_api_key
                if settings.groq_api_key: groq_key = settings.groq_api_key

        # 2. Try Gemini (Primary)
        if gemini_key:
            try:
                ai_data = self._generate_gemini_roadmap(
                    student_data, risk_assessment, placement_probs, salary_pred, gemini_key
                )
                if ai_data:
                    return ai_data
            except Exception as e:
                print(f"Gemini failed, trying Groq fallback... Error: {e}")

        # 3. Try Groq (Secondary Fallback)
        if groq_key:
            try:
                ai_data = self._generate_groq_roadmap(
                    student_data, risk_assessment, placement_probs, salary_pred, groq_key
                )
                if ai_data:
                    ai_data["summary"] = "[Groq] " + ai_data["summary"]
                    return ai_data
            except Exception as e:
                print(f"Groq failed, using static fallback... Error: {e}")

        # 4. Final Fallback (Static Rules)
        risk_level = risk_assessment.get('risk_level', RiskLevel.MEDIUM)
        risk_factors = risk_assessment.get('risk_factors', [])
        
        summary = self.generate_summary(risk_level, risk_factors, placement_probs, salary_pred)
        actions = self.generate_recommendations(risk_level, risk_factors, pd.DataFrame())
        
        return {
            "summary": summary,
            "next_best_actions": actions,
            "is_ai_generated": False
        }

    def _generate_gemini_roadmap(self, student, risk, probs, salary, api_key) -> Optional[Dict]:
        """Call Gemini with provided key"""
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            
            academic = student.get('academic', {})
            course = academic.get('course_type', 'Engineering')
            cgpa = academic.get('cgpa', 7.0)
            
            prompt = self._get_prompt(course, cgpa, risk, probs, salary)
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type='application/json')
            )
            
            text = response.text
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                data["is_ai_generated"] = True
                return data
        except:
            return None

    def _generate_groq_roadmap(self, student, risk, probs, salary, api_key) -> Optional[Dict]:
        """Call Groq with provided key"""
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            
            academic = student.get('academic', {})
            course = academic.get('course_type', 'Engineering')
            cgpa = academic.get('cgpa', 7.0)
            
            prompt = self._get_prompt(course, cgpa, risk, probs, salary)
            prompt += "\nCRITICAL: The 'next_best_actions' must be a simple List of Strings."

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a career counselor. JSON format, next_best_actions is list of strings."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            
            if "next_best_actions" in data:
                actions = []
                for action in data["next_best_actions"]:
                    if isinstance(action, dict):
                        actions.append(action.get('description') or action.get('text') or str(list(action.values())[0]))
                    else:
                        actions.append(str(action))
                data["next_best_actions"] = actions
                
            data["is_ai_generated"] = True
            return data
        except:
            return None

    def _get_prompt(self, course, cgpa, risk, probs, salary) -> str:
        return f"""
        Act as an expert Career Counselor. 4-step roadmap for student risk profile.
        STUDENT: Course {course}, CGPA {cgpa}, Risk {risk.get('risk_level')} ({risk.get('placement_risk_score')*100:.1f}%)
        PROBS: 6m {probs.get('6m')[0]*100:.1f}%, SALARY: {salary.get('expected_salary_avg')[0]/100000:.2f}L
        FACTORS: {", ".join(risk.get('risk_factors', []))}
        JSON keys: "summary" (string), "next_best_actions" (list of 4 strings).
        """

    def generate_summary(self, risk_level, risk_factors, placement_probs, salary_pred, features=None) -> str:
        if risk_level == RiskLevel.HIGH: summary = "HIGH RISK: Significant challenges. "
        elif risk_level == RiskLevel.MEDIUM: summary = "MEDIUM RISK: Moderate prospects. "
        else: summary = "LOW RISK: Strong potential. "
        prob_6m = placement_probs['6m'][0]
        summary += f"6-month probability: {prob_6m*100:.0f}%."
        return summary

    def generate_recommendations(self, risk_level, risk_factors, features) -> List[str]:
        return ["Complete certifications", "Update resume", "Apply for more internships"]

    def get_recruiter_matches(self, course_type: str) -> List[str]:
        return ["Top Tech Firms", "Management Consulting", "Placement Network Partners"]
