from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import mktime
from urllib.parse import quote_plus

import feedparser

from ..cache import get as cache_get, set as cache_set
from ..config import MAX_NEWS_ITEMS, NEWS_LOOKBACK_HOURS

logger = logging.getLogger(__name__)

CRYPTO_TICKERS = {
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE",
    "AVAX", "DOT", "MATIC", "LTC", "LINK", "USDT", "USDC",
}

RSS_SOURCES = [
    "https://news.google.com/rss/search?q={query}&hl=tr&gl=TR&ceid=TR:tr",
]

CRYPTO_NAMES = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "BNB": "Binance",
    "SOL": "Solana", "XRP": "Ripple", "ADA": "Cardano",
    "DOGE": "Dogecoin", "AVAX": "Avalanche",
}


@dataclass
class NewsItem:
    title: str
    link: str
    published: datetime
    summary: str
    source: str = ""


def fetch_news(
    ticker: str,
    hours: int = NEWS_LOOKBACK_HOURS,
    limit: int = MAX_NEWS_ITEMS,
) -> list[NewsItem]:
    cache_key = f"news:{ticker}:{hours}"
    cached = cache_get(cache_key)
    if cached is not None:
        logger.info("Cache hit: news for %s", ticker)
        return cached

    queries = _build_queries(ticker)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    seen: set[str] = set()
    items: list[NewsItem] = []

    for query in queries:
        for url_template in RSS_SOURCES:
            url = url_template.format(query=quote_plus(query))
            try:
                feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0"})
                for entry in feed.entries:
                    published = _parse_published(entry)
                    if published is None or published < cutoff:
                        continue
                    title = getattr(entry, "title", "").strip()
                    key = title.lower()[:80]
                    if not title or key in seen:
                        continue
                    seen.add(key)
                    items.append(NewsItem(
                        title=title,
                        link=getattr(entry, "link", ""),
                        published=published,
                        summary=getattr(entry, "summary", ""),
                        source=feed.feed.get("title", ""),
                    ))
            except Exception as e:
                logger.debug("RSS fetch failed %s: %s", url, e)

        if len(items) >= limit:
            break

    items.sort(key=lambda i: i.published, reverse=True)
    result = items[:limit]
    cache_set(cache_key, result)
    logger.info("Found %d unique news items for %s", len(result), ticker)
    return result


def _build_queries(ticker: str) -> list[str]:
    t = ticker.upper()
    if t in CRYPTO_TICKERS:
        long_name = CRYPTO_NAMES.get(t, t)
        return [f"{t} kripto", f"{long_name}", f"{long_name} fiyat haber"]
    return [f"{t} hisse", f"{t} borsa KAP", f"{t}"]


def _parse_published(entry) -> datetime | None:
    parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if not parsed:
        return None
    return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
