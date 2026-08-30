"""
NetSage AI — FastAPI Main Application
Serves both the REST API and the static frontend.
"""

import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from backend.database import init_db
from backend.seed import seed_database
from backend.routers import cases, diagnosis, reviews, dashboard

# Create FastAPI app
app = FastAPI(
    title="NetSage AI",
    description="AI-Assisted Network Troubleshooting Platform for Cisco Packet Tracer Labs",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(cases.router)
app.include_router(diagnosis.router)
app.include_router(reviews.router)
app.include_router(dashboard.router)

# Mount static files
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed data on startup."""
    await init_db()
    await seed_database()
    print("\n" + "=" * 60)
    print("  NetSage AI — Network Troubleshooting Platform")
    print("  http://localhost:8000")
    print("=" * 60 + "\n")


@app.get("/")
async def serve_frontend():
    """Serve the main frontend page."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "NetSage AI API is running. Frontend not found."}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from ai.diagnosis.engine import get_engine
    engine = get_engine()
    return {
        "status": "healthy",
        "demo_mode": engine.is_demo_mode,
        "version": "1.0.0"
    }
