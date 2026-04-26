"""
PolyMind Backend — FastAPI Entry Point.
Κεντρικό σημείο εκκίνησης του API server.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import app_config
from core.database import init_db
from routers import parent, child, language


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Αρχικοποίηση βάσης δεδομένων κατά την εκκίνηση."""
    await init_db()
    yield


# Δημιουργία FastAPI instance
app = FastAPI(
    title=app_config.app_name,
    version=app_config.version,
    lifespan=lifespan,
)

# CORS middleware — επιτρέπει επικοινωνία frontend ↔ backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Σύνδεση routers
app.include_router(parent.router)
app.include_router(child.router)
app.include_router(language.router)


@app.get("/")
async def root() -> dict:
    """Health check endpoint."""
    return {
        "app": app_config.app_name,
        "version": app_config.version,
        "status": "running",
    }
