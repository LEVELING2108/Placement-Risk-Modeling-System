from fpdf import FPDF
from datetime import datetime
from typing import Dict, Any
import matplotlib.pyplot as plt
import tempfile
import os
import io

class ReportGenerator:
    """
    Generates professional PDF Credit Memos / Risk Summaries with Visual Charts
    """
    
    def __init__(self, student_data: Dict[str, Any]):
        self.student = student_data
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        
        # Try to find a working font
        self.font = "helvetica"
        try:
            self.pdf.set_font(self.font, 'B', 16)
        except:
            self.font = "Arial" # Fallback
        
    def generate(self) -> bytes:
        """
        Create the full PDF document and return bytes
        """
        print("DEBUG: PDF Generation started")
        self._header()
        self._student_info()
        self._risk_assessment()
        self._placement_prediction()
        self._explainability_chart()
        self._ai_roadmap()
        self._footer()
        print("DEBUG: PDF Generation complete")
        
        return self.pdf.output()

    def _safe_text(self, text: Any) -> str:
        """Sanitize text for PDF (latin-1 compatibility)"""
        if text is None: return "N/A"
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    def _header(self):
        self.pdf.set_font(self.font, 'B', 20)
        self.pdf.set_text_color(79, 70, 229) # Primary Indigo
        self.pdf.cell(0, 10, 'PlacementRisk AI', ln=True, align='C')
        
        self.pdf.set_font(self.font, '', 10)
        self.pdf.set_text_color(100, 116, 139) # Secondary Slate
        self.pdf.cell(0, 10, 'Lender Decision Support System - Official Credit Memo', ln=True, align='C')
        
        self.pdf.line(10, 30, 200, 30)
        self.pdf.ln(15)

    def _student_info(self):
        self.pdf.set_font(self.font, 'B', 14)
        self.pdf.set_text_color(30, 41, 59)
        self.pdf.cell(0, 10, 'I. STUDENT PROFILE', ln=True)
        
        self.pdf.set_font(self.font, '', 11)
        self.pdf.set_text_color(0, 0, 0)
        
        academic = self.student.get('academic', {})
        institute = self.student.get('institute', {})
        
        col_width = self.pdf.epw / 2
        
        self.pdf.cell(col_width, 8, f"Student ID: {self._safe_text(self.student.get('student_id'))}")
        self.pdf.cell(col_width, 8, f"Course: {self._safe_text(academic.get('course_type'))}", ln=True)
        
        self.pdf.cell(col_width, 8, f"CGPA: {self._safe_text(academic.get('cgpa'))}")
        self.pdf.cell(col_width, 8, f"Institute Tier: {self._safe_text(institute.get('institute_tier'))}", ln=True)
        
        self.pdf.cell(col_width, 8, f"Internships: {self._safe_text(academic.get('internship_count', 0))}")
        self.pdf.cell(col_width, 8, f"Current Semester: {self._safe_text(academic.get('semester'))}", ln=True)
        
        self.pdf.ln(10)

    def _risk_assessment(self):
        pred = self.student.get('prediction', {})
        risk = pred.get('risk_assessment', {})
        
        self.pdf.set_font(self.font, 'B', 14)
        self.pdf.cell(0, 10, 'II. RISK ASSESSMENT', ln=True)
        
        # Risk Box
        risk_level_raw = risk.get('risk_level', 'Unknown')
        risk_level = str(risk_level_raw).split('.')[-1].upper()
        risk_score = risk.get('placement_risk_score', 0)
        
        # Color coding
        if 'LOW' in risk_level: 
            self.pdf.set_fill_color(209, 250, 229); self.pdf.set_text_color(6, 95, 70)
        elif 'MEDIUM' in risk_level:
            self.pdf.set_fill_color(254, 243, 199); self.pdf.set_text_color(146, 64, 14)
        else:
            self.pdf.set_fill_color(254, 226, 226); self.pdf.set_text_color(153, 27, 27)
            
        self.pdf.set_font(self.font, 'B', 12)
        self.pdf.cell(0, 12, f"  OVERALL RISK LEVEL: {risk_level} (Score: {risk_score*100:.1f}%)", ln=True, fill=True)
        
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font(self.font, 'B', 11)
        self.pdf.ln(5)
        self.pdf.cell(0, 8, 'Key Risk Drivers:', ln=True)
        
        self.pdf.set_font(self.font, '', 10)
        factors = risk.get('risk_factors', [])
        for f in factors:
            self.pdf.cell(0, 6, f"- {self._safe_text(f)}", ln=True)
            
        self.pdf.ln(10)

    def _placement_prediction(self):
        pred = self.student.get('prediction', {})
        placement = pred.get('placement_prediction', {})
        salary = pred.get('salary_prediction', {})
        
        self.pdf.set_font(self.font, 'B', 14)
        self.pdf.cell(0, 10, 'III. EMPLOYABILITY FORECAST', ln=True)
        
        self.pdf.set_font(self.font, '', 11)
        self.pdf.cell(0, 8, f"Predicted Timeline: {self._safe_text(placement.get('predicted_timeline'))}", ln=True)
        self.pdf.cell(0, 8, f"6-Month Placement Probability: {placement.get('probability_6_months', 0)*100:.1f}%", ln=True)
        
        avg_sal = salary.get('expected_salary_avg', 0)
        self.pdf.cell(0, 8, f"Estimated Starting Salary: INR {avg_sal/100000:.2f} Lakhs/yr", ln=True)
        
        self.pdf.ln(10)

    def _explainability_chart(self):
        pred = self.student.get('prediction', {})
        scores = pred.get('explainability_scores', {})
        
        if not scores: return
        
        self.pdf.set_font(self.font, 'B', 14)
        self.pdf.cell(0, 10, 'IV. FEATURE CONTRIBUTIONS (SHAP)', ln=True)
        self.pdf.set_font(self.font, '', 10)
        self.pdf.cell(0, 6, 'Visual representation of factors impacting placement probability:', ln=True)
        
        # Generate Plot
        try:
            # Sort and take top 10
            sorted_scores = sorted(scores.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
            labels = [s[0].replace('_', ' ').title() for s in sorted_scores]
            values = [s[1] for s in sorted_scores]
            colors = ['#10b981' if v > 0 else '#ef4444' for v in values]
            
            plt.figure(figsize=(8, 5))
            plt.barh(labels, values, color=colors)
            plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
            plt.xlabel('Contribution Score')
            plt.title('Top Factors Driving Prediction')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                plt.savefig(tmp.name, dpi=300)
                plt.close()
                # Insert into PDF
                self.pdf.image(tmp.name, x=15, w=180)
                os.unlink(tmp.name) # Clean up
                
            self.pdf.ln(5)
        except Exception as e:
            print(f"ERROR: Could not generate SHAP chart for PDF: {e}")
            self.pdf.set_font(self.font, 'I', 10)
            self.pdf.cell(0, 10, '(Visual chart generation failed, see text assessment)', ln=True)

    def _ai_roadmap(self):
        pred = self.student.get('prediction', {})
        recs = pred.get('recommendations', {})
        
        if not recs: return
        
        self.pdf.set_font(self.font, 'B', 14)
        self.pdf.cell(0, 10, 'IV. AI-GENERATED CAREER ROADMAP', ln=True)
        
        self.pdf.set_font(self.font, 'I', 10)
        summary = self._safe_text(recs.get('summary', ''))
        self.pdf.multi_cell(0, 6, summary)
        self.pdf.ln(5)
        
        self.pdf.set_font(self.font, 'B', 11)
        self.pdf.cell(0, 8, 'Proposed Action Plan:', ln=True)
        
        self.pdf.set_font(self.font, '', 10)
        actions = recs.get('next_best_actions', [])
        for i, action in enumerate(actions, 1):
            self.pdf.multi_cell(0, 6, f"{i}. {self._safe_text(action)}")
            self.pdf.ln(2)

    def _footer(self):
        self.pdf.set_y(-30)
        self.pdf.set_font(self.font, 'I', 8)
        self.pdf.set_text_color(128, 128, 128)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.pdf.cell(0, 10, f'Report generated on {timestamp} by PlacementRisk AI Engine v2.0', align='C', ln=True)
        self.pdf.cell(0, 5, f'Page {self.pdf.page_no()}', align='C')
