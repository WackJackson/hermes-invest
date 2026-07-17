from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from investment_core.models import HoldingRecord, RuleProfile


class Storage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                create table if not exists holdings (
                    symbol text not null,
                    market text not null,
                    name text not null,
                    quantity real not null,
                    avg_cost real not null,
                    currency text not null,
                    account text not null,
                    open_date text not null
                )
                """
            )
            conn.execute(
                """
                create table if not exists settings (
                    key text primary key,
                    value text not null
                )
                """
            )
            conn.commit()

    def replace_holdings(self, records: list[HoldingRecord]) -> int:
        with self._connect() as conn:
            conn.execute("delete from holdings")
            conn.executemany(
                """
                insert into holdings (symbol, market, name, quantity, avg_cost, currency, account, open_date)
                values (:symbol, :market, :name, :quantity, :avg_cost, :currency, :account, :open_date)
                """,
                [record.model_dump() for record in records],
            )
            conn.commit()
        return len(records)

    def list_holdings(self) -> list[HoldingRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "select symbol, market, name, quantity, avg_cost, currency, account, open_date from holdings order by market, symbol"
            ).fetchall()
        return [HoldingRecord(**dict(row)) for row in rows]

    def save_rule_profile(self, profile: RuleProfile) -> RuleProfile:
        with self._connect() as conn:
            conn.execute(
                "replace into settings (key, value) values (?, ?)",
                ("rule_profile", json.dumps(profile.model_dump(), ensure_ascii=True)),
            )
            conn.commit()
        return profile

    def get_rule_profile(self) -> RuleProfile:
        with self._connect() as conn:
            row = conn.execute("select value from settings where key = ?", ("rule_profile",)).fetchone()
        if row is None:
            return RuleProfile()
        return RuleProfile(**json.loads(row["value"]))
