"""FastAPI application factory for BuyWise AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from buywise.api.routes import router


def create_app() -> FastAPI:
    """Create and configure the BuyWise AI FastAPI application."""
    app = FastAPI(
        title="BuyWise AI - Shopping Intelligence Platform",
        description="Evidence-grounded shopping intelligence platform with deterministic price arithmetic and strict provenance.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Secure Cross-Origin Resource Sharing (CORS) configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app


app = create_app()
