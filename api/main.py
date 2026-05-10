import os
import json
import sqlite3
import logging
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

logging.basicConfig(level=logging.INFO)
DB_PATH = os.getenv("DB_PATH", "data/seen.db")

app = FastAPI(title="Base Scout API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row) -> dict:
    d = dict(row)
    try:
        d["tags"] = json.loads(d.get("tags") or "[]")
    except Exception:
        d["tags"] = []
    return d


@app.get("/")
def root():
    return {"name": "Base Scout API", "status": "ok"}


@app.get("/projects")
def get_projects(
    narrative: Optional[str] = Query(None),
    min_score: int = Query(1, ge=1, le=5),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    conn = get_conn()
    query = "SELECT * FROM projects WHERE score >= ?"
    params: list = [min_score]
    if narrative and narrative != "all":
        query += " AND narrative = ?"
        params.append(narrative)
    query += " ORDER BY score DESC, created_at DESC LIMIT ? OFFSET ?"
    params += [limit, offset]
    try:
        rows = conn.execute(query, params).fetchall()
        return {"projects": [row_to_dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        return {"projects": [], "count": 0, "error": str(e)}
    finally:
        conn.close()


@app.get("/narratives")
def get_narratives():
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT narrative, COUNT(*) as count, AVG(score) as avg_score FROM projects GROUP BY narrative ORDER BY count DESC"
        ).fetchall()
        return {"narratives": [dict(r) for r in rows]}
    except Exception:
        return {"narratives": []}
    finally:
        conn.close()


@app.get("/stats")
def get_stats():
    conn = get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        top = conn.execute("SELECT * FROM projects ORDER BY score DESC LIMIT 5").fetchall()
        latest = conn.execute("SELECT * FROM projects ORDER BY created_at DESC LIMIT 5").fetchall()
        return {
            "total_projects": total,
            "top_projects": [row_to_dict(r) for r in top],
            "latest_projects": [row_to_dict(r) for r in latest],
        }
    except Exception as e:
        return {"total_projects": 0, "error": str(e)}
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
