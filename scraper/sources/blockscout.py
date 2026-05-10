import httpx
import logging

logger = logging.getLogger(__name__)

BASE_BLOCKSCOUT = "https://base.blockscout.com/api/v2"


def fetch_blockscout() -> list[dict]:
    results = []
    try:
        r = httpx.get(
            f"{BASE_BLOCKSCOUT}/smart-contracts",
            params={"filter": "verified", "sort": "inserted_at", "order": "desc"},
            timeout=15,
        )
        r.raise_for_status()
        contracts = r.json().get("items", [])[:20]
        for c in contracts:
            name = c.get("name") or c.get("address", {}).get("hash", "")
            addr = c.get("address", {}).get("hash", "")
            results.append({
                "source": "Blockscout",
                "name": name[:120],
                "url": f"https://base.blockscout.com/address/{addr}",
                "description": f"Verified contract on Base. Address: {addr}",
                "contract": addr,
                "type": "contract",
            })
        logger.info(f"Blockscout: {len(results)} contracts")
    except Exception as e:
        logger.warning(f"Blockscout error: {e}")
    return results
