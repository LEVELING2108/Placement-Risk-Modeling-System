"""
AI-generated summary and recommendation engine
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from app.schemas.prediction import RiskLevel


class RecommendationEngine:
    """
    Generates AI-powered summaries and actionable recommendations
    for students based on their risk profile
    """
    
    def __init__(self):
        self.recommendation_templates = {
            'skill_up': [
                "Complete additional certifications in high-demand skills",
                "Enroll in industry-recognized online courses",
                "Focus on technical skills relevant to your field",
                "Build a portfolio project to showcase skills",
                "Attend workshops and bootcamps"
            ],
            'resume': [
                "Update resume with recent projects and achievements",
                "Add quantifiable accomplishments to resume",
                "Highlight internship experience and outcomes",
                "Include relevant coursework and certifications",
                "Get resume reviewed by industry professionals"
            ],
            'interview': [
                "Practice mock interviews with placement cell",
                "Prepare for technical and HR interview rounds",
                "Work on communication and presentation skills",
                "Study common interview questions for your field",
                "Participate in group discussion sessions"
            ],
            'networking': [
                "Attend industry meetups and networking events",
                "Connect with alumni in your target companies",
                "Join professional communities and forums",
                "Participate in hackathons and competitions",
                "Leverage LinkedIn for professional networking"
            ],
            'job_search': [
                "Increase job application frequency",
                "Diversify job search across multiple sectors",
                "Target companies aligned with your skills",
                "Use job portals and recruitment agencies",
                "Consider startup opportunities for faster growth"
            ],
            'internship': [
                "Apply for more internship opportunities",
                "Seek longer-duration internships",
                "Target MNCs or reputable organizations",
                "Request performance feedback from past internships",
                "Convert internship to full-time offer if possible"
            ]
        }
        
        self.recruiter_matches = {
            'Engineering': [
                'Tech Mahindra', 'Infosys', 'Wipro', 'TCS', 'Accenture',
                'Cognizant', 'HCL Technologies', 'Tech Startups'
            ],
            'MBA': [
                'Deloitte', 'KPMG', 'EY', 'PwC', 'McKinsey',
                'BCG', 'Bain', 'Banking & Financial Services'
            ],
            'Nursing': [
                'Apollo Hospitals', 'Fortis Healthcare', 'Max Healthcare',
                'AIIMS', 'Government Health Services'
            ],
            'Science': [
                'Research Labs', 'Pharma Companies', 'Biotech Firms',
                'Educational Institutions', 'Data Science Companies'
            ],
            'Commerce': [
                'Big 4 Accounting Firms', 'Banks', 'Financial Services',
                'Tax Consultancies', 'Corporate Firms'
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
        """
        Generate AI-powered summary explaining the risk assessment
        
        Args:
            risk_level: Classified risk level
            risk_factors: List of identified risk factors
            placement_probs: Placement probabilities
            salary_pred: Salary predictions (optional)
            features: Feature DataFrame (optional)
            
        Returns:
            Human-readable summary string
        """
        # Start with risk level
        if risk_level == RiskLevel.HIGH:
            summary = "HIGH RISK: This student shows significant placement challenges. "
        elif risk_level == RiskLevel.MEDIUM:
            summary = "MEDIUM RISK: This student has moderate placement prospects with room for improvement. "
        else:
            summary = "LOW RISK: This student demonstrates strong placement potential. "
        
        # Add key risk factors (top 3)
        if risk_factors and risk_factors[0] != "No significant risk factors identified":
            top_factors = risk_factors[:3]
            summary += f"Key concerns: {', '.join(top_factors)}. "
        
        # Add placement probability context
        prob_3m = placement_probs['3m'][0]
        prob_6m = placement_probs['6m'][0]
        prob_12m = placement_probs['12m'][0]
        
        if prob_3m >= 0.7:
            summary += f"Strong likelihood of placement within 3 months ({prob_3m*100:.0f}% probability). "
        elif prob_6m >= 0.5:
            summary += f"Expected placement within 6 months ({prob_6m*100:.0f}% probability). "
        elif prob_12m >= 0.3:
            summary += f"Placement likely within 12 months ({prob_12m*100:.0f}% probability). "
        else:
            summary += "May face significant delays in securing employment. "
        
        # Add salary context if available
        if salary_pred and 'expected_salary_avg' in salary_pred:
            avg_salary = salary_pred['expected_salary_avg'][0]
            summary += f"Expected starting salary: Rs.{avg_salary/100000:.2f} Lakhs. "
        
        # Add positive notes if applicable
        if features is not None:
            if 'internship_count' in features.columns:
                if features['internship_count'].values[0] >= 2:
                    summary += "Strong internship background is a positive indicator. "
            
            if 'cgpa' in features.columns:
                if features['cgpa'].values[0] >= 8.0:
                    summary += "Excellent academic performance strengthens employability. "
            
            if 'skill_certifications_count' in features.columns:
                if features['skill_certifications_count'].values[0] >= 3:
                    summary += "Multiple certifications demonstrate proactive skill development. "
        
        return summary
    
    def generate_recommendations(
        self,
        risk_level: RiskLevel,
        risk_factors: List[str],
        features: pd.DataFrame
    ) -> List[str]:
        """
        Generate actionable next-best recommendations
        
        Args:
            risk_level: Classified risk level
            risk_factors: List of identified risk factors
            features: Feature DataFrame
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Determine priority recommendations based on risk factors
        for factor in risk_factors:
            if 'internship' in factor.lower():
                recommendations.extend(self.recommendation_templates['internship'][:2])
            
            if 'cgpa' in factor.lower() or 'academic' in factor.lower():
                recommendations.extend(self.recommendation_templates['skill_up'][:2])
            
            if 'resume' in factor.lower():
                recommendations.extend(self.recommendation_templates['resume'][:2])
            
            if 'interview' in factor.lower():
                recommendations.extend(self.recommendation_templates['interview'][:2])
            
            if 'skill' in factor.lower() or 'certification' in factor.lower():
                recommendations.extend(self.recommendation_templates['skill_up'][:2])
            
            if 'job application' in factor.lower() or 'activity' in factor.lower():
                recommendations.extend(self.recommendation_templates['job_search'][:2])
            
            if 'networking' in factor.lower():
                recommendations.extend(self.recommendation_templates['networking'][:2])
        
        # Add risk-level specific recommendations
        if risk_level == RiskLevel.HIGH:
            # High risk: comprehensive intervention
            recommendations.extend([
                "Schedule immediate counseling session with placement cell",
                "Create structured 90-day placement action plan",
                "Identify and address skill gaps urgently"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            # Medium risk: targeted improvement
            recommendations.extend([
                "Focus on top 2-3 identified risk areas",
                "Increase engagement with placement services",
                "Set weekly job application targets"
            ])
        else:
            # Low risk: optimization
            recommendations.extend([
                "Maintain current job search momentum",
                "Target premium opportunities aligned with skills",
                "Negotiate salary confidently based on profile"
            ])
        
        # Remove duplicates and limit to top 5
        unique_recs = list(dict.fromkeys(recommendations))
        return unique_recs[:5]
    
    def get_recruiter_matches(self, course_type: str) -> List[str]:
        """
        Get high-potential recruiter matches for a course type
        
        Args:
            course_type: Student's course type
            
        Returns:
            List of recruiter/company names
        """
        # Try exact match first
        if course_type in self.recruiter_matches:
            return self.recruiter_matches[course_type]
        
        # Try partial matching
        for key in self.recruiter_matches.keys():
            if key.lower() in course_type.lower():
                return self.recruiter_matches[key]
        
        # Default: return general recruiters
        return [
            'Leading Companies in Sector',
            'Industry-Specific Recruiters',
            'Placement Network Partners'
        ]
