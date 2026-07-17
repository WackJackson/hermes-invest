from __future__ import annotations

from pathlib import Path

from fastapi import Request

from investment_core.storage import Storage


DEFAULT_DB_PATH = Path("data/investment_core.db")


def get_storage(request: Request) -> Storage:
    return request.app.state.storage
