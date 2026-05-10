import feedparser
import logging

logger = logging.getLogger(__name__)

RSS_FEEDS = [
    {"name": "Base Blog",   "url": "https://base.mirror.xyz/feed"},
    {"name": "L2Beat",      "url": "https://l2beat.com/feed.xml"},
    {"name": "Bankless",    "url": "https://bankless.com/feed"},
    {"name": "The Defiant", "url": "https://thedefiant.io/feed"},
]


def fetch_rss() -> list[dict]:
    results = []
    for feed_meta in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_meta["url"])
            for entry in feed.entries[:10]:
                results.append({
                    "source": feed_meta["name"],
                    "name": entry.get("title", "")[:120],
                    "url": entry.get("link", ""),
                    "description": entry.get("summary", "")[:400],
                    "type": "article",
                })
            logger.info(f"RSS {feed_meta['name']}: {len(feed.entries)} entries")
        except Exception as e:
            logger.warning(f"RSS error {feed_meta['name']}: {e}")
    return results
