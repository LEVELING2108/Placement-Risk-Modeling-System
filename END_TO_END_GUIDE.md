# Placement-Risk Modeling System - End-to-End Guide

## 🎯 Complete System Overview

A production-ready, end-to-end AI-powered platform for predicting student placement timelines, estimating salaries, and assessing education-loan repayment risks. Built for lenders, educational institutes, and career counselors.

---

## 🚀 Quick Start

### 1. Start the System
```bash
# Navigate to project directory
cd "C:\Users\suman\Downloads\PERSONAL PROJECT\Placement-Risk Modeling system"

# Models are already trained, just start the server
python main.py
```

### 2. Access the Dashboard
Open your browser and go to:
- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📱 System Features

### 1. **Dashboard** (Main Landing Page)
- Real-time portfolio statistics
- Risk distribution charts
- Placement timeline predictions
- Portfolio health score meter
- Recent predictions table
- Quick navigation to all features

### 2. **Portfolio Management**
- View all analyzed students
- Search and filter students
- Export portfolio to CSV
- Upload batch student data
- Individual student profiles
- Risk score tracking

### 3. **Risk Prediction**
- Detailed student risk assessment form
- Real-time prediction results
- Placement probability breakdown
- Salary estimation with confidence intervals
- AI-generated risk summaries
- Actionable recommendations

### 4. **Batch Analysis**
- Analyze multiple students at once
- Generate random student samples
- Batch risk visualization
- Comparative analysis
- Export batch results

### 5. **Student Profiles**
- Complete student information
- Academic history
- Internship tracking
- Risk factor breakdown
- Recommendation history

### 6. **Analytics**
- Risk by course type
- Risk by institute tier
- Comparative visualizations
- Trend analysis

### 7. **Reports**
- Portfolio risk reports
- CSV data export
- Summary statistics
- Printable reports

---

## 🎨 Dashboard Walkthrough

### Main Dashboard View
When you open http://localhost:8000, you'll see:

1. **Top Navigation Bar**
   - System name and branding
   - "New Prediction" button for quick analysis

2. **Statistics Cards** (4 cards)
   - Total Students Analyzed
   - Low Risk Students (green)
   - Medium Risk Students (yellow)
   - High Risk Students (red)

3. **Charts Section** (4 charts)
   - **Risk Distribution**: Doughnut chart showing risk breakdown
   - **Placement Timeline**: Bar chart of predicted timelines
   - **Average Salary**: Course-wise salary comparison
   - **Portfolio Health**: Visual health meter (0-100%)

4. **Recent Predictions Table**
   - Shows last 10 predictions
   - Student ID, Course, CGPA, Timeline, Salary, Risk Level
   - "View" button for detailed analysis

### How to Make a Prediction

#### Method 1: Quick Prediction (From Dashboard)
1. Click "New Prediction" button
2. Fill in student details:
   - Student ID
   - Course type
   - CGPA
   - Internship count
   - Institute tier
3. Click "Predict"
4. Results saved automatically to portfolio

#### Method 2: Detailed Prediction
1. Navigate to "Predict Risk" in sidebar
2. Fill comprehensive form:
   - **Academic Information**:
     - Course type, year, semester
     - CGPA, academic consistency
     - Internship count and duration
   - **Institute & Market Data**:
     - Institute tier
     - Placement rates
     - Job demand score
     - Sector trends
3. Click "Run Prediction"
4. View detailed results:
   - Placement probabilities (3/6/12 months)
   - Salary estimation
   - Risk score and level
   - Risk factors
   - AI summary
   - Recommendations

#### Method 3: Batch Analysis
1. Navigate to "Batch Analysis"
2. Set number of students (1-100)
3. Click "Run Batch Analysis"
4. System generates random students and analyzes each
5. View:
   - Risk distribution chart
   - Salary distribution chart
   - Detailed results table
   - Add to main portfolio

### Portfolio Management

#### Viewing Portfolio
1. Click "Portfolio" in sidebar
2. See all analyzed students
3. Use search box to find specific students
4. Filter by risk level (Low/Medium/High)

#### Exporting Data
1. Click "Export CSV" button
2. File downloads automatically
3. Contains all student predictions and risk scores

#### Uploading Batch Data
1. Click "Upload Batch" button
2. Prepare CSV with student data
3. Upload and process
4. Review batch predictions

---

## 🔌 API Endpoints Reference

### Prediction Endpoints

#### 1. Single Prediction
```http
POST /api/v1/predict
Content-Type: application/json

{
  "student_id": "STU_001",
  "academic": {
    "course_type": "Engineering",
    "current_year": 4,
    "semester": 8,
    "cgpa": 7.5,
    "academic_consistency": 0.75,
    "internship_count": 2,
    "total_internship_duration_months": 4.0,
    "skill_certifications_count": 3,
    "relevant_coursework_count": 6
  },
  "institute": {
    "institute_tier": "Tier-2",
    "historic_placement_rate_3m": 0.55,
    "historic_placement_rate_6m": 0.75,
    "historic_placement_rate_12m": 0.90,
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
}
```

**Response:**
```json
{
  "student_id": "STU_001",
  "timestamp": "2026-04-14T17:00:00",
  "placement_prediction": {
    "probability_3_months": 0.65,
    "probability_6_months": 0.83,
    "probability_12_months": 0.92,
    "predicted_timeline": "Placed within 6 months"
  },
  "salary_prediction": {
    "expected_salary_min": 450000,
    "expected_salary_max": 550000,
    "expected_salary_avg": 500000,
    "confidence_interval_lower": 420000,
    "confidence_interval_upper": 580000
  },
  "risk_assessment": {
    "placement_risk_score": 0.42,
    "risk_level": "Medium",
    "risk_factors": [
      "Limited internship exposure",
      "Average field-wise job demand"
    ]
  },
  "recommendations": {
    "summary": "MEDIUM RISK: This student has moderate placement prospects...",
    "next_best_actions": [
      "Apply for more internship opportunities",
      "Complete additional certifications",
      "Practice mock interviews"
    ],
    "recruiter_matches": [
      "Tech Mahindra",
      "Infosys",
      "Wipro",
      "TCS",
      "Accenture"
    ]
  },
  "model_version": "1.0.0"
}
```

#### 2. Batch Prediction
```http
POST /api/v1/batch-predict
Content-Type: application/json

{
  "students": [...],
  "max_batch_size": 100
}
```

#### 3. Risk Score Only
```http
POST /api/v1/risk-score
Content-Type: application/json
```

### Portfolio Management Endpoints

#### Get Portfolio
```http
GET /api/v1/portfolio
```

#### Get Student
```http
GET /api/v1/portfolio/{student_id}
```

#### Remove Student
```http
DELETE /api/v1/portfolio/{student_id}
```

#### Portfolio Statistics
```http
GET /api/v1/portfolio/stats
```

**Response:**
```json
{
  "total_students": 50,
  "risk_distribution": {
    "Low": 20,
    "Medium": 22,
    "High": 8
  },
  "average_risk_score": 0.42,
  "average_salary": 525000,
  "timeline_distribution": {
    "Placed within 3 months": 15,
    "Placed within 6 months": 25,
    "Placed within 12 months": 8,
    "High risk of delayed placement": 2
  },
  "portfolio_health_score": 0.58
}
```

#### Export Portfolio
```http
GET /api/v1/portfolio/export
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

### System Endpoints

#### Health Check
```http
GET /api/v1/health
```

#### Model Info
```http
GET /api/v1/model-info
```

---

## 📊 Understanding Predictions

### Placement Timeline
- **3 Months**: High probability of immediate placement
- **6 Months**: Moderate timeline, needs some support
- **12 Months**: Extended timeline, significant support needed
- **Delayed**: High risk, requires intensive intervention

### Risk Levels
- **Low (Score < 0.4)**: Strong placement prospects
- **Medium (Score 0.4-0.7)**: Moderate prospects, room for improvement
- **High (Score > 0.7)**: Significant challenges, needs intervention

### Salary Ranges
Based on:
- Course type and institute tier
- Historic placement data
- Current market conditions
- Student profile strength

---

## 🎓 Use Cases

### For Lenders/Banks

1. **Loan Application Assessment**
   - Assess student's employability before approving loan
   - Make informed lending decisions
   - Set appropriate loan amounts based on salary predictions

2. **Portfolio Risk Monitoring**
   - Monitor all loan recipients' placement prospects
   - Identify at-risk borrowers early
   - Plan supportive interventions

3. **Repayment Planning**
   - Adjust repayment schedules based on predicted timelines
   - Set up grace periods aligned with placement probability
   - Reduce default rates through early intervention

### For Educational Institutes

1. **Placement Cell Optimization**
   - Identify students needing extra support
   - Allocate placement resources effectively
   - Track placement preparation progress

2. **Career Counseling**
   - Provide data-driven guidance to students
   - Suggest skill development areas
   - Set realistic expectations

3. **Program Improvement**
   - Identify weak areas in curriculum
   - Adjust programs based on market demand
   - Improve overall placement rates

### For Students

1. **Self-Assessment**
   - Understand placement prospects
   - Identify areas for improvement
   - Set realistic salary expectations

2. **Career Planning**
   - Get personalized recommendations
   - Focus on high-impact activities
   - Target appropriate recruiters

---

## 🔧 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Web Dashboard                          │
│              (HTML/CSS/JavaScript)                       │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Server                          │
│  • REST API Endpoints                                    │
│  • Portfolio Management                                  │
│  • Analytics & Reports                                   │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│              Prediction Service                          │
│  • Preprocessing → Feature Engineering → Models         │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                  ML Models                               │
│  • Placement: GB + RF + LR Ensemble                     │
│  • Salary: GB + RF + Ridge Ensemble                     │
│  • Risk: Multi-factor scoring system                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Placement-Risk Modeling system/
│
├── static/
│   └── index.html                  # Web dashboard
│
├── app/
│   ├── api/
│   │   └── routes.py               # All API endpoints
│   ├── core/
│   │   └── config.py               # Configuration
│   ├── models/
│   │   ├── placement_model.py      # Placement prediction
│   │   └── salary_model.py         # Salary estimation
│   ├── schemas/
│   │   └── prediction.py           # Data schemas
│   └── services/
│       ├── data_generator.py       # Sample data
│       ├── feature_engineering.py  # Feature creation
│       ├── prediction_service.py   # Main orchestrator
│       ├── preprocessing.py        # Data processing
│       ├── recommendation.py       # AI recommendations
│       └── risk_scoring.py         # Risk assessment
│
├── models/                         # Trained model files
├── data/                           # Training data
├── main.py                         # Application entry
├── train.py                        # Training script
├── requirements.txt                # Dependencies
└── README.md                       # Documentation
```

---

## 💡 Example Workflows

### Workflow 1: Assess New Loan Applicant

1. **Gather Student Information**
   - Collect academic records
   - Get institute placement data
   - Research market conditions

2. **Run Prediction**
   - Navigate to "Predict Risk"
   - Fill in all student details
   - Click "Run Prediction"

3. **Review Results**
   - Check placement timeline
   - Review salary estimate
   - Assess risk level
   - Read AI summary

4. **Make Decision**
   - Low Risk: Approve standard loan
   - Medium Risk: Approve with conditions
   - High Risk: Require collateral or guarantor

5. **Save to Portfolio**
   - Automatically saved for monitoring
   - Track over time

### Workflow 2: Monitor Existing Portfolio

1. **Open Dashboard**
   - View overall statistics
   - Check health score
   - Review risk distribution

2. **Identify At-Risk Students**
   - Filter by "High Risk"
   - Review risk factors
   - Check placement probabilities

3. **Plan Interventions**
   - View recommendations
   - Contact students
   - Offer support programs

4. **Export Report**
   - Click "Export CSV"
   - Share with management
   - Document decisions

### Workflow 3: Batch Analysis for New Batch

1. **Generate Sample**
   - Go to "Batch Analysis"
   - Set student count
   - Run analysis

2. **Review Results**
   - Check risk distribution
   - Identify patterns
   - Compare with previous batches

3. **Take Action**
   - Focus on high-risk students
   - Allocate resources
   - Set up support programs

---

## 🎯 Key Features Checklist

✅ **Predictive Modeling**
- ✅ 3/6/12 month placement prediction
- ✅ Salary estimation with confidence intervals
- ✅ Multi-model ensemble approach
- ✅ Feature engineering (50+ features)

✅ **Risk Assessment**
- ✅ Comprehensive risk scoring (0-1)
- ✅ Risk level classification
- ✅ Risk factor identification
- ✅ Explainable AI decisions

✅ **Recommendations**
- ✅ AI-generated summaries
- ✅ Actionable next steps
- ✅ Recruiter matching
- ✅ Skill development suggestions

✅ **Dashboard**
- ✅ Real-time statistics
- ✅ Interactive charts
- ✅ Portfolio health meter
- ✅ Recent predictions table

✅ **Portfolio Management**
- ✅ Student tracking
- ✅ Search and filter
- ✅ CSV export
- ✅ Individual profiles

✅ **Analytics**
- ✅ Risk by course type
- ✅ Risk by institute tier
- ✅ Comparative visualizations
- ✅ Trend analysis

✅ **API**
- ✅ RESTful endpoints
- ✅ Swagger documentation
- ✅ Batch processing
- ✅ Portfolio management

✅ **Production Ready**
- ✅ Trained models
- ✅ Error handling
- ✅ Input validation
- ✅ Scalable architecture

---

## 📞 Support & Resources

- **Dashboard**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Training Script**: `python train.py`
- **Test Suite**: `python test_api.py`

---

**System Status**: ✅ Fully Operational
**Models**: ✅ Trained and Loaded
**Dashboard**: ✅ Running and Accessible
**API**: ✅ All Endpoints Active

**Ready for Production Use!** 🚀
