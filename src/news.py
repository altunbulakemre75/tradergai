from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import mktime
from urllib.parse import quote_plus

import feedparser

from .config import MAX_NEWS_ITEMS, NEWS_LOOKBACK_HOURS

logger = logging.getLogger(__name__)

RSS_URL = "https://news.google.com/rss/search?q={query}&hl=tr&gl=TR&ceid=TR:tr"

CRYPTO_TICKERS = {"BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "DOT", "MATIC", "LTC", "LINK", "USDT", "USDC"}


@dataclass
class NewsItem:
    title: str
    link: str
    published: datetime
    summary: str


def fetch_news(
    ticker: str,
    hours: int = NEWS_LOOKBACK_HOURS,
    limit: int = MAX_NEWS_ITEMS,
) -> list[NewsItem]:
    queries = _build_queries(ticker)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    seen_titles: set[str] = set()
    items: list[NewsItem] = []

    for query in queries:
        url = RSS_URL.format(query=quote_plus(query))
        logger.info("Fetching news: %s", url)
        feed = feedparser.parse(url)

        for entry in feed.entries:
            published = _parse_published(entry)
            if published is None or published < cutoff:
                continue
            title = getattr(entry, "title", "").strip()
            key = title.lower()
            if not title or key in seen_titles:
                continue
            seen_titles.add(key)
            items.append(
                NewsItem(
                    title=title,
                    link=getattr(entry, "link", ""),
                    published=published,
                    summary=getattr(entry, "summary", ""),
                )
            )
            if len(items) >= limit:
                break
        if len(items) >= limit:
            break

    items.sort(key=lambda i: i.published, reverse=True)
    logger.info("Found %d unique news items for %s", len(items), ticker)
    return items


def _build_queries(ticker: str) -> list[str]:
    t = ticker.upper()
    if t in CRYPTO_TICKERS:
        names = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "BNB": "Binance Coin",
            "SOL": "Solana",
            "XRP": "Ripple",
            "ADA": "Cardano",
            "DOGE": "Dogecoin",
            "AVAX": "Avalanche",
        }
        long_name = names.get(t, t)
        return [
            f"{t} kripto",
            f"{long_name} fiyat",
            f"{long_name} haber",
            t,
        ]
    return [
        f"{t} hisse",
        f"{t} borsa",
        f"{t} KAP",
        t,
    ]


def _parse_published(entry) -> datetime | None:
    parsed = getattr(entry, "published_parsed", None) or getattr(
        entry, "updated_parsed", None
    )
    if parsed is None:
        return None
    return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
