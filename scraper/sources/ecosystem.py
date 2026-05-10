import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


def fetch_ecosystem() -> list[dict]:
    results = []
    headers = {"User-Agent": "Mozilla/5.0 BaseScout/1.0"}
    try:
        r = httpx.get("https://www.base.org/ecosystem", headers=headers, timeout=20, follow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        seen_hrefs = set()
        for card in soup.select("a[href]"):
            href = card.get("href", "")
            text = card.get_text(separator=" ", strip=True)[:200]
            if not href or href in seen_hrefs or not text or len(text) < 5:
                continue
            if href.startswith("/") and len(href) < 15:
                continue
            seen_hrefs.add(href)
            full_url = href if href.startswith("http") else f"https://www.base.org{href}"
            results.append({
                "source": "Base Ecosystem",
                "name": text[:120],
                "url": full_url,
                "description": f"Project on Base ecosystem page: {text}",
                "type": "ecosystem",
            })
        logger.info(f"Ecosystem: {len(results)} items")
    except Exception as e:
        logger.warning(f"Ecosystem error: {e}")
    return results
