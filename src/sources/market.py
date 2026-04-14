from __future__ import annotations

import logging
from dataclasses import dataclass

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


def get_market_data(ticker: str) -> MarketData:
    t = ticker.upper()
    if t in CRYPTO_TICKERS:
        return _get_crypto(t)
    return _get_stock(t)


def _get_stock(ticker: str) -> MarketData:
    try:
        import yfinance as yf
        symbol = f"{ticker}.IS"
        info = yf.Ticker(symbol).fast_info
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
        info = yf.Ticker(symbol).fast_info
        price = getattr(info, "last_price", None)
        prev = getattr(info, "previous_close", None)
        change_pct = ((price - prev) / prev * 100) if price and prev else None
        return MarketData(ticker, price, change_pct, None, "USD", True)
    except Exception as e:
        logger.warning("Kripto fiyatı alınamadı %s: %s", ticker, e)
        return MarketData(ticker, None, None, None, "USD", True)
