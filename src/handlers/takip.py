from __future__ import annotations

import re

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..db import add_ticker, ensure_user, get_watchlist, remove_ticker

TICKER_RE = re.compile(r"^[A-Z0-9]{2,8}$")


async def ekle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    ensure_user(user_id, update.effective_user.username)

    if not context.args:
        await update.message.reply_text("Kullanım: `/ekle THYAO`", parse_mode=ParseMode.MARKDOWN)
        return

    ticker = context.args[0].upper()
    if not TICKER_RE.match(ticker):
        await update.message.reply_text(f"❌ Geçersiz ticker: `{ticker}`", parse_mode=ParseMode.MARKDOWN)
        return

    watchlist = get_watchlist(user_id)
    if len(watchlist) >= 20:
        await update.message.reply_text("⚠️ Maksimum 20 hisse takip edebilirsiniz.")
        return

    if add_ticker(user_id, ticker):
        await update.message.reply_text(f"✅ *{ticker}* takip listene eklendi.", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(f"ℹ️ *{ticker}* zaten takip listende.", parse_mode=ParseMode.MARKDOWN)


async def sil_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("Kullanım: `/sil THYAO`", parse_mode=ParseMode.MARKDOWN)
        return

    ticker = context.args[0].upper()
    if remove_ticker(user_id, ticker):
        await update.message.reply_text(f"🗑️ *{ticker}* takip listenden çıkarıldı.", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(f"ℹ️ *{ticker}* takip listende değildi.", parse_mode=ParseMode.MARKDOWN)


async def listem_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    ensure_user(user_id, update.effective_user.username)
    watchlist = get_watchlist(user_id)

    if not watchlist:
        await update.message.reply_text(
            "📋 Takip listen boş.\n`/ekle THYAO` ile hisse ekle.", parse_mode=ParseMode.MARKDOWN
        )
        return

    tickers_str = " • ".join(f"`{t}`" for t in watchlist)
    await update.message.reply_text(
        f"⭐ *Takip Listem* ({len(watchlist)} hisse)\n\n{tickers_str}\n\n"
        f"`/sil TICKER` ile çıkarabilirsin.",
        parse_mode=ParseMode.MARKDOWN,
    )
