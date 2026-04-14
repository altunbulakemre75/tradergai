from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from telegram.constants import ParseMode

from .analyzer import analyze
from .db import get_all_subscribed_users
from .sources.market import get_market_data
from .sources.news import fetch_news

logger = logging.getLogger(__name__)


async def _sabah_bulteni(bot: Bot) -> None:
    logger.info("Sabah bülteni gönderiliyor...")
    users = get_all_subscribed_users()
    if not users:
        return

    for user_id, tickers in users.items():
        lines = ["🌅 *Günaydın! Günlük Bülten*\n"]
        for ticker in tickers[:10]:
            try:
                news, market = await asyncio.gather(
                    asyncio.to_thread(fetch_news, ticker),
                    asyncio.to_thread(get_market_data, ticker),
                )
                if not news:
                    lines.append(f"📊 *{ticker}* — haber yok")
                    continue
                result = await asyncio.to_thread(analyze, ticker, news)
                from .formatter import _EMOJI, _LABEL
                emoji = _EMOJI.get(result.sentiment, "🟡")
                label = _LABEL.get(result.sentiment, "Nötr")
                price_str = ""
                if market and market.price:
                    ch = f" ({market.change_pct:+.1f}%)" if market.change_pct else ""
                    price_str = f" | {market.price:,.2f} {market.currency}{ch}"
                lines.append(f"{emoji} *{ticker}*{price_str} — {label} ({result.score}/100)")
            except Exception:
                logger.exception("Bülten hatası: %s", ticker)

        lines.append("\n_/analiz TICKER ile detay görebilirsin_")
        try:
            await bot.send_message(
                chat_id=user_id,
                text="\n".join(lines),
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            logger.warning("Bülten gönderilemedi: user_id=%s", user_id)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Istanbul")
    scheduler.add_job(
        _sabah_bulteni,
        trigger=CronTrigger(hour=9, minute=0),
        args=[bot],
        id="sabah_bulteni",
        replace_existing=True,
    )
    logger.info("Scheduler kuruldu (sabah bülteni 09:00)")
    return scheduler
