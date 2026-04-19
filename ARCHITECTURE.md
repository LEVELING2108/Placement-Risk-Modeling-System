# System Architecture & Data Flow

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Web App  │  │ Dashboard│  │ Lender   │  │ Institute│           │
│  │          │  │          │  │ Portal   │  │ Portal   │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                            │
│                                                                     │
│  POST /api/v1/predict          → Single student prediction         │
│  POST /api/v1/batch-predict    → Batch predictions                 │
│  POST /api/v1/risk-score       → Risk assessment only              │
│  GET  /api/v1/model-info       → Model information                 │
│  GET  /api/v1/health           → Health check                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   PREDICTION SERVICE (Orchestrator)                 │
│                                                                     │
│  1. Receive request                                                  │
│  2. Preprocess data                                                  │
│  3. Engineer features                                                │
│  4. Run placement model                                              │
│  5. Run salary model                                                 │
│  6. Calculate risk score                                             │
│  7. Generate recommendations                                         │
│  8. Format response                                                  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                                  │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Preprocessor │→ │ Feature      │→ │ ML Models    │             │
│  │              │  │ Engineering  │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                             ↓                       │
│                                    ┌──────────────┐                │
│                                    │ Risk Scoring │                │
│                                    └──────────────┘                │
│                                             ↓                       │
│                                    ┌──────────────┐                │
│                                    │ Recommend    │                │
│                                    │ Engine       │                │
│                                    └──────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      MODEL LAYER                                    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  Placement Prediction Model (Ensemble)                  │       │
│  │  • Gradient Boosting (50% weight)                       │       │
│  │  • Random Forest (30% weight)                           │       │
│  │  • Logistic Regression (20% weight)                     │       │
│  │                                                          │       │
│  │  Output: 3/6/12 month placement probabilities           │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  Salary Estimation Model (Ensemble)                     │       │
│  │  • Gradient Boosting (50% weight)                       │       │
│  │  • Random Forest (30% weight)                           │       │
│  │  • Ridge Regression (20% weight)                        │       │
│  │                                                          │       │
│  │  Output: Salary range with confidence intervals         │       │
│  └─────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Single Prediction

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: INPUT                                                │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│  StudentPredictionRequest                                    │
│  ├─ student_id: "STU_001"                                   │
│  ├─ academic: StudentAcademicData                           │
│  │   ├─ course_type: "Engineering"                          │
│  │   ├─ cgpa: 7.5                                           │
│  │   ├─ internship_count: 2                                 │
│  │   └─ ...                                                 │
│  ├─ institute: InstituteData                                │
│  │   ├─ institute_tier: "Tier-2"                            │
│  │   ├─ historic_placement_rate_3m: 0.55                   │
│  │   └─ ...                                                 │
│  ├─ labor_market: LaborMarketData                           │
│  │   ├─ field_job_demand_score: 0.7                         │
│  │   ├─ sector_hiring_trend: "IT"                           │
│  │   └─ ...                                                 │
│  └─ real_time_signals: RealTimeSignals (optional)           │
│      ├─ job_portal_applications_count: 20                   │
│      ├─ interview_pipeline_stage: 3                         │
│      └─ ...                                                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: PREPROCESSING                                        │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│  • Flatten nested structure                                  │
│  • Handle missing values                                     │
│  • Encode categoricals:                                      │
│    - course_type → course_type_encoded                       │
│    - institute_tier → institute_tier_encoded                 │
│    - sector_hiring_trend → sector_hiring_trend_encoded       │
│  • Create derived features:                                  │
│    - internship_quality_score                                │
│    - academic_strength                                       │
│    - institute_placement_strength                            │
│    - market_opportunity_score                                │
│    - student_engagement_score                                │
│                                                              │
│  Output: DataFrame with ~15 encoded features                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: FEATURE ENGINEERING                                  │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│  • Interaction features:                                     │
│    - academic_institute_interaction                          │
│    - internship_market_interaction                           │
│    - engagement_market_interaction                           │
│    - cgpa_internship_interaction                             │
│                                                              │
│  • Polynomial features:                                      │
│    - cgpa_squared                                            │
│    - internship_quality_score_squared                        │
│    - academic_strength_squared                               │
│    - market_opportunity_score_squared                        │
│                                                              │
│  • Binned features:                                          │
│    - cgpa_category                                           │
│    - internship_level                                        │
│                                                              │
│  • Temporal features:                                        │
│    - study_progress                                          │
│    - years_to_graduation                                     │
│    - is_final_year                                           │
│                                                              │
│  • Ratio features:                                           │
│    - certification_coursework_ratio                          │
│    - application_interview_ratio                             │
│    - academic_market_alignment                               │
│                                                              │
│  Output: DataFrame with ~35 features                         │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 4: PLACEMENT PREDICTION                                 │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│  ┌─────────────────────────────────────────────┐            │
│  │ Model 1: Gradient Boosting                  │            │
│  │ P(3m) = 0.68, P(6m) = 0.85, P(12m) = 0.94 │            │
│  └─────────────────────────────────────────────┘            │
│                          +                                   │
│  ┌─────────────────────────────────────────────┐            │
│  │ Model 2: Random Forest                      │            │
│  │ P(3m) = 0.65, P(6m) = 0.82, P(12m) = 0.92 │            │
│  └─────────────────────────────────────────────┘            │
│                          +                                   │
│  ┌─────────────────────────────────────────────┐            │
│  │ Model 3: Logistic Regression                │            │
│  │ P(3m) = 0.62, P(6m) = 0.79, P(12m) = 0.90 │            │
│  └─────────────────────────────────────────────┘            │
│                          ↓                                   │
│              Weighted Average                                │
│              (0.5, 0.3, 0.2)                                 │
│                          ↓                                   │
│  Final: P(3m) = 0.66, P(6m) = 0.83, P(12m) = 0.92          │
│                                                              │
│  Timeline Classification:                                    │
│  • P(3m) >= 0.70 → "Placed within 3 months"                 │
│  • P(6m) >= 0.50 → "Placed within 6 months" ← MATCH         │
│  • P(12m) >= 0.30 → "Placed within 12 months"               │
│  • Else → "High risk of delayed placement"                  │
│                                                              │
│  Output: PlacementPrediction                                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 5: SALARY PREDICTION                                    │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│  ┌──────────────────────────────────────────┐               │
│  │ Model 1: Gradient Boosting               │               │
│  │ Salary = ₹520,000                        │               │
│  └──────────────────────────────────────────┘               │
│                          +                                   │
│  ┌──────────────────────────────────────────┐               │
│  │ Model 2: Random Forest                   │               │
│  │ Salary = ₹495,000                        │               │
│  └──────────────────────────────────────────┘               │
│                          +                                   │
│  ┌──────────────────────────────────────────┐               │
│  │ Model 3: Ridge Regression                │               │
│  │ Salary = ₹480,000                        │               │
│  └──────────────────────────────────────────┘               │
│                          ↓                                   │
│              Weighted Average                                │
│              Salary = ₹505,000                               │
│                          ↓                                   │
│  Confidence Interval (±1.96σ):                               │
│  • Lower: ₹425,000                                           │
│  • Upper: ₹585,000                                           │
│                                                              │
│  Salary Range (±10%):                                        │
│  • Min: ₹454,500                                             │
│  • Max: ₹555,500                                             │
│  • Avg: ₹505,000                                             │
│                                                              │
│  Output: SalaryPrediction                                    │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 6: RISK SCORING                                         │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│  Risk Categories (weighted):                                 │
│  ├─ Academic Risk (20%)                                      │
│  │   └─ Based on CGPA, consistency                           │
│  ├─ Internship Risk (25%)                                    │
│  │   └─ Based on count, duration, performance                │
│  ├─ Institute Risk (20%)                                     │
│  │   └─ Based on tier, placement rate, recruiter activity    │
│  ├─ Market Risk (20%)                                        │
│  │   └─ Based on demand, density, growth, macro              │
│  └─ Engagement Risk (15%)                                    │
│      └─ Based on applications, interviews, skills            │
│                          ↓                                   │
│              Weighted Sum + Placement Risk (30%)             │
│                          ↓                                   │
│  Final Risk Score: 0.42 (on 0-1 scale)                       │
│                                                              │
│  Risk Level Classification:                                  │
│  • Score >= 0.70 → HIGH                                      │
│  • Score >= 0.40 → MEDIUM ← MATCH                            │
│  • Score < 0.40 → LOW                                        │
│                                                              │
│  Risk Factor Identification (top 3-5):                       │
│  1. "Limited internship exposure"                            │
│  2. "Average field-wise job demand"                          │
│  3. "Moderate job application activity"                      │
│                                                              │
│  Output: RiskAssessment                                      │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 7: RECOMMENDATION GENERATION                            │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│  AI Summary Generation:                                      │
│  ┌────────────────────────────────────────────────┐         │
│  │ "MEDIUM RISK: This student has moderate        │         │
│  │ placement prospects with room for improvement. │         │
│  │ Key concerns: Limited internship exposure,     │         │
│  │ Average field-wise job demand. Expected        │         │
│  │ placement within 6 months (83% probability).   │         │
│  │ Expected starting salary: ₹5.05 Lakhs."        │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  Next-Best Actions (based on risk factors):                  │
│  1. "Apply for more internship opportunities"                │
│  2. "Complete additional certifications"                     │
│  3. "Practice mock interviews"                               │
│  4. "Increase job application frequency"                     │
│  5. "Target companies aligned with skills"                   │
│                                                              │
│  Recruiter Matches (based on course type):                   │
│  1. "Tech Mahindra"                                          │
│  2. "Infosys"                                                │
│  3. "Wipro"                                                  │
│  4. "TCS"                                                    │
│  5. "Accenture"                                              │
│                                                              │
│  Output: Recommendation                                      │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STEP 8: RESPONSE FORMATTING                                  │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│  StudentPredictionResponse                                   │
│  ├─ student_id: "STU_001"                                   │
│  ├─ timestamp: "2026-04-14T10:30:00"                        │
│  ├─ placement_prediction: PlacementPrediction               │
│  ├─ salary_prediction: SalaryPrediction                     │
│  ├─ risk_assessment: RiskAssessment                         │
│  ├─ recommendations: Recommendation                         │
│  ├─ model_version: "1.0.0"                                  │
│  └─ explainability_scores: {                                │
│       "internship_quality_score": 0.18,                     │
│       "institute_placement_strength": 0.15,                 │
│       "cgpa": 0.12,                                         │
│       "market_opportunity_score": 0.11,                     │
│       ...                                                   │
│     }                                                        │
└──────────────────────────────────────────────────────────────┘
```

---

## Model Training Pipeline

```
┌────────────────────────────────────────────────────────────┐
│ STEP 1: DATA GENERATION                                    │
│ ────────────────────────────────────────────────────────── │
│                                                            │
│  SampleDataGenerator creates synthetic data:               │
│  • 2,000 student records                                   │
│  • Varied risk profiles (40% low, 35% medium, 25% high)   │
│  • Realistic correlations                                  │
│  • Outcome labels (placed_3m, placed_6m, placed_12m)      │
│  • Actual salary values                                    │
│                                                            │
│  Output: training_data.csv                                 │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│ STEP 2: FEATURE PREPARATION                                │
│ ────────────────────────────────────────────────────────── │
│                                                            │
│  For each training sample:                                 │
│  1. Preprocess raw data                                    │
│  2. Encode categoricals                                    │
│  3. Create derived features                                │
│  4. Engineer advanced features                             │
│                                                            │
│  Output: X (features), y (targets)                         │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│ STEP 3: TRAIN-TEST SPLIT                                   │
│ ────────────────────────────────────────────────────────── │
│                                                            │
│  • Training set: 80% (1,600 samples)                       │
│  • Test set: 20% (400 samples)                             │
│  • Stratified split (maintains risk distribution)          │
│                                                            │
│  Output: X_train, X_test, y_train, y_test                  │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│ STEP 4: MODEL TRAINING                                     │
│ ────────────────────────────────────────────────────────── │
│                                                            │
│  Placement Models (3 timelines × 3 models = 9 models):    │
│  ├─ 3-Month:                                              │
│  │   ├─ Gradient Boosting → fit(X_train, y_3m)           │
│  │   ├─ Random Forest → fit(X_train, y_3m)               │
│  │   └─ Logistic Regression → fit(X_train, y_3m)         │
│  ├─ 6-Month:                                              │
│  │   ├─ Gradient Boosting → fit(X_train, y_6m)           │
│  │   ├─ Random Forest → fit(X_train, y_6m)               │
│  │   └─ Logistic Regression → fit(X_train, y_6m)         │
│  └─ 12-Month:                                             │
│      ├─ Gradient Boosting → fit(X_train, y_12m)          │
│      ├─ Random Forest → fit(X_train, y_12m)              │
│      └─ Logistic Regression → fit(X_train, y_12m)        │
│                                                            │
│  Salary Model (3 models):                                 │
│  ├─ Gradient Boosting → fit(X_train, y_salary)           │
│  ├─ Random Forest → fit(X_train, y_salary)               │
│  └─ Ridge Regression → fit(X_train, y_salary)            │
│                                                            │
│  Output: 12 trained models                               │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│ STEP 5: MODEL EVALUATION                                   │
│ ────────────────────────────────────────────────────────── │
│                                                            │
│  Placement Metrics:                                        │
│  • Accuracy, Precision, Recall, F1                         │
│  • ROC-AUC                                                 │
│  • Confusion Matrix                                        │
│  • Cross-validation scores                                 │
│                                                            │
│  Salary Metrics:                                           │
│  • RMSE, MAE                                               │
│  • R² Score                                                │
│  • MAPE                                                    │
│                                                            │
│  Output: training_metrics.json                             │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│ STEP 6: MODEL PERSISTENCE                                  │
│ ────────────────────────────────────────────────────────── │
│                                                            │
│  Save to disk:                                             │
│  • models/placement_model.pkl (all 9 placement models)    │
│  • models/salary_model.pkl (all 3 salary models)          │
│                                                            │
│  Includes:                                                 │
│  • Trained model objects                                   │
│  • Model weights                                           │
│  • Feature names                                           │
│  • Training metadata                                       │
│                                                            │
│  Output: Saved model files                                 │
└────────────────────────────────────────────────────────────┘
```

---

## Risk Scoring Methodology

```
┌─────────────────────────────────────────────────────────────┐
│                    RISK CALCULATION                          │
└─────────────────────────────────────────────────────────────┘

Risk Score = Σ (Category_Score × Category_Weight) + Placement_Risk × 0.30

Where:

┌────────────────────────────────────────────────────────────────┐
│ Category 1: Academic Risk (Weight: 20%)                        │
├────────────────────────────────────────────────────────────────┤
│ • CGPA Risk (60%): (10 - CGPA) / 10                           │
│ • Consistency Risk (40%): 1 - academic_consistency             │
│                                                                  │
│ Example: CGPA=7.5, Consistency=0.75                           │
│ → CGPA Risk = (10-7.5)/10 = 0.25                              │
│ → Consistency Risk = 1-0.75 = 0.25                            │
│ → Academic Risk = 0.25×0.6 + 0.25×0.4 = 0.25                  │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Category 2: Internship Risk (Weight: 25%)                      │
├────────────────────────────────────────────────────────────────┤
│ • Count Risk (40%): 0 internships=1.0, 1=0.6, 2+=0.2          │
│ • Duration Risk (30%): max(0, 1 - duration/6)                  │
│ • Performance Risk (30%): 1 - performance_score                │
│                                                                  │
│ Example: 2 internships, 5 months, perf=0.85                   │
│ → Count Risk = 0.2                                            │
│ → Duration Risk = 1 - 5/6 = 0.17                              │
│ → Performance Risk = 1 - 0.85 = 0.15                          │
│ → Internship Risk = 0.2×0.4 + 0.17×0.3 + 0.15×0.3 = 0.18     │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Category 3: Institute Risk (Weight: 20%)                       │
├────────────────────────────────────────────────────────────────┤
│ • Tier Risk (40%): tier_encoded / 2                            │
│ • Placement Rate Risk (35%): 1 - placement_rate_3m             │
│ • Recruiter Risk (25%): 1 - recruiter_participation            │
│                                                                  │
│ Example: Tier-2, 55% placement, 0.65 recruiter                │
│ → Tier Risk = 1/2 = 0.5                                       │
│ → Placement Risk = 1 - 0.55 = 0.45                            │
│ → Recruiter Risk = 1 - 0.65 = 0.35                            │
│ → Institute Risk = 0.5×0.4 + 0.45×0.35 + 0.35×0.25 = 0.44    │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Category 4: Market Risk (Weight: 20%)                          │
├────────────────────────────────────────────────────────────────┤
│ • Demand Risk (35%): 1 - field_job_demand                      │
│ • Density Risk (25%): 1 - region_job_density                   │
│ • Growth Risk (20%): (1 - hiring_growth) / 2                   │
│ • Macro Risk (20%): 1 - macroeconomic_condition                │
│                                                                  │
│ Example: demand=0.7, density=0.6, growth=0.15, macro=0.75     │
│ → Demand Risk = 0.3                                           │
│ → Density Risk = 0.4                                          │
│ → Growth Risk = (1-0.15)/2 = 0.425                            │
│ → Macro Risk = 0.25                                           │
│ → Market Risk = 0.3×0.35 + 0.4×0.25 + 0.425×0.2 + 0.25×0.2  │
│              = 0.33                                           │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Category 5: Engagement Risk (Weight: 15%)                      │
├────────────────────────────────────────────────────────────────┤
│ • Application Risk (40%): <5 apps=0.8, <15=0.4, 15+=0.2       │
│ • Interview Risk (40%): 1 - stage/5                            │
│ • Skill Risk (20%): max(0, 1 - skills/5)                       │
│                                                                  │
│ Example: 20 apps, stage=3, 4 skills                           │
│ → Application Risk = 0.2                                      │
│ → Interview Risk = 1 - 3/5 = 0.4                              │
│ → Skill Risk = 1 - 4/5 = 0.2                                  │
│ → Engagement Risk = 0.2×0.4 + 0.4×0.4 + 0.2×0.2 = 0.28       │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ Category 6: Placement Probability Risk (Weight: 30%)           │
├────────────────────────────────────────────────────────────────┤
│ • 3-Month Risk (50%): 1 - P(3m)                                │
│ • 6-Month Risk (30%): 1 - P(6m)                                │
│ • 12-Month Risk (20%): 1 - P(12m)                              │
│                                                                  │
│ Example: P(3m)=0.66, P(6m)=0.83, P(12m)=0.92                  │
│ → Placement Risk = 0.34×0.5 + 0.17×0.3 + 0.08×0.2 = 0.24     │
└────────────────────────────────────────────────────────────────┘

FINAL CALCULATION:
─────────────────────────────────────────────────────────────────
Risk Score = 0.25×0.20 + 0.18×0.25 + 0.44×0.20 + 0.33×0.20 
             + 0.28×0.15 + 0.24×0.30
           
           = 0.05 + 0.045 + 0.088 + 0.066 + 0.042 + 0.072
           
           = 0.363

Risk Level: MEDIUM (0.40 <= 0.363 < 0.70)
─────────────────────────────────────────────────────────────────
```

---

## API Request/Response Flow

```
CLIENT REQUEST
────────────────────────────────────────────────────────────────
POST /api/v1/predict
Content-Type: application/json

{
  "student_id": "STU_001",
  "academic": { ... },
  "institute": { ... },
  "labor_market": { ... },
  "real_time_signals": { ... }
}
────────────────────────────────────────────────────────────────
                    ↓
API VALIDATION (Pydantic)
────────────────────────────────────────────────────────────────
✓ Validate all required fields
✓ Check data types and ranges
✓ Convert enums
✓ Set defaults for optional fields
────────────────────────────────────────────────────────────────
                    ↓
PREDICTION SERVICE
────────────────────────────────────────────────────────────────
1. Convert request to dictionary
2. Preprocess data
3. Engineer features
4. Load models (if not loaded)
5. Run placement prediction
6. Run salary prediction
7. Calculate risk score
8. Generate recommendations
9. Format response
────────────────────────────────────────────────────────────────
                    ↓
CLIENT RESPONSE
────────────────────────────────────────────────────────────────
HTTP 200 OK
Content-Type: application/json

{
  "student_id": "STU_001",
  "timestamp": "2026-04-14T10:30:00",
  "placement_prediction": {
    "probability_3_months": 0.66,
    "probability_6_months": 0.83,
    "probability_12_months": 0.92,
    "predicted_timeline": "Placed within 6 months"
  },
  "salary_prediction": {
    "expected_salary_min": 454500,
    "expected_salary_max": 555500,
    "expected_salary_avg": 505000,
    "confidence_interval_lower": 425000,
    "confidence_interval_upper": 585000
  },
  "risk_assessment": {
    "placement_risk_score": 0.36,
    "risk_level": "Medium",
    "risk_factors": [
      "Limited internship exposure",
      "Average field-wise job demand"
    ]
  },
  "recommendations": {
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
  },
  "model_version": "1.0.0",
  "explainability_scores": {
    "internship_quality_score": 0.18,
    "institute_placement_strength": 0.15
  }
}
────────────────────────────────────────────────────────────────
```

---

This architecture ensures:
✅ **Modularity** - Each component is independent
✅ **Scalability** - Easy to add models or features
✅ **Explainability** - Transparent decision process
✅ **Robustness** - Handles errors gracefully
✅ **Performance** - Optimized for production use
