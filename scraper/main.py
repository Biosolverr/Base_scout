import logging
import json
import os
import sqlite3
import hashlib

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "data/seen.db")

from sources.rss import fetch_rss
from sources.blockscout import fetch_blockscout
from sources.defillama import fetch_defillama
from sources.ecosystem import fetch_ecosystem
from filter import filter_new
from llm import analyze_batch


def save_projects(projects: list[dict]):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT, url TEXT, source TEXT,
            narrative TEXT, score INTEGER, tags TEXT,
            summary TEXT, why_interesting TEXT, type TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    for p in projects:
        pid = hashlib.sha256((p.get("url","") + p.get("name","")).encode()).hexdigest()[:16]
        conn.execute("""
            INSERT OR REPLACE INTO projects
            (id, name, url, source, narrative, score, tags, summary, why_interesting, type)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            pid,
            p.get("name","")[:200], p.get("url",""), p.get("source",""),
            p.get("narrative","other"), int(p.get("score",1)),
            json.dumps(p.get("tags",[])),
            p.get("summary",""), p.get("why_interesting",""), p.get("type",""),
        ))
    conn.commit()
    conn.close()
    logger.info(f"Saved {len(projects)} projects")


def run():
    logger.info("=== Base Scout scraper started ===")
    all_items = []
    all_items += fetch_rss()
    all_items += fetch_blockscout()
    all_items += fetch_defillama()
    all_items += fetch_ecosystem()
    logger.info(f"Total collected: {len(all_items)}")
    new_items = filter_new(all_items)
    if not new_items:
        logger.info("No new items.")
        return
    enriched = analyze_batch(new_items)
    save_projects(enriched)
    logger.info(f"=== Done: {len(enriched)} new projects ===")


if __name__ == "__main__":
    run()
