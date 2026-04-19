"""
Placement-Risk Modeling System
AI-Powered Predictive Engine for Education-Loan Borrowers
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
from app.api.auth import router as auth_router
from app.core.config import settings
import os

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered placement-risk modeling system for education-loan borrowers",
    version=settings.APP_VERSION
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/")
async def root():
    """Serve the main dashboard"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Placement-Risk Modeling System API",
        "version": settings.APP_VERSION,
        "dashboard": "/static/index.html",
        "endpoints": [
            "/api/v1/predict",
            "/api/v1/batch-predict",
            "/api/v1/risk-score",
            "/api/v1/model-info"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("PLACEMENT-RISK MODELING SYSTEM")
    print("="*60)
    print("\nDashboard: http://localhost:8000")
    print("API Docs:  http://localhost:8000/docs")
    print("\n" + "="*60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
