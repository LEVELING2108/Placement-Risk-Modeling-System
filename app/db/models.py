from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    tenant_id = Column(String, index=True)
    
    predictions = relationship("PredictionResult", back_populates="lender")

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    tenant_id = Column(String, index=True)
    
    # Store full input data as JSON for flexibility
    academic_data = Column(JSON)
    institute_data = Column(JSON)
    labor_market_data = Column(JSON)
    real_time_signals = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    predictions = relationship("PredictionResult", back_populates="student")

class PredictionResult(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id"))
    lender_id = Column(Integer, ForeignKey("users.id"))
    tenant_id = Column(String, index=True)
    
    # Prediction Metrics
    placement_risk_score = Column(Float)
    risk_level = Column(String)
    predicted_timeline = Column(String)
    expected_salary_avg = Column(Float)
    
    # Full prediction JSON (for roadmaps, SHAP, etc.)
    full_prediction = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    student = relationship("StudentProfile", back_populates="predictions")
    lender = relationship("User", back_populates="predictions")

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String)
    trained_at = Column(DateTime)
    metrics = Column(JSON)
    feature_count = Column(Integer)
    is_active = Column(Boolean, default=True)
