import asyncio, hashlib, json, logging, os
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from scraper.sources.rss import fetch_rss
from scraper.sources.blockscout import fetch_blockscout
from scraper.sources.defillama import fetch_defillama
from scraper.sources.ecosystem import fetch_ecosystem
from scraper.filter import filter_new
from scraper.llm import analyze_batch
from api.db import get_client, init_db

async def save_projects(projects):
    async with get_client() as client:
        await init_db(client)
        for p in projects:
            pid = hashlib.sha256((p.get("url","") + p.get("name","")).encode()).hexdigest()[:16]
            await client.execute("""
                INSERT OR REPLACE INTO projects
                (id, name, url, source, narrative, score, tags, summary, why_interesting, type)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, [
                pid, p.get("name","")[:200], p.get("url",""),
                p.get("source",""), p.get("narrative","other"),
                int(p.get("score",1)), json.dumps(p.get("tags",[])),
                p.get("summary",""), p.get("why_interesting",""), p.get("type",""),
            ])
    logger.info(f"Saved {len(projects)} projects")

async def run():
    logger.info("=== Base Scout scraper started ===")
    all_items = fetch_rss() + fetch_blockscout() + fetch_defillama() + fetch_ecosystem()
    logger.info(f"Total collected: {len(all_items)}")
    new_items = filter_new(all_items)
    if not new_items:
        logger.info("No new items, done.")
        return
    enriched = analyze_batch(new_items)
    await save_projects(enriched)
    logger.info(f"=== Done: {len(enriched)} new projects added ===")

if __name__ == "__main__":
    asyncio.run(run())
