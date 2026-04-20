"""
Placement-Risk Modeling System
AI-Powered Predictive Engine for Education-Loan Borrowers
"""

import time
import traceback
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.api.routes import router
from app.api.auth import router as auth_router
from app.core.config import settings
from app.core.logging import setup_logging, logger
from prometheus_fastapi_instrumentator import Instrumentator
import os

# Initialize logging
setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered placement-risk modeling system for education-loan borrowers",
    version=settings.APP_VERSION
)

# Initialize Prometheus Instrumentator
Instrumentator().instrument(app).expose(app)

# Middleware for request logging and error handling
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        logger.info(
            "request_processed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=f"{duration:.4f}s",
            client_ip=request.client.host if request.client else "unknown"
        )
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            traceback=traceback.format_exc(),
            duration=f"{duration:.4f}s"
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e)}
        )

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def startup_event():
    """Check if models are trained on startup"""
    missing_models = []
    if not os.path.exists(settings.PLACEMENT_MODEL_PATH):
        missing_models.append("Placement Model")
    if not os.path.exists(settings.SALARY_MODEL_PATH):
        missing_models.append("Salary Model")
        
    if missing_models:
        logger.warning(
            "MODELS_NOT_FOUND", 
            message=f"Missing: {', '.join(missing_models)}. Please run 'python train.py' to train the models.",
            path=settings.MODEL_DIR
        )
    else:
        logger.info("MODELS_READY", message="All prediction models loaded successfully.")

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
        "dashboard": "/static/index.html"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("server_starting", host="0.0.0.0", port=8000)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
