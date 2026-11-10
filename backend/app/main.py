"""
FastAPI Main Application Entrypoint
AI/ML-Powered Mining Safety and Worker Evacuation System
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.database.session import Base, engine, SessionLocal
from backend.app.database.seed_data import seed_database
from backend.app.api import (
    routes_sensors,
    routes_workers,
    routes_zones,
    routes_alerts,
    routes_simulation,
    routes_analytics,
    routes_reports,
    websocket,
)

# Configure Logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mining_safety")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle manager.
    Initializes database tables and runs initial seeding if database is empty.
    """
    logger.info("Initializing Mining Safety System backend...")
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")

    # Run initial seed data if not present
    with SessionLocal() as db:
        seed_database(db)

    yield

    logger.info("Shutting down Mining Safety System backend...")


# Initialize FastAPI Application
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Production-grade backend API and real-time WebSocket orchestration "
        "for the AI/ML-Powered Mining Safety and Worker Evacuation System."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred in the mining safety backend.",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


# Mount API Routers
app.include_router(routes_sensors.router)
app.include_router(routes_workers.router)
app.include_router(routes_zones.router)
app.include_router(routes_alerts.router)
app.include_router(routes_simulation.router)
app.include_router(routes_analytics.router)
app.include_router(routes_reports.router)
app.include_router(websocket.router)


# Configure Frontend Static Assets Directory
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)
assets_path = os.path.join(FRONTEND_DIST, "assets")
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    logger.info(f"Mounted frontend static assets from: {assets_path}")
else:
    logger.warning(f"Frontend static assets not found at: {assets_path}")


@app.get("/api/system/status", tags=["System"])
def system_status():
    """System metadata and operational status."""
    return {
        "status": "online",
        "system": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "mode": "Academic Prototype (Simulated & Threshold-Based Risk Engine)",
        "docs_url": "/docs",
        "websocket_endpoint": "/ws/telemetry",
    }


@app.get("/health", tags=["System"])
@app.get("/api/health", tags=["System"])
def health_check():
    """System health check endpoint verifying database connectivity."""
    db_status = "connected"
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "database_backend": settings.DATABASE_URL.split("://")[0],
        "simulation_enabled": settings.ENABLE_SYNTHETIC_GENERATOR,
    }


@app.get("/", tags=["System"])
def root():
    """Serves the compiled React frontend application or fallback system metadata."""
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(system_status())


@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa_frontend(full_path: str):
    """
    Catch-all route for Single Page Application (SPA) client-side routing.
    Preserves API endpoints and 404s, while routing navigation paths to React index.html.
    """
    if (
        full_path.startswith("api/")
        or full_path == "api"
        or full_path.startswith("ws/")
        or full_path == "ws"
        or full_path.startswith("docs")
        or full_path.startswith("redoc")
        or full_path == "openapi.json"
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"API endpoint /{full_path} not found"},
        )

    # Check if exact static file requested (e.g., vite.svg, favicon.ico)
    static_file = os.path.join(FRONTEND_DIST, full_path)
    if os.path.isfile(static_file):
        return FileResponse(static_file)

    # Return React index.html for client-side routing (e.g., /analytics, /workers, etc.)
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"File or path /{full_path} not found"},
    )
