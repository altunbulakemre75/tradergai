from __future__ import annotations

import asyncio
import re

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..sources.kap import fetch_kap

TICKER_RE = re.compile(r"^[A-Z0-9]{2,8}$")


async def kap_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Kullanım: `/kap THYAO`", parse_mode=ParseMode.MARKDOWN)
        return

    ticker = context.args[0].upper()
    if not TICKER_RE.match(ticker):
        await update.message.reply_text(f"❌ Geçersiz ticker: `{ticker}`", parse_mode=ParseMode.MARKDOWN)
        return

    progress = await update.message.reply_text(f"🏛️ *{ticker}* KAP bildirimleri alınıyor...", parse_mode=ParseMode.MARKDOWN)

    try:
        items = await asyncio.to_thread(fetch_kap, ticker)

        if not items:
            await progress.edit_text(
                f"📋 *{ticker}* için son 48 saatte KAP bildirimi bulunamadı.",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        lines = [f"🏛️ *{ticker}* — Son KAP Bildirimleri\n"]
        for i, item in enumerate(items[:5], 1):
            date_str = item.published.strftime("%d.%m %H:%M")
            title = item.title[:80] + ("…" if len(item.title) > 80 else "")
            lines.append(f"{i}\\. [{title}]({item.link}) _{date_str}_")

        await progress.edit_text(
            "\n".join(lines),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    except Exception:
        import logging
        logging.getLogger(__name__).exception("KAP hatası: %s", ticker)
        await progress.edit_text("⚠️ KAP verileri alınamadı.")
