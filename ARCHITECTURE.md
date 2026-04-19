# System Architecture & Data Flow (v2.0)

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       CLIENT LAYER                          │
│     Modern Dashboard (Vanilla JS + Bootstrap + Chart.js)    │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTPS / JWT
┌─────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                     │
│    • Auth: OAuth2 + JWT (Jose)                              │
│    • Routing: Student, Portfolio, Analytics, Auth           │
│    • Validation: Pydantic v2 Models                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 PREDICTION SERVICE (Orchestrator)           │
│                                                             │
│  1. Data Enrichment (Adzuna Job API)                        │
│  2. ML Prediction Pipeline (Placement + Salary)              │
│  3. Explainability Engine (SHAP Values)                      │
│  4. Multi-AI Generation (Gemini → Groq Fallback)            │
│  5. Result Persistence (SQLAlchemy)                         │
└─────────────────────────────────────────────────────────────┘
           ↓                             ↓
┌───────────────────────┐    ┌────────────────────────────────┐
│   MODEL LAYER (SKL)   │    │      PERSISTENCE LAYER         │
├───────────────────────┤    ├────────────────────────────────┤
│ • Placement Ensemble  │    │ • SQLite DB (Local Storage)    │
│ • Salary Ensemble     │    │ • SQLAlchemy ORM               │
│ • SHAP Explainer      │    │ • Multi-Tenant Data Isolation  │
└───────────────────────┘    └────────────────────────────────┘
```

---

## Enhanced Data Flow

### 1. Security & Context
Every request is authenticated via **JWT**. The system extracts the `tenant_id` from the token, ensuring that database queries for Portfolios and Analytics are strictly scoped to that specific lender.

### 2. Intelligent Roadmaps (Multi-AI)
The recommendation engine uses a priority-based logic to ensure 100% roadmap availability:
1.  **Primary**: Calls **Gemini 2.0 Flash** for deep reasoning.
2.  **Fallback**: If Gemini hits a rate limit (429), it automatically fails over to **Groq (Llama 3.1)**.
3.  **Static**: Final fallback uses rule-based templates if all APIs are offline.

### 3. Database Schema
The system uses a relational model for high-performance data retrieval:
-   **Users**: Hashed credentials and tenant assignments.
-   **StudentProfiles**: Denormalized academic and market features.
-   **PredictionResults**: Linked results containing scores, SHAP values, and roadmaps.
-   **ModelRegistry**: Tracking model version history and accuracy metrics.

---

## Risk Scoring Methodology

Risk is calculated using a weighted combination of five distinct risk categories plus the model-predicted placement probability:

```
Risk Score = Σ (Category_Score × Weight) + Placement_Probability_Risk × 0.30
```

1.  **Academic Risk (20%)**: Based on CGPA and academic consistency.
2.  **Internship Risk (25%)**: Based on count, duration, and performance.
3.  **Institute Risk (20%)**: Based on tier, placement history, and recruiter activity.
4.  **Market Risk (20%)**: Dynamic score enriched by live **Adzuna API** data.
5.  **Engagement Risk (15%)**: Real-time student activity signals.

---

## Model Training & Registry
The training pipeline (`train.py`) generates synthetic data, trains ensemble models, and validates accuracy. Results are saved both as `.pkl` objects and a record in the `ModelRegistry` database table, allowing the UI to show exactly which model is currently serving predictions.
