from __future__ import annotations

import asyncio

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..analyzer import analyze
from ..sources.news import fetch_news

BIST_TOP = ["THYAO", "ASELS", "EREGL", "BIMAS", "AKBNK", "GARAN", "SISE", "KCHOL", "TUPRS", "FROTO"]


async def top_cmd(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    progress = await update.message.reply_text(
        "📊 BIST hisseleri analiz ediliyor... (bu birkaç dakika sürebilir)",
    )

    results = []
    for ticker in BIST_TOP:
        try:
            news = await asyncio.to_thread(fetch_news, ticker)
            if not news:
                continue
            result = await asyncio.to_thread(analyze, ticker, news)
            results.append((ticker, result))
            await asyncio.sleep(1)  # rate limit
        except Exception:
            pass

    if not results:
        await progress.edit_text("⚠️ Analiz yapılamadı.")
        return

    results.sort(key=lambda x: x[1].score * (1 if x[1].sentiment == "pozitif" else -1), reverse=True)

    from ..formatter import _EMOJI
    lines = ["📊 *Bugünün BIST Özeti*\n"]
    lines.append("*🟢 En Pozitif:*")
    pos = [(t, r) for t, r in results if r.sentiment == "pozitif"][:3]
    for t, r in pos:
        lines.append(f"  {_EMOJI['pozitif']} *{t}* — {r.score}/100")

    lines.append("\n*🔴 En Negatif:*")
    neg = [(t, r) for t, r in results if r.sentiment == "negatif"][:3]
    for t, r in neg:
        lines.append(f"  {_EMOJI['negatif']} *{t}* — {r.score}/100")

    await progress.edit_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)
