from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

COINGECKO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
    "SOL": "solana", "XRP": "ripple", "ADA": "cardano",
    "DOGE": "dogecoin", "AVAX": "avalanche-2", "DOT": "polkadot",
    "MATIC": "matic-network", "LTC": "litecoin", "LINK": "chainlink",
}


@dataclass
class CryptoData:
    ticker: str
    price_usd: float
    change_24h: float
    market_cap: float
    volume_24h: float


def get_crypto_data(ticker: str) -> CryptoData | None:
    coin_id = COINGECKO_IDS.get(ticker.upper())
    if not coin_id:
        return None
    try:
        from pycoingecko import CoinGeckoAPI
        cg = CoinGeckoAPI()
        data = cg.get_price(
            ids=coin_id,
            vs_currencies="usd",
            include_24hr_change=True,
            include_market_cap=True,
            include_24hr_vol=True,
        )
        info = data.get(coin_id, {})
        return CryptoData(
            ticker=ticker.upper(),
            price_usd=info.get("usd", 0),
            change_24h=info.get("usd_24h_change", 0),
            market_cap=info.get("usd_market_cap", 0),
            volume_24h=info.get("usd_24h_vol", 0),
        )
    except Exception as e:
        logger.warning("CoinGecko veri alınamadı %s: %s", ticker, e)
        return None
