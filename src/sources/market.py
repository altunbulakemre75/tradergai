from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from ..cache import get as cache_get, set as cache_set

logger = logging.getLogger(__name__)

CRYPTO_TICKERS = {
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE",
    "AVAX", "DOT", "MATIC", "LTC", "LINK",
}


@dataclass
class MarketData:
    ticker: str
    price: float | None
    change_pct: float | None
    volume: float | None
    currency: str
    is_crypto: bool
    history_df: Any = None # pandas DataFrame for history


def get_market_data(ticker: str) -> MarketData:
    t = ticker.upper()
    cached = cache_get(f"market:{t}")
    if cached is not None:
        logger.info("Cache hit: market for %s", t)
        return cached
    result = _get_crypto(t) if t in CRYPTO_TICKERS else _get_stock(t)
    cache_set(f"market:{t}", result)
    return result


def _get_stock(ticker: str) -> MarketData:
    try:
        import yfinance as yf
        symbol = f"{ticker}.IS"
        ticker_obj = yf.Ticker(symbol)
        
        info = ticker_obj.fast_info
        price = getattr(info, "last_price", None)
        prev = getattr(info, "previous_close", None)
        change_pct = ((price - prev) / prev * 100) if price and prev else None
        volume = getattr(info, "three_month_average_volume", None)
        return MarketData(ticker, price, change_pct, volume, "TL", False)
    except Exception as e:
        logger.warning("Hisse fiyatı alınamadı %s: %s", ticker, e)
        return MarketData(ticker, None, None, None, "TL", False)


def _get_crypto(ticker: str) -> MarketData:
    try:
        import yfinance as yf
        symbol = f"{ticker}-USD"
        ticker_obj = yf.Ticker(symbol)
        
        info = ticker_obj.fast_info
        price = getattr(info, "last_price", None)
        prev = getattr(info, "previous_close", None)
        change_pct = ((price - prev) / prev * 100) if price and prev else None
        return MarketData(ticker, price, change_pct, None, "USD", True)
    except Exception as e:
        logger.warning("Kripto fiyatı alınamadı %s: %s", ticker, e)
        return MarketData(ticker, None, None, None, "USD", True)

