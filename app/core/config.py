"""
Configuration settings for the application
"""

class Settings:
    APP_NAME = "Placement-Risk Modeling System"
    APP_VERSION = "1.0.0"
    
    # Data and Model paths
    MODEL_DIR = "models"
    DATA_DIR = "data"
    PLACEMENT_MODEL_PATH = "models/placement_model.pkl"
    SALARY_MODEL_PATH = "models/salary_model.pkl"
    SCALER_PATH = "models/scaler.pkl"
    PORTFOLIO_PATH = "data/portfolio.json"
    
    # Prediction thresholds
    PLACEMENT_3M_THRESHOLD = 0.7
    PLACEMENT_6M_THRESHOLD = 0.5
    PLACEMENT_12M_THRESHOLD = 0.3
    
    # Risk score thresholds
    HIGH_RISK_THRESHOLD = 0.7
    MEDIUM_RISK_THRESHOLD = 0.4
    
    # Salary bounds (in local currency)
    MIN_SALARY = 100000
    MAX_SALARY = 5000000
    
    # Feature engineering constants
    COURSE_ENCODINGS = {
        "Engineering": 0,
        "MBA": 1,
        "Nursing": 2,
        "Arts": 3,
        "Science": 4,
        "Commerce": 5,
        "Law": 6,
        "Medical": 7,
        "Pharmacy": 8,
        "Other": 9
    }
    
    INSTITUTE_TIER_ENCODINGS = {
        "Tier-1": 0,
        "Tier-2": 1,
        "Tier-3": 2
    }
    
    SECTOR_ENCODINGS = {
        "IT": 0,
        "BFSI": 1,
        "Manufacturing": 2,
        "Healthcare": 3,
        "Education": 4,
        "Retail": 5,
        "Telecom": 6,
        "Energy": 7,
        "Other": 8
    }

settings = Settings()
