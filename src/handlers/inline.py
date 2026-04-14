import uuid
import re
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ContextTypes

from ..sources.market import get_market_data

TICKER_RE = re.compile(r"^[A-Z0-9]{2,8}$")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query.strip().upper()

    if not query or not TICKER_RE.match(query):
        return

    # Hızlı piyasa verisi çek
    market = get_market_data(query)
    
    if market.price:
        change_emoji = "📈" if (market.change_pct or 0) >= 0 else "📉"
        change_str = f" ({market.change_pct:+.2f}%) {change_emoji}" if market.change_pct is not None else ""
        text = f"📊 <b>{query}</b>: {market.price:,.2f} {market.currency}{change_str}\n\n🤖 <i>Detaylı analiz için bota gidip /analiz {query} yazın.</i>"
        title = f"{query} Fiyat: {market.price:,.2f} {market.currency}"
        desc = "Güncel piyasa verisini kolayca sohbete gönderin."
    else:
        text = f"🔎 <b>{query}</b> hissesi ile ilgili analiz yapmak için botu ziyaret edin: @TraderGAIBot"
        title = f"{query} Analizini Paylaş"
        desc = "Bu hissenin detaylı analizi için bota yönlendirir."

    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=title,
            description=desc,
            input_message_content=InputTextMessageContent(
                text,
                parse_mode="HTML"
            ),
        )
    ]

    await update.inline_query.answer(results, cache_time=60)
