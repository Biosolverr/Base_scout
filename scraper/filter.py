import sqlite3
import hashlib
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "data/seen.db")


def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen (
            id TEXT PRIMARY KEY,
            name TEXT,
            url TEXT,
            first_seen TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    return conn


def _make_id(item: dict) -> str:
    raw = item.get("contract") or item.get("url", "") + item.get("name", "")
    return hashlib.sha256(raw.lower().strip().encode()).hexdigest()[:16]


def filter_new(items: list[dict]) -> list[dict]:
    conn = _get_conn()
    new_items = []
    for item in items:
        item_id = _make_id(item)
        row = conn.execute("SELECT id FROM seen WHERE id=?", (item_id,)).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO seen (id, name, url) VALUES (?,?,?)",
                (item_id, item.get("name", ""), item.get("url", "")),
            )
            new_items.append(item)
    conn.commit()
    conn.close()
    logger.info(f"Filter: {len(items)} total → {len(new_items)} new")
    return new_items
