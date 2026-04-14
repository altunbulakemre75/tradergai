from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import mktime
from urllib.parse import quote_plus

import feedparser

logger = logging.getLogger(__name__)

KAP_RSS = "https://www.kap.org.tr/tr/rss/sirket-haberleri/{ticker}"
KAP_SEARCH = "https://www.kap.org.tr/tr/Ara?text={query}"


@dataclass
class KapItem:
    title: str
    link: str
    published: datetime
    summary: str


def fetch_kap(ticker: str, hours: int = 48) -> list[KapItem]:
    urls = [
        KAP_RSS.format(ticker=ticker.upper()),
        f"https://www.kap.org.tr/rss/bildirim-ara?text={quote_plus(ticker)}",
    ]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    items: list[KapItem] = []

    for url in urls:
        try:
            feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0"})
            for entry in feed.entries:
                parsed = getattr(entry, "published_parsed", None)
                if not parsed:
                    continue
                pub = datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
                if pub < cutoff:
                    continue
                items.append(KapItem(
                    title=getattr(entry, "title", "").strip(),
                    link=getattr(entry, "link", ""),
                    published=pub,
                    summary=getattr(entry, "summary", ""),
                ))
        except Exception as e:
            logger.debug("KAP fetch failed %s: %s", url, e)

    items.sort(key=lambda i: i.published, reverse=True)
    return items[:10]
