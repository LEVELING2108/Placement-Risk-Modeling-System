# Quick Reference Guide

## 🚀 Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Train models (generates data + trains + saves)
python train.py

# Start API server
python main.py

# Run tests
python test_api.py

# View examples
python examples.py

# Quick demo
python quick_start.py
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/predict` | Single student prediction |
| POST | `/api/v1/batch-predict` | Batch predictions (up to 1000) |
| POST | `/api/v1/risk-score` | Risk assessment only |
| GET | `/api/v1/model-info` | Model information |
| GET | `/api/v1/health` | Health check |

**Base URL:** `http://localhost:8000`

---

## 📥 Input Data Structure

### Student Academic Data
```python
{
    "course_type": "Engineering|MBA|Nursing|Arts|Science|Commerce|Law|Medical|Pharmacy|Other",
    "current_year": 1-5,
    "semester": 1-10,
    "cgpa": 0.0-10.0,
    "academic_consistency": 0.0-1.0,
    "internship_count": 0+,
    "total_internship_duration_months": 0.0+,
    "internship_employer_type": "MNC|Startup|Mid-size|Government",
    "internship_performance_score": 0.0-1.0,
    "skill_certifications_count": 0+,
    "relevant_coursework_count": 0+
}
```

### Institute Data
```python
{
    "institute_tier": "Tier-1|Tier-2|Tier-3",
    "historic_placement_rate_3m": 0.0-1.0,
    "historic_placement_rate_6m": 0.0-1.0,
    "historic_placement_rate_12m": 0.0-1.0,
    "historic_avg_salary": 100000-5000000,
    "placement_cell_activity_level": 0.0-1.0,
    "recruiter_participation_score": 0.0-1.0
}
```

### Labor Market Data
```python
{
    "field_job_demand_score": 0.0-1.0,
    "region_job_density": 0.0-1.0,
    "sector_hiring_trend": "IT|BFSI|Manufacturing|Healthcare|Education|Retail|Telecom|Energy|Other",
    "sector_hiring_growth": -1.0 to 1.0,
    "macroeconomic_condition_score": 0.0-1.0
}
```

### Real-Time Signals (Optional)
```python
{
    "job_portal_applications_count": 0+,
    "interview_pipeline_stage": 0-5,
    "resume_updates_count": 0+,
    "skill_up_events_count": 0+,
    "institute_placement_progress": 0.0-1.0
}
```

---

## 📤 Output Data Structure

### Placement Prediction
```python
{
    "probability_3_months": 0.66,      # 0.0-1.0
    "probability_6_months": 0.83,      # 0.0-1.0
    "probability_12_months": 0.92,     # 0.0-1.0
    "predicted_timeline": "Placed within 6 months"
}
```

### Salary Prediction
```python
{
    "expected_salary_min": 454500,
    "expected_salary_max": 555500,
    "expected_salary_avg": 505000,
    "confidence_interval_lower": 425000,
    "confidence_interval_upper": 585000
}
```

### Risk Assessment
```python
{
    "placement_risk_score": 0.36,      # 0.0-1.0
    "risk_level": "Low|Medium|High",
    "risk_factors": [
        "Limited internship exposure",
        "Average field-wise job demand"
    ]
}
```

### Recommendations
```python
{
    "summary": "MEDIUM RISK: This student has...",
    "next_best_actions": [
        "Apply for more internship opportunities",
        "Complete additional certifications"
    ],
    "recruiter_matches": [
        "Tech Mahindra",
        "Infosys",
        "Wipro"
    ]
}
```

---

## 🔧 Configuration (app/core/config.py)

### Prediction Thresholds
```python
PLACEMENT_3M_THRESHOLD = 0.7   # Min probability for 3-month placement
PLACEMENT_6M_THRESHOLD = 0.5   # Min probability for 6-month placement
PLACEMENT_12M_THRESHOLD = 0.3  # Min probability for 12-month placement
```

### Risk Thresholds
```python
HIGH_RISK_THRESHOLD = 0.7      # Score >= 0.7 → High risk
MEDIUM_RISK_THRESHOLD = 0.4    # Score >= 0.4 → Medium risk
                               # Score < 0.4 → Low risk
```

### Salary Bounds
```python
MIN_SALARY = 100000            # Minimum predicted salary
MAX_SALARY = 5000000           # Maximum predicted salary
```

---

## 💻 Python Usage Examples

### Single Prediction
```python
from app.services.prediction_service import PredictionService
from app.services.data_generator import SampleDataGenerator

# Initialize
predictor = PredictionService()
generator = SampleDataGenerator()

# Generate sample student
student = generator.generate_single_student(
    student_id="STU_001",
    risk_profile='medium'
)

# Get prediction
result = predictor.predict_single(student)

# Access results
print(f"Timeline: {result.placement_prediction.predicted_timeline}")
print(f"Risk: {result.risk_assessment.risk_level}")
print(f"Salary: ₹{result.salary_prediction.expected_salary_avg/100000:.2f}L")
```

### Batch Predictions
```python
from app.services.data_generator import SampleDataGenerator

generator = SampleDataGenerator()

# Generate 100 students
students = [
    generator.generate_single_student(student_id=f"STU_{i}")
    for i in range(100)
]

# Batch predict
results = predictor.predict_batch(students)
print(f"Generated {len(results)} predictions")
```

### Custom Student
```python
from app.schemas.prediction import StudentPredictionRequest, StudentAcademicData

student = StudentPredictionRequest(
    student_id="CUSTOM_001",
    academic=StudentAcademicData(
        course_type="Engineering",
        current_year=4,
        semester=8,
        cgpa=8.5,
        academic_consistency=0.85,
        internship_count=3,
        total_internship_duration_months=6.0,
        skill_certifications_count=5,
        relevant_coursework_count=10
    ),
    institute=...,  # Add institute data
    labor_market=...,  # Add market data
    real_time_signals=...  # Optional
)

result = predictor.predict_single(student)
```

---

## 🧪 Testing Commands

```bash
# Test API endpoints
python test_api.py

# Test with different risk profiles
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"student_id": "TEST", ...}'

# Check model info
curl http://localhost:8000/api/v1/model-info

# Health check
curl http://localhost:8000/api/v1/health
```

---

## 📊 Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point |
| `train.py` | Model training pipeline |
| `test_api.py` | API test suite |
| `examples.py` | Comprehensive usage examples |
| `quick_start.py` | Quick demonstration |
| `setup.py` | Setup automation |

| Directory | Contents |
|-----------|----------|
| `app/api/` | API routes |
| `app/core/` | Configuration |
| `app/models/` | ML models |
| `app/schemas/` | Data schemas |
| `app/services/` | Business logic |
| `models/` | Saved model files |
| `data/` | Training data & metrics |

---

## 🎯 Risk Factor Examples

### Academic Risk Factors
- "Low CGPA (<6.5)"
- "Poor academic consistency"

### Internship Risk Factors
- "No internship experience"
- "Limited internship exposure"
- "Short internship duration"

### Institute Risk Factors
- "Tier-3 institute"
- "Weak institute placement record"

### Market Risk Factors
- "Low field-wise job demand"
- "Low regional job opportunities"
- "Declining sector hiring trends"

### Engagement Risk Factors
- "Low job application activity"
- "Early interview pipeline stage"
- "Limited skill development activity"

### Probability Risk Factors
- "Low 3-month placement probability"
- "Low 6-month placement probability"

---

## 🔍 Troubleshooting

### Models Not Loaded
```bash
# Train models first
python train.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### API Won't Start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
python main.py  # Edit main.py to change port
```

### Poor Predictions
```bash
# Retrain with more data
# Edit train.py: n_samples=5000
python train.py
```

---

## 📚 Documentation Files

- `README.md` - Full documentation
- `PROJECT_SUMMARY.md` - Project overview
- `ARCHITECTURE.md` - System architecture
- `QUICK_REFERENCE.md` - This file

---

## 🎓 Common Use Cases

### For Lenders
```python
# Portfolio risk assessment
portfolio = [...]  # List of students
results = predictor.predict_batch(portfolio)

# Calculate portfolio risk
high_risk = sum(1 for r in results if r.risk_assessment.risk_level == "High")
print(f"High risk students: {high_risk}/{len(results)}")
```

### For Institutes
```python
# Identify students needing support
for result in results:
    if result.risk_assessment.risk_level in ["Medium", "High"]:
        print(f"Student {result.student_id} needs support")
        print(f"  Actions: {result.recommendations.next_best_actions}")
```

### For Students
```python
# Self-assessment
result = predictor.predict_single(my_profile)
print(f"My placement timeline: {result.placement_prediction.predicted_timeline}")
print(f"Recommended actions: {result.recommendations.next_best_actions}")
```

---

## ⚡ Performance Tips

1. **Load models once** - Models are cached in PredictionService
2. **Use batch predictions** - More efficient for multiple students
3. **Pre-validate data** - Catch errors before API calls
4. **Monitor memory** - Large batches need more RAM
5. **Use risk-score endpoint** - Lighter than full prediction

---

## 🔐 Best Practices

1. ✅ Validate input data before predictions
2. ✅ Handle errors gracefully
3. ✅ Log predictions for auditing
4. ✅ Monitor model drift over time
5. ✅ Retrain models with real data
6. ✅ Update thresholds based on outcomes
7. ✅ Test with edge cases
8. ✅ Document custom configurations

---

**For full documentation, see README.md**
**For architecture details, see ARCHITECTURE.md**
**For examples, see examples.py**
