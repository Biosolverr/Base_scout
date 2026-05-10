import os
import libsql_client

def get_client():
    return libsql_client.create_client_sync(
        url=os.environ["TURSO_URL"],
        auth_token=os.environ["TURSO_TOKEN"],
    )

async def get_async_client():
    return libsql_client.create_client(
        url=os.environ["TURSO_URL"],
        auth_token=os.environ["TURSO_TOKEN"],
    )

async def init_db(client):
    await client.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT,
            url TEXT,
            source TEXT,
            narrative TEXT,
            score INTEGER,
            tags TEXT,
            summary TEXT,
            why_interesting TEXT,
            type TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
