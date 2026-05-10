import os, json, logging
import libsql_client
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from api.db import init_db

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Base Scout API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

def make_client():
    return libsql_client.create_client(
        url=os.environ["TURSO_URL"],
        auth_token=os.environ["TURSO_TOKEN"],
    )

@app.get("/")
def root():
    return {"name": "Base Scout API", "version": "1.0.0", "status": "ok"}

@app.get("/projects")
async def get_projects(
    narrative: Optional[str] = Query(None),
    min_score: int = Query(1, ge=1, le=5),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    async with make_client() as client:
        await init_db(client)
        query = "SELECT * FROM projects WHERE score >= ?"
        params = [min_score]
        if narrative and narrative != "all":
            query += " AND narrative = ?"
            params.append(narrative)
        query += " ORDER BY score DESC, created_at DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        rs = await client.execute(query, params)
        projects = []
        for row in rs.rows:
            d = dict(zip([c.name for c in rs.columns], row))
            d["tags"] = json.loads(d.get("tags") or "[]")
            projects.append(d)
        return {"projects": projects, "count": len(projects)}

@app.get("/narratives")
async def get_narratives():
    async with make_client() as client:
        await init_db(client)
        rs = await client.execute(
            "SELECT narrative, COUNT(*) as count, AVG(score) as avg_score "
            "FROM projects GROUP BY narrative ORDER BY count DESC"
        )
        return {"narratives": [dict(zip([c.name for c in rs.columns], row)) for row in rs.rows]}

@app.get("/stats")
async def get_stats():
    async with make_client() as client:
        await init_db(client)
        total = (await client.execute("SELECT COUNT(*) FROM projects")).rows[0][0]
        top_rs = await client.execute("SELECT * FROM projects ORDER BY score DESC LIMIT 5")
        latest_rs = await client.execute("SELECT * FROM projects ORDER BY created_at DESC LIMIT 5")
        def to_list(rs):
            return [dict(zip([c.name for c in rs.columns], row)) for row in rs.rows]
        return {"total_projects": total, "top_projects": to_list(top_rs), "latest_projects": to_list(latest_rs)}
