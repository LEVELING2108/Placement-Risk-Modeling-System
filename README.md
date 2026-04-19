# Placement-Risk Modeling System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red.svg)](https://www.sqlalchemy.org/)
[![AI](https://img.shields.io/badge/AI-Gemini%20%7C%20Groq-blueviolet.svg)]()
[![Status](https://img.shields.io/badge/Status-Production--Ready-success.svg)]()

## AI-Powered Predictive Engine for Education-Loan Borrowers

An advanced machine learning system that predicts student placement timelines, estimates starting salaries, and identifies applicants who may face delays affecting their loan repayment ability. **Now upgraded with a Persistent Database, Multi-AI Fallback, and Advanced Explainability.**

---

## 🎯 Key Features (v2.0 Upgraded)

### 1. **Persistent SQLite Database**
- **Data Integrity**: All student records, predictions, and AI roadmaps are securely stored in a persistent SQLite database using **SQLAlchemy ORM**.
- **Real Data Support**: No more in-memory JSON limitations; the system handles thousands of records with high performance.
- **Efficient Analytics**: Dashboard statistics and charts are powered by high-speed SQL aggregations.

### 2. **Multi-AI Career Roadmaps**
- **Personalized Advice**: 4-step actionable roadmaps tailored to the student's specific risk profile.
- **Unlimited Reliability**: Dual-provider system using **Gemini 2.0 Flash** with automatic fallback to **Groq (Llama 3.1)** for 100% uptime and high rate limits.

### 3. **Advanced Explainability (SHAP)**
- **Instance-Level Breakdown**: View exactly why a student received a specific risk score.
- **Visual Contribution Charts**: Interactive bar charts showing exactly which factors (CGPA, Internships, etc.) drove the prediction.

### 4. **Interactive "What-If" Simulator**
- **Scenario Testing**: Lenders can simulate "what-if" improvements (e.g., *What if the student gets 1 more internship?*) to see real-time impact on risk.

### 5. **Live Job Market Integration**
- **Dynamic Demand Scores**: Real-time sector demand and hiring trends fetched via **Adzuna API**.

### 6. **Production Security**
- **JWT Authentication**: Secure login with OAuth2 and JSON Web Tokens.
- **Multi-Tenancy**: Isolated portfolios for different lending institutions (Lender A cannot see Lender B's data).

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Modern UI Dashboard (Vanilla JS)            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│           API Layer (FastAPI + JWT Auth)                │
└─────────────────────────────────────────────────────────┘
              ↓                             ↓
┌───────────────────────────┐    ┌────────────────────────┐
│    Prediction Engine      │    │    Persistence Layer   │
├───────────────────────────┤    ├────────────────────────┤
│ • Scikit-Learn Models     │    │ • SQLite Database      │
│ • SHAP Explainability     │    │ • SQLAlchemy ORM       │
│ • Gemini & Groq AI        │    │ • Multi-Tenant Logic   │
└───────────────────────────┘    └────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/LEVELING2108/Placement-Risk-Modeling-System.git
cd Placement-Risk-Modeling-System

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
ADZUNA_APP_ID=your_adzuna_id
ADZUNA_APP_KEY=your_adzuna_key
```

### 3. Initialize & Start

```bash
# Initialize database and seed users
python init_db.py

# Train models (optional if already trained)
python train.py

# Start the FastAPI server
python main.py
```
**Dashboard:** [http://localhost:8000](http://localhost:8000)  
**Demo Credentials:** `lender_a` / `password123`

---

## 🔌 API Endpoints (v2.0)

| Endpoint | Method | Auth | Description |
| :--- | :--- | :--- | :--- |
| `/api/v1/auth/login` | POST | No | Authenticate and get JWT token |
| `/api/v1/predict` | POST | Yes | Prediction + SHAP + AI Roadmap (Saves to DB) |
| `/api/v1/simulate` | POST | Yes | Interactive "What-If" scenario analysis |
| `/api/v1/portfolio` | GET | Yes | Retrieve current tenant's portfolio from DB |
| `/api/v1/model-info`| GET | No | View Model Registry & performance |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, FastAPI, Pydantic v2
- **Database**: SQLite, SQLAlchemy ORM
- **Machine Learning**: Scikit-learn (Random Forest, Gradient Boosting), SHAP
- **Generative AI**: Google Gemini 2.0 Flash, Groq (Llama 3.1)
- **Data APIs**: Adzuna Jobs API
- **Security**: Bcrypt, Python-Jose (JWT), Passlib
- **Frontend**: HTML5, Bootstrap 5, Chart.js

---

**Built with ❤️ for better lending outcomes and student success**
