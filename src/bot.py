import logging

from telegram import Update, BotCommand
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    InlineQueryHandler,
    ContextTypes,
)

from .config import TELEGRAM_BOT_TOKEN
from .db import add_ticker, ensure_user
from .handlers.analiz import analiz_cmd
from .handlers.kap import kap_cmd
from .handlers.takip import ekle_cmd, listem_cmd, sil_cmd
from .handlers.top import top_cmd
from .handlers.inline import inline_query

logger = logging.getLogger(__name__)

WELCOME = (
    "<b>👋 TraderGAI'ye Hoş Geldin!</b>\n\n"
    "BIST hisseleri ve Kripto paralar için haber bazlı yapay zeka analizi yapıyorum.\n\n"
    "📊 <code>/analiz THYAO</code> — Detaylı sentiment raporu\n"
    "🏛️ <code>/kap THYAO</code> — Son KAP bildirimleri\n"
    "⭐ <code>/ekle THYAO</code> — Takip listesine ekle\n"
    "📋 <code>/listem</code> — Takip listeni gör\n"
    "🏆 <code>/top</code> — Popüler hisseler\n"
    "❓ <code>/help</code> — Yardım"
)

HELP = (
    "<b>🛠️ Kullanılabilir Komutlar:</b>\n\n"
    "/analiz &lt;HİSSE&gt; — Sentiment ve teknik analiz\n"
    "/kap &lt;HİSSE&gt; — Son resmi bildirimler\n"
    "/ekle &lt;HİSSE&gt; — Listeye ekle\n"
    "/sil &lt;HİSSE&gt; — Listeden çıkar\n"
    "/listem — Takip listeniz\n"
    "/top — Günün öne çıkanları\n\n"
    "<i>İpucu: Sadece @bot_adı THYAO yazarak diğer sohbetlerde de hızlı fiyat paylaşabilirsiniz.</i>"
)


async def start_cmd(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    ensure_user(update.effective_user.id, update.effective_user.username)
    await update.message.reply_html(WELCOME)


async def help_cmd(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(HELP)


async def post_init(application: Application) -> None:
    """Bot başlatıldığında yapılacak ayarlar."""
    commands = [
        BotCommand("analiz", "Sentiment analizi yap"),
        BotCommand("kap", "KAP bildirimlerini gör"),
        BotCommand("listem", "Takip listem"),
        BotCommand("top", "Popüler hisseler"),
        BotCommand("help", "Yardım al"),
    ]
    await application.bot.set_my_commands(commands)
    
    # Scheduler'ı burada başlatıyoruz
    from .scheduler import setup_scheduler
    scheduler = setup_scheduler(application.bot)
    scheduler.start()



async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    if data.startswith("ekle:"):
        ticker = data.split(":", 1)[1]
        user_id = update.effective_user.id
        ensure_user(user_id, update.effective_user.username)
        if add_ticker(user_id, ticker):
            await query.message.reply_html(f"✅ <b>{ticker}</b> takip listene eklendi.")
        else:
            await query.message.reply_html(f"ℹ️ <b>{ticker}</b> zaten takip listende.")

    elif data.startswith("kap:"):
        ticker = data.split(":", 1)[1]
        context.args = [ticker]
        await kap_cmd(update, context)


def build_application() -> Application:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("analiz", analiz_cmd))
    app.add_handler(CommandHandler("kap", kap_cmd))
    app.add_handler(CommandHandler("ekle", ekle_cmd))
    app.add_handler(CommandHandler("sil", sil_cmd))
    app.add_handler(CommandHandler("listem", listem_cmd))
    app.add_handler(CommandHandler("top", top_cmd))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CallbackQueryHandler(callback_handler))
    return app

