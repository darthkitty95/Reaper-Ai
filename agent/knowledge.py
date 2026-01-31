import sqlite3
import json
import hashlib
from pathlib import Path

class KnowledgeStore:
    def __init__(self, db_path="./agent_data/knowledge.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._ensure_table()

    def _ensure_table(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS examples (
            id TEXT PRIMARY KEY,
            diagnostic TEXT,
            patch TEXT,
            metadata TEXT
        )
        """)
        self.conn.commit()

    def add_example(self, diagnostic, patch, metadata=None):
        cur = self.conn.cursor()
        diag_json = json.dumps(diagnostic.to_dict() if hasattr(diagnostic, "to_dict") else diagnostic)
        mid = hashlib.sha256((diag_json + patch).encode("utf-8")).hexdigest()
        cur.execute("INSERT OR IGNORE INTO examples(id, diagnostic, patch, metadata) VALUES (?, ?, ?, ?)",
                    (mid, diag_json, patch, json.dumps(metadata or {})))
        self.conn.commit()

    def find_similar(self, diagnostic):
        cur = self.conn.cursor()
        target = diagnostic.message if hasattr(diagnostic, "message") else str(diagnostic)
        cur.execute("SELECT id, diagnostic, patch, metadata FROM examples")
        for _id, diag_json, patch, metadata in cur.fetchall():
            if target in diag_json:
                return {"id": _id, "diagnostic": json.loads(diag_json), "patch": patch, "metadata": json.loads(metadata)}
        return None
