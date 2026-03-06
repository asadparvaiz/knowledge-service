from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("data/tenants.db")


class TenantStore:
    def __init__(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self):
        return sqlite3.connect(DB_PATH)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                  tenant_id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def create_tenant(self, tenant_id: str, name: str) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            try:
                conn.execute(
                    "INSERT INTO tenants (tenant_id, name, created_at) VALUES (?, ?, ?)",
                    (tenant_id, name, now),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                raise ValueError(f"tenant '{tenant_id}' already exists")
        return {"tenant_id": tenant_id, "name": name, "created_at": now}

    def tenant_exists(self, tenant_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT tenant_id FROM tenants WHERE tenant_id = ?", (tenant_id,)).fetchone()
        return row is not None
