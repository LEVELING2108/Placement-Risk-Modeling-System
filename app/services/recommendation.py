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

class RecommendationEngine:
    """
    Generates AI-powered summaries and actionable recommendations.
    Uses a priority system: Gemini -> Groq (Fallback) -> Static Rules (Final Fallback).
    """
    
    def __init__(self):
        # Gemini Setup
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self._gemini_client = None
        if self.gemini_key:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=self.gemini_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")

        # Groq Setup
        self.groq_key = os.getenv("GROQ_API_KEY")
        self._groq_client = None
        if self.groq_key:
            try:
                from groq import Groq
                self._groq_client = Groq(api_key=self.groq_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Groq client: {e}")

    def generate_advanced_recommendations(
        self,
        student_data: Dict,
        risk_assessment: Dict,
        placement_probs: Dict,
        salary_pred: Dict
    ) -> Dict:
        """
        Main entry point: Tries Gemini, then Groq, then Fallback rules.
        """
        # 1. Try Gemini (Primary)
        if self._gemini_client:
            try:
                ai_data = self._generate_gemini_roadmap(
                    student_data, risk_assessment, placement_probs, salary_pred
                )
                if ai_data:
                    return ai_data
            except Exception as e:
                print(f"Gemini failed, trying Groq fallback... Error: {e}")

        # 2. Try Groq (Secondary Fallback)
        if self._groq_client:
            try:
                ai_data = self._generate_groq_roadmap(
                    student_data, risk_assessment, placement_probs, salary_pred
                )
                if ai_data:
                    ai_data["summary"] = "[Groq] " + ai_data["summary"]
                    return ai_data
            except Exception as e:
                print(f"Groq failed, using static fallback... Error: {e}")

        # 3. Final Fallback (Static Rules)
        risk_level = risk_assessment.get('risk_level', RiskLevel.MEDIUM)
        risk_factors = risk_assessment.get('risk_factors', [])
        
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
            
            prompt = self._get_prompt(course, cgpa, risk, probs, salary)
            
            from google.genai import types
            response = self._gemini_client.models.generate_content(
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
            if "429" not in str(e): # Don't spam logs for simple quota issues
                print(f"Gemini API error: {e}")
        return None

    def _generate_groq_roadmap(self, student, risk, probs, salary) -> Optional[Dict]:
        """Call Groq (Llama 3.1) to generate a roadmap if Gemini fails"""
        try:
            academic = student.get('academic', {})
            course = academic.get('course_type', 'Engineering')
            cgpa = academic.get('cgpa', 7.0)
            
            prompt = self._get_prompt(course, cgpa, risk, probs, salary)
            prompt += "\nCRITICAL: The 'next_best_actions' must be a simple List of Strings, NOT a list of objects."

            response = self._groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a career counselor. Provide responses in JSON format where 'next_best_actions' is a list of strings."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            
            # Post-process to ensure it matches schema if LLM disobeyed
            if "next_best_actions" in data:
                actions = []
                for action in data["next_best_actions"]:
                    if isinstance(action, dict):
                        # Extract description or first string value
                        actions.append(action.get('description') or action.get('text') or str(list(action.values())[0]))
                    else:
                        actions.append(str(action))
                data["next_best_actions"] = actions
                
            data["is_ai_generated"] = True
            return data
        except Exception as e:
            print(f"Groq API error: {e}")
        return None

    def _get_prompt(self, course, cgpa, risk, probs, salary) -> str:
        return f"""
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

    def generate_summary(self, risk_level, risk_factors, placement_probs, salary_pred, features=None) -> str:
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

    def generate_recommendations(self, risk_level, risk_factors, features) -> List[str]:
        """Fallback rule-based recommendations generator"""
        recs = ["Complete additional certifications", "Update your resume"]
        if risk_level == RiskLevel.HIGH:
            recs.append("Schedule a session with your placement cell")
        return recs

    def get_recruiter_matches(self, course_type: str) -> List[str]:
        """Static list of recruiters"""
        return ["Top Tech Firms", "Management Consulting", "Placement Network Partners"]
