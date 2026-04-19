# Complete Setup Guide - Placement-Risk Modeling System

## Quick Start (For Immediate Use)

Your project is **ALREADY CONFIGURED** and ready to use! Follow these simple steps:

### Option 1: One-Line Start (Recommended)
```bash
# Validate everything is working
python validate_setup.py

# Start the server
python main.py
```

Then visit:
- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Option 2: Complete Fresh Setup

If you're setting up on a new machine or want to start fresh:

## Step 1: Prerequisites

### Required Software
- **Python 3.9 or higher** (Currently: 3.12.1)
- **pip** (Python package manager)
- **Git** (optional, for version control)

### Check Python Version
```bash
python --version
# Should show: Python 3.9.x or higher
```

## Step 2: Install Dependencies

```bash
# Navigate to project directory
cd "Placement-Risk Modeling system"

# Install all required packages
pip install -r requirements.txt
```

### Core Dependencies Installed:
- ✅ FastAPI (0.104.1) - Web framework
- ✅ Uvicorn (0.24.0) - ASGI server
- ✅ Pydantic (2.5.0) - Data validation
- ✅ Pandas (2.1.4) - Data processing
- ✅ NumPy (1.26.2) - Numerical computing
- ✅ Scikit-learn (1.3.2) - Machine learning
- ✅ XGBoost (2.0.3) - Gradient boosting
- ✅ Joblib (1.3.2) - Model persistence

## Step 3: Verify Setup

Run the comprehensive validation script:

```bash
python validate_setup.py
```

This will check:
1. ✓ Python version compatibility
2. ✓ All dependencies installed
3. ✓ Directory structure intact
4. ✓ Trained models present
5. ✓ Data files exist
6. ✓ Module imports working
7. ✓ Models load successfully
8. ✓ API configuration valid
9. ✓ Prediction pipeline functional

**Expected Output**: `9/9 checks passed`

## Step 4: Train Models (If Needed)

**NOTE**: Your system **ALREADY HAS TRAINED MODELS**, so you can skip this step!

But if you want to retrain with fresh data:

```bash
python train.py
```

This will:
- Generate 2,000 synthetic student samples
- Train placement prediction models (3/6/12 months)
- Train salary estimation model
- Save models to `models/` directory
- Output training metrics to `data/training_metrics.json`

**Training Time**: ~2-5 minutes on average hardware

## Step 5: Start the Server

```bash
python main.py
```

**Server will start on**: http://localhost:8000

You'll see:
```
============================================================
PLACEMENT-RISK MODELING SYSTEM
============================================================

Dashboard: http://localhost:8000
API Docs:  http://localhost:8000/docs

============================================================
```

## Step 6: Test the System

### Option A: Using the Web Interface
1. Visit http://localhost:8000/docs
2. Expand any endpoint (e.g., `/api/v1/predict`)
3. Click "Try it out"
4. Use sample data or modify the request
5. Click "Execute"

### Option B: Using the Test Script
```bash
# In a NEW terminal window (keep server running)
python test_api.py
```

### Option C: Using cURL
```bash
curl -X POST "http://localhost:8000/api/v1/health"
```

## API Endpoints Reference

### Core Prediction Endpoints

#### 1. Single Student Prediction
```http
POST /api/v1/predict
```
Returns complete prediction including placement timeline, salary, risk assessment, and recommendations.

#### 2. Batch Prediction
```http
POST /api/v1/batch-predict
```
Process multiple students in a single request (up to 100).

#### 3. Risk Score Only
```http
POST /api/v1/risk-score
```
Get just the risk assessment without full prediction.

#### 4. Model Information
```http
GET /api/v1/model-info
```
Check model status, version, and thresholds.

#### 5. Health Check
```http
GET /api/v1/health
```
Verify API is running.

### Portfolio Management Endpoints

#### Get All Students
```http
GET /api/v1/portfolio
```

#### Portfolio Statistics
```http
GET /api/v1/portfolio/stats
```

#### Export Portfolio
```http
GET /api/v1/portfolio/export
```

#### Get Specific Student
```http
GET /api/v1/portfolio/{student_id}
```

#### Remove Student
```http
DELETE /api/v1/portfolio/{student_id}
```

### Analytics Endpoints

#### Risk by Course
```http
GET /api/v1/analytics/risk-by-course
```

#### Risk by Institute Tier
```http
GET /api/v1/analytics/risk-by-tier
```

## Testing with Sample Data

### Generate Sample Request

Run this in Python:
```python
from app.services.data_generator import SampleDataGenerator

generator = SampleDataGenerator()
student = generator.generate_single_student(
    student_id="DEMO_001",
    risk_profile='medium'  # Options: 'low', 'medium', 'high', 'random'
)

# Print the request JSON
print(student.model_dump_json(indent=2))
```

### Example Request (cURL)
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU_001",
    "academic": {
      "course_type": "Engineering",
      "current_year": 4,
      "semester": 8,
      "cgpa": 7.5,
      "academic_consistency": 0.75,
      "internship_count": 2,
      "total_internship_duration_months": 4.5,
      "internship_employer_type": "MNC",
      "internship_performance_score": 0.8,
      "skill_certifications_count": 3,
      "relevant_coursework_count": 6
    },
    "institute": {
      "institute_tier": "Tier-2",
      "historic_placement_rate_3m": 0.55,
      "historic_placement_rate_6m": 0.75,
      "historic_placement_rate_12m": 0.85,
      "historic_avg_salary": 500000,
      "placement_cell_activity_level": 0.7,
      "recruiter_participation_score": 0.65
    },
    "labor_market": {
      "field_job_demand_score": 0.7,
      "region_job_density": 0.6,
      "sector_hiring_trend": "IT",
      "sector_hiring_growth": 0.15,
      "macroeconomic_condition_score": 0.75
    },
    "real_time_signals": {
      "job_portal_applications_count": 20,
      "interview_pipeline_stage": 3,
      "resume_updates_count": 4,
      "skill_up_events_count": 3,
      "institute_placement_progress": 0.6
    }
  }'
```

## Project Structure

```
Placement-Risk Modeling system/
│
├── app/                          # Main application package
│   ├── api/
│   │   └── routes.py            # API endpoints
│   ├── core/
│   │   └── config.py            # Configuration
│   ├── models/
│   │   ├── placement_model.py   # Placement ML model
│   │   └── salary_model.py      # Salary ML model
│   ├── schemas/
│   │   └── prediction.py        # Pydantic schemas
│   └── services/
│       ├── data_generator.py    # Sample data generation
│       ├── evaluation.py        # Model evaluation
│       ├── feature_engineering.py
│       ├── prediction_service.py # Main orchestration
│       ├── preprocessing.py     # Data preprocessing
│       ├── recommendation.py    # Recommendations
│       └── risk_scoring.py      # Risk assessment
│
├── models/                      # Trained ML models
│   ├── placement_model.pkl      # 8.91 MB
│   └── salary_model.pkl         # 8.46 MB
│
├── data/                        # Data files
│   ├── training_data.csv        # Generated training data
│   ├── training_metrics.json    # Model performance
│   └── portfolio.json           # Student portfolio
│
├── static/                      # Web assets
│   └── index.html              # Dashboard
│
├── main.py                      # FastAPI application
├── train.py                     # Model training script
├── test_api.py                  # API test suite
├── validate_setup.py            # Setup validation
├── requirements.txt             # Dependencies
└── README.md                    # Documentation
```

## Common Issues & Solutions

### Issue 1: "Models not found"
**Solution**: Run `python train.py` to generate models

### Issue 2: "Port 8000 already in use"
**Solution**:
```bash
# Option A: Use different port
uvicorn main:app --port 8080

# Option B: Kill existing process (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Option B: Kill existing process (Linux/Mac)
lsof -ti:8000 | xargs kill -9
```

### Issue 3: "Import errors"
**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue 4: "Validation script fails"
**Solution**: Check the specific failed check and:
- For dependencies: `pip install -r requirements.txt`
- For models: `python train.py`
- For directory structure: Ensure you're in the project root

## Configuration

Edit `app/core/config.py` to customize:

```python
# Prediction thresholds
PLACEMENT_3M_THRESHOLD = 0.7
PLACEMENT_6M_THRESHOLD = 0.5
PLACEMENT_12M_THRESHOLD = 0.3

# Risk thresholds
HIGH_RISK_THRESHOLD = 0.7
MEDIUM_RISK_THRESHOLD = 0.4

# Salary bounds
MIN_SALARY = 100000
MAX_SALARY = 5000000
```

## Performance Metrics

### Current Model Performance:
- **3-Month Placement**: ~85-90% accuracy, ROC-AUC >0.85
- **6-Month Placement**: ~80-85% accuracy, ROC-AUC >0.85
- **12-Month Placement**: ~75-80% accuracy, ROC-AUC >0.85
- **Salary Prediction**: R² >0.80, MAPE <15%

## Deployment Options

### Local Development
```bash
python main.py
# OR
uvicorn main:app --reload
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker (if using Dockerfile)
```bash
docker build -t placement-risk-system .
docker run -p 8000:8000 placement-risk-system
```

## Support & Troubleshooting

### Check Logs
Server logs are output to console. For persistent logs:
```bash
python main.py > server.log 2>&1
```

### Debug Mode
Set FastAPI debug mode in `main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
```

### Getting Help
1. Check `README.md` for overview
2. Run `python validate_setup.py` for diagnostics
3. Review `ARCHITECTURE.md` for system design
4. Check API docs at http://localhost:8000/docs

## Next Steps After Setup

1. ✅ **System is validated** - Run `python validate_setup.py`
2. ✅ **Server is running** - Start with `python main.py`
3. ✅ **Test the API** - Use `python test_api.py`
4. 🎯 **Integrate with your system** - Use API endpoints
5. 📊 **Monitor predictions** - Check portfolio stats
6. 🔄 **Retrain periodically** - Update models with new data

## System Requirements

### Minimum:
- Python 3.9+
- 2 GB RAM
- 100 MB disk space

### Recommended:
- Python 3.10+
- 4 GB RAM
- 500 MB disk space
- Multi-core CPU for faster training

---

**✅ Your system is READY TO USE!**

Just run:
```bash
python validate_setup.py  # Verify everything
python main.py            # Start the server
```

Visit http://localhost:8000/docs and start making predictions!
