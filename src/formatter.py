from __future__ import annotations
from .analyzer import AnalysisResult
from .sources.market import MarketData

_EMOJI = {"pozitif": "🟢", "negatif": "🔴", "nötr": "🟡"}
_LABEL = {"pozitif": "Pozitif", "negatif": "Negatif", "nötr": "Nötr"}

def get_sentiment_bar(score: int) -> str:
    """Üretilen skor için görsel bir bar oluşturur."""
    length = 10
    filled = int(round(score / 100 * length))
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {score}%"

def format_analysis(ticker: str, result: AnalysisResult, news_count: int, market: MarketData | None = None) -> str:
    emoji = _EMOJI.get(result.sentiment, "🟡")
    label = _LABEL.get(result.sentiment, "Nötr")
    bar = get_sentiment_bar(result.score)

    lines = [
        f"📊 <b>{ticker} Analiz Raporu</b>",
        f"━━━━━━━━━━━━━━",
    ]

    # Piyasa Verisi (Eğer varsa)
    if market and market.price:
        change_emoji = "📈" if (market.change_pct or 0) >= 0 else "📉"
        change_str = f" ({market.change_pct:+.2f}%) {change_emoji}" if market.change_pct is not None else ""
        lines.append(f"💰 <b>Fiyat:</b> {market.price:,.2f} {market.currency}{change_str}")

    lines.extend([
        f"🎭 <b>Duygu Durumu:</b> {emoji} {label}",
        f"📈 <b>Skor:</b> <code>{bar}</code>",
        f"📰 <b>Haber Sayısı:</b> {news_count}",
        f"━━━━━━━━━━━━━━",
    ])

    if result.summary:
        lines.append(f"📝 <b>Özet:</b>\n<i>{result.summary}</i>\n")

    if result.keywords:
        kw = " • ".join(result.keywords)
        lines.append(f"🔑 <b>Anahtar Kelimeler:</b>\n<code>{kw}</code>\n")

    if result.risk:
        lines.append(f"⚠️ <b>Risk Notu:</b> {result.risk}")
    
    if result.opportunity:
        lines.append(f"💡 <b>Fırsat Notu:</b> {result.opportunity}")

    if result.impact_duration:
        lines.append(f"⏳ <b>Etki Vadesi:</b> {result.impact_duration.capitalize()}")

    if result.catalyst:
        lines.append(f"⚡ <b>Ana Katalizör:</b> {result.catalyst}")

    return "\n".join(lines)


def format_no_news(ticker: str) -> str:
    return (
        f"📊 <b>{ticker}</b>\n\n"
        f"❌ Son 24 saatte ilgili haber bulunamadı.\n"
        f"Lütfen başka bir hisse deneyin."
    )


def format_invalid_ticker(raw: str) -> str:
    return (
        f"❌ <b>Geçersiz kod:</b> <code>{raw}</code>\n"
        f"Örnek: <code>/analiz THYAO</code>"
    )


def format_usage() -> str:
    return "ℹ️ <b>Kullanım:</b> <code>/analiz THYAO</code>"
