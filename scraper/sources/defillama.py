import httpx
import logging

logger = logging.getLogger(__name__)


def fetch_defillama() -> list[dict]:
    results = []
    try:
        r = httpx.get("https://api.llama.fi/protocols", timeout=15)
        r.raise_for_status()
        protocols = r.json()
        base_protocols = [p for p in protocols if "Base" in (p.get("chains") or [])]
        base_protocols.sort(key=lambda x: x.get("id", 0), reverse=True)
        for p in base_protocols[:30]:
            results.append({
                "source": "DeFiLlama",
                "name": p.get("name", "")[:120],
                "url": p.get("url") or f"https://defillama.com/protocol/{p.get('slug', '')}",
                "description": p.get("description", "")[:400],
                "type": "protocol",
                "tvl": p.get("tvl", 0),
            })
        logger.info(f"DeFiLlama: {len(results)} Base protocols")
    except Exception as e:
        logger.warning(f"DeFiLlama error: {e}")
    return results
