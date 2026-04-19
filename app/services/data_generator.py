"""
Sample data generator for testing and model training
"""

import numpy as np
import pandas as pd
from typing import List, Dict
import json

from app.schemas.prediction import (
    StudentPredictionRequest,
    StudentAcademicData,
    InstituteData,
    LaborMarketData,
    RealTimeSignals,
    CourseType,
    InstituteTier,
    Sector
)


class SampleDataGenerator:
    """Generates realistic sample data for testing and training"""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)
    
    def generate_single_student(
        self, 
        student_id: str = None,
        risk_profile: str = 'random'
    ) -> StudentPredictionRequest:
        """
        Generate a single student prediction request
        
        Args:
            student_id: Student ID (auto-generated if None)
            risk_profile: 'low', 'medium', 'high', or 'random'
            
        Returns:
            StudentPredictionRequest
        """
        if student_id is None:
            student_id = f"STU_{np.random.randint(10000, 99999)}"
        
        if risk_profile == 'random':
            risk_profile = np.random.choice(['low', 'medium', 'high'])
        
        # Generate academic data based on risk profile
        academic = self._generate_academic_data(risk_profile)
        
        # Generate institute data
        institute = self._generate_institute_data(risk_profile)
        
        # Generate labor market data
        labor_market = self._generate_labor_market_data(risk_profile)
        
        # Generate real-time signals
        real_time_signals = self._generate_real_time_signals(risk_profile)
        
        return StudentPredictionRequest(
            student_id=student_id,
            academic=academic,
            institute=institute,
            labor_market=labor_market,
            real_time_signals=real_time_signals
        )
    
    def generate_dataset(
        self, 
        n_students: int = 1000,
        include_outcomes: bool = True
    ) -> pd.DataFrame:
        """
        Generate a complete dataset for training
        
        Args:
            n_students: Number of students to generate
            include_outcomes: Whether to include outcome labels
            
        Returns:
            DataFrame with features and optional outcomes
        """
        records = []
        
        for i in range(n_students):
            # Random risk profile (weighted)
            risk_profile = ['low', 'medium', 'high'][np.random.choice([0, 1, 2], p=[0.4, 0.35, 0.25])]
            
            student = self.generate_single_student(
                student_id=f"STU_{i+1}",
                risk_profile=risk_profile
            )
            
            # Flatten to dictionary
            record = self._flatten_student(student)
            
            # Add outcomes if requested
            if include_outcomes:
                outcomes = self._generate_outcomes(record, risk_profile)
                record.update(outcomes)
            
            records.append(record)
        
        df = pd.DataFrame(records)
        return df
    
    def _generate_academic_data(self, risk_profile: str) -> StudentAcademicData:
        """Generate academic data based on risk profile"""
        if risk_profile == 'low':
            cgpa = np.random.uniform(7.5, 9.5)
            academic_consistency = np.random.uniform(0.7, 1.0)
            internship_count = np.random.choice([2, 3, 4], p=[0.5, 0.3, 0.2])
            total_internship_duration = np.random.uniform(3, 8)
            internship_performance = np.random.uniform(0.7, 1.0)
            skill_certifications = np.random.randint(2, 6)
            relevant_coursework = np.random.randint(5, 12)
        elif risk_profile == 'medium':
            cgpa = np.random.uniform(6.0, 8.0)
            academic_consistency = np.random.uniform(0.5, 0.8)
            internship_count = np.random.choice([1, 2], p=[0.6, 0.4])
            total_internship_duration = np.random.uniform(1, 4)
            internship_performance = np.random.uniform(0.5, 0.8)
            skill_certifications = np.random.randint(1, 4)
            relevant_coursework = np.random.randint(3, 8)
        else:  # high risk
            cgpa = np.random.uniform(4.5, 7.0)
            academic_consistency = np.random.uniform(0.2, 0.6)
            internship_count = np.random.choice([0, 1], p=[0.6, 0.4])
            total_internship_duration = np.random.uniform(0, 2)
            internship_performance = np.random.uniform(0.3, 0.6) if np.random.random() > 0.4 else None
            skill_certifications = np.random.randint(0, 2)
            relevant_coursework = np.random.randint(1, 5)
        
        course_types = [CourseType.ENGINEERING, CourseType.MBA, CourseType.NURSING, 
                        CourseType.ARTS, CourseType.SCIENCE, CourseType.COMMERCE,
                        CourseType.LAW, CourseType.MEDICAL, CourseType.PHARMACY, CourseType.OTHER]
        course_type = course_types[int(np.random.randint(0, len(course_types)))]
        
        return StudentAcademicData(
            course_type=course_type,
            current_year=np.random.randint(1, 5),
            semester=np.random.randint(1, 10),
            cgpa=round(cgpa, 2),
            academic_consistency=round(academic_consistency, 2),
            internship_count=internship_count,
            total_internship_duration_months=round(total_internship_duration, 1),
            internship_employer_type=np.random.choice(['MNC', 'Startup', 'Mid-size', 'Government']),
            internship_performance_score=round(internship_performance, 2) if internship_performance else None,
            skill_certifications_count=skill_certifications,
            relevant_coursework_count=relevant_coursework
        )
    
    def _generate_institute_data(self, risk_profile: str) -> InstituteData:
        """Generate institute data based on risk profile"""
        if risk_profile == 'low':
            tier_idx = np.random.choice([0, 1], p=[0.7, 0.3])
            tier = [InstituteTier.TIER_1, InstituteTier.TIER_2][tier_idx]
            placement_3m = np.random.uniform(0.6, 0.9)
            placement_6m = np.random.uniform(0.75, 0.95)
            placement_12m = np.random.uniform(0.85, 0.98)
            avg_salary = np.random.uniform(600000, 1500000)
            placement_cell_activity = np.random.uniform(0.7, 1.0)
            recruiter_participation = np.random.uniform(0.7, 1.0)
        elif risk_profile == 'medium':
            profile_idx = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])
            tier = [InstituteTier.TIER_1, InstituteTier.TIER_2, InstituteTier.TIER_3][profile_idx]
            placement_3m = np.random.uniform(0.4, 0.65)
            placement_6m = np.random.uniform(0.55, 0.8)
            placement_12m = np.random.uniform(0.7, 0.9)
            avg_salary = np.random.uniform(350000, 700000)
            placement_cell_activity = np.random.uniform(0.5, 0.75)
            recruiter_participation = np.random.uniform(0.5, 0.75)
        else:  # high risk
            tier_idx = np.random.choice([0, 1], p=[0.4, 0.6])
            tier = [InstituteTier.TIER_2, InstituteTier.TIER_3][tier_idx]
            placement_3m = np.random.uniform(0.2, 0.45)
            placement_6m = np.random.uniform(0.35, 0.6)
            placement_12m = np.random.uniform(0.5, 0.75)
            avg_salary = np.random.uniform(200000, 450000)
            placement_cell_activity = np.random.uniform(0.2, 0.55)
            recruiter_participation = np.random.uniform(0.2, 0.55)
        
        return InstituteData(
            institute_tier=tier,
            historic_placement_rate_3m=round(placement_3m, 2),
            historic_placement_rate_6m=round(placement_6m, 2),
            historic_placement_rate_12m=round(placement_12m, 2),
            historic_avg_salary=round(avg_salary, 0),
            placement_cell_activity_level=round(placement_cell_activity, 2),
            recruiter_participation_score=round(recruiter_participation, 2)
        )
    
    def _generate_labor_market_data(self, risk_profile: str) -> LaborMarketData:
        """Generate labor market data based on risk profile"""
        if risk_profile == 'low':
            demand_score = np.random.uniform(0.7, 1.0)
            job_density = np.random.uniform(0.7, 1.0)
            hiring_growth = np.random.uniform(0.0, 0.5)
            macro_score = np.random.uniform(0.7, 1.0)
        elif risk_profile == 'medium':
            demand_score = np.random.uniform(0.4, 0.7)
            job_density = np.random.uniform(0.4, 0.7)
            hiring_growth = np.random.uniform(-0.1, 0.2)
            macro_score = np.random.uniform(0.5, 0.7)
        else:  # high risk
            demand_score = np.random.uniform(0.1, 0.45)
            job_density = np.random.uniform(0.1, 0.45)
            hiring_growth = np.random.uniform(-0.4, 0.05)
            macro_score = np.random.uniform(0.2, 0.55)
        
        sectors = [Sector.IT, Sector.BFSI, Sector.MANUFACTURING, Sector.HEALTHCARE,
                   Sector.EDUCATION, Sector.RETAIL, Sector.TELECOM, Sector.ENERGY, Sector.OTHER]
        sector = sectors[int(np.random.randint(0, len(sectors)))]
        
        return LaborMarketData(
            field_job_demand_score=round(demand_score, 2),
            region_job_density=round(job_density, 2),
            sector_hiring_trend=sector,
            sector_hiring_growth=round(hiring_growth, 2),
            macroeconomic_condition_score=round(macro_score, 2)
        )
    
    def _generate_real_time_signals(self, risk_profile: str) -> RealTimeSignals:
        """Generate real-time signals based on risk profile"""
        if risk_profile == 'low':
            applications = np.random.randint(15, 40)
            interview_stage = np.random.randint(2, 6)
            resume_updates = np.random.randint(3, 8)
            skill_events = np.random.randint(3, 8)
            placement_progress = np.random.uniform(0.6, 1.0)
        elif risk_profile == 'medium':
            applications = np.random.randint(8, 20)
            interview_stage = np.random.randint(1, 4)
            resume_updates = np.random.randint(2, 5)
            skill_events = np.random.randint(1, 4)
            placement_progress = np.random.uniform(0.3, 0.7)
        else:  # high risk
            applications = np.random.randint(0, 10)
            interview_stage = np.random.randint(0, 2)
            resume_updates = np.random.randint(0, 3)
            skill_events = np.random.randint(0, 2)
            placement_progress = np.random.uniform(0.0, 0.4)
        
        return RealTimeSignals(
            job_portal_applications_count=int(applications),
            interview_pipeline_stage=int(interview_stage),
            resume_updates_count=int(resume_updates),
            skill_up_events_count=int(skill_events),
            institute_placement_progress=round(placement_progress, 2)
        )
    
    def _flatten_student(self, student: StudentPredictionRequest) -> Dict:
        """Flatten student request to dictionary"""
        record = {}
        
        # Academic
        record['course_type'] = student.academic.course_type.value
        record['current_year'] = student.academic.current_year
        record['semester'] = student.academic.semester
        record['cgpa'] = student.academic.cgpa
        record['academic_consistency'] = student.academic.academic_consistency
        record['internship_count'] = student.academic.internship_count
        record['total_internship_duration_months'] = student.academic.total_internship_duration_months
        record['internship_performance_score'] = student.academic.internship_performance_score
        record['skill_certifications_count'] = student.academic.skill_certifications_count
        record['relevant_coursework_count'] = student.academic.relevant_coursework_count
        
        # Institute
        record['institute_tier'] = student.institute.institute_tier.value
        record['historic_placement_rate_3m'] = student.institute.historic_placement_rate_3m
        record['historic_placement_rate_6m'] = student.institute.historic_placement_rate_6m
        record['historic_placement_rate_12m'] = student.institute.historic_placement_rate_12m
        record['historic_avg_salary'] = student.institute.historic_avg_salary
        record['placement_cell_activity_level'] = student.institute.placement_cell_activity_level
        record['recruiter_participation_score'] = student.institute.recruiter_participation_score
        
        # Labor Market
        record['field_job_demand_score'] = student.labor_market.field_job_demand_score
        record['region_job_density'] = student.labor_market.region_job_density
        record['sector_hiring_trend'] = student.labor_market.sector_hiring_trend.value
        record['sector_hiring_growth'] = student.labor_market.sector_hiring_growth
        record['macroeconomic_condition_score'] = student.labor_market.macroeconomic_condition_score
        
        # Real-time signals
        if student.real_time_signals:
            record['job_portal_applications_count'] = student.real_time_signals.job_portal_applications_count
            record['interview_pipeline_stage'] = student.real_time_signals.interview_pipeline_stage
            record['resume_updates_count'] = student.real_time_signals.resume_updates_count
            record['skill_up_events_count'] = student.real_time_signals.skill_up_events_count
            record['institute_placement_progress'] = student.real_time_signals.institute_placement_progress
        
        return record
    
    def _generate_outcomes(self, record: Dict, risk_profile: str) -> Dict:
        """Generate outcome labels based on risk profile"""
        if risk_profile == 'low':
            placed_3m = np.random.choice([0, 1], p=[0.25, 0.75])
            placed_6m = np.random.choice([0, 1], p=[0.15, 0.85]) if not placed_3m else 1
            placed_12m = 1
            salary = record.get('historic_avg_salary', 500000) * np.random.uniform(0.9, 1.2)
        elif risk_profile == 'medium':
            placed_3m = np.random.choice([0, 1], p=[0.6, 0.4])
            placed_6m = np.random.choice([0, 1], p=[0.35, 0.65]) if not placed_3m else 1
            placed_12m = np.random.choice([0, 1], p=[0.15, 0.85]) if not placed_6m else 1
            salary = record.get('historic_avg_salary', 400000) * np.random.uniform(0.8, 1.1)
        else:  # high risk
            placed_3m = np.random.choice([0, 1], p=[0.8, 0.2])
            placed_6m = np.random.choice([0, 1], p=[0.55, 0.45]) if not placed_3m else 1
            placed_12m = np.random.choice([0, 1], p=[0.3, 0.7]) if not placed_6m else 1
            salary = record.get('historic_avg_salary', 300000) * np.random.uniform(0.7, 1.0)
        
        return {
            'placed_3m': int(placed_3m),
            'placed_6m': int(placed_6m),
            'placed_12m': int(placed_12m),
            'actual_salary': round(salary, 2) if placed_12m else 0,
            'risk_profile': risk_profile
        }


if __name__ == "__main__":
    # Generate sample data
    generator = SampleDataGenerator(seed=42)
    
    # Generate single student
    student = generator.generate_single_student(risk_profile='medium')
    print("Sample Student Request:")
    print(student.model_dump_json(indent=2))
    
    # Generate dataset
    print("\nGenerating dataset with 1000 students...")
    df = generator.generate_dataset(n_students=1000, include_outcomes=True)
    print(f"\nDataset shape: {df.shape}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nRisk profile distribution:")
    print(df['risk_profile'].value_counts())
    
    # Save to CSV
    df.to_csv('sample_training_data.csv', index=False)
    print("\nDataset saved to 'sample_training_data.csv'")
