from __future__ import annotations

import asyncio
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode, ChatAction
from telegram.ext import ContextTypes

from .. import formatter
from ..analyzer import analyze
from ..chart_generator import generate_gauge
from ..db import ensure_user
from ..sources.market import get_market_data
from ..sources.news import fetch_news

TICKER_RE = re.compile(r"^[A-Z0-9]{2,8}$")


async def analiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ensure_user(update.effective_user.id, update.effective_user.username)

    if not context.args:
        await update.message.reply_html(formatter.format_usage())
        return

    tickers = [a.upper() for a in context.args if TICKER_RE.match(a.upper())]
    invalid = [a for a in context.args if not TICKER_RE.match(a.upper())]

    if invalid:
        await update.message.reply_html(formatter.format_invalid_ticker(", ".join(invalid)))
        return

    if not tickers:
        await update.message.reply_html(formatter.format_usage())
        return

    for ticker in tickers[:3]:  # max 3 ticker aynı anda
        await _run_single(update, ticker)


async def _run_single(update: Update, ticker: str) -> None:
    # "Yazıyor..." animasyonu simüle et
    await update.message.chat.send_action(ChatAction.TYPING)
    progress = await update.message.reply_html(f"🔎 <b>{ticker}</b> için veriler toplanıyor ve analiz ediliyor...")

    try:
        news, market = await asyncio.gather(
            asyncio.to_thread(fetch_news, ticker),
            asyncio.to_thread(get_market_data, ticker),
        )

        if not news:
            await progress.edit_text(
                formatter.format_no_news(ticker), parse_mode=ParseMode.HTML
            )
            return

        # "Fotoğraf yükleniyor..." animasyonu
        await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
        
        result = await asyncio.to_thread(analyze, ticker, news)
        
        # Grafik üretimi
        gauge_buf = await asyncio.to_thread(generate_gauge, result.score, f"{ticker} Sentiment")
        
        message = formatter.format_analysis(ticker, result, len(news), market)

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⭐ Takibe Al", callback_data=f"ekle:{ticker}"),
                InlineKeyboardButton("📰 Haber Kaynağı", url=f"https://www.google.com/search?q={ticker}+hisse+haber&tbm=nws"),
            ],
            [
                InlineKeyboardButton("📋 Son KAP Bildirimleri", callback_data=f"kap:{ticker}")
            ]
        ])

        # Önceki yükleniyor mesajını silip görseli gönderiyoruz
        await progress.delete()
        await update.message.reply_photo(
            photo=gauge_buf,
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
        
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Analiz hatası: %s", ticker)
        await progress.edit_text("⚠️ Bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
