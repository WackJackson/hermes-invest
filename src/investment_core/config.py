from __future__ import annotations

import os
from pathlib import Path


def get_db_path() -> Path:
    return Path(os.getenv("INVEST_DB_PATH", "data/investment_core.db"))


def get_root_path() -> str:
    return os.getenv("APP_ROOT_PATH", "")
