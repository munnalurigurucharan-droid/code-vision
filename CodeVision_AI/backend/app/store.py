from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

class ProjectStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.execute('''CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, origin TEXT NOT NULL,
                created_at TEXT NOT NULL, analysis_json TEXT NOT NULL
            )''')
            con.execute('''CREATE TABLE IF NOT EXISTS resolutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT NOT NULL,
                issue TEXT NOT NULL, root_cause TEXT NOT NULL,
                fix TEXT NOT NULL, attempts TEXT NOT NULL, created_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )''')

    def connect(self):
        con = sqlite3.connect(self.db_path, timeout=10)
        con.row_factory = sqlite3.Row
        return con

    def put(self, project: dict[str, Any]) -> None:
        with self.connect() as con:
            con.execute('''INSERT OR REPLACE INTO projects
                (id,title,origin,created_at,analysis_json) VALUES(?,?,?,?,?)''',
                (project['id'], project['title'], project['origin'],
                 datetime.now(timezone.utc).isoformat(), json.dumps(project)))

    def get(self, project_id: str) -> dict[str, Any] | None:
        with self.connect() as con:
            result = con.execute('SELECT analysis_json FROM projects WHERE id=?', (project_id,)).fetchone()
        return json.loads(result['analysis_json']) if result else None

    def list(self) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute('SELECT id,title,origin,created_at FROM projects ORDER BY created_at DESC LIMIT 30').fetchall()
        return [dict(row) for row in rows]

    def log_resolution(self, project_id: str, issue: str, root_cause: str, fix: str, attempts: str) -> None:
        with self.connect() as con:
            con.execute('''INSERT INTO resolutions(project_id,issue,root_cause,fix,attempts,created_at)
                VALUES(?,?,?,?,?,?)''',
                (project_id, issue, root_cause, fix, attempts, datetime.now(timezone.utc).isoformat()))

    def resolutions(self, project_id: str) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute('SELECT issue,root_cause,fix,attempts,created_at FROM resolutions WHERE project_id=? ORDER BY id DESC LIMIT 25', (project_id,)).fetchall()
        return [dict(row) for row in rows]
