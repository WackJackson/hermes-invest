from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from investment_core.config import get_db_path
from investment_core.routes import analysis_router, hermes_router, holdings_router, rules_router
from investment_core.storage import Storage


def create_app(db_path: str | Path | None = None) -> FastAPI:
    app = FastAPI(
        title="Hermes Investment Core",
        version="0.1.0",
        description="Lightweight investment core service for personal long-term value investing workflows",
    )
    app.state.storage = Storage(Path(db_path) if db_path else get_db_path())

    @app.get("/healthz", tags=["health"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(holdings_router)
    app.include_router(rules_router)
    app.include_router(analysis_router)
    app.include_router(hermes_router)
    return app


app = create_app()
