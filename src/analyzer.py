from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

import google.generativeai as genai

from .config import GEMINI_API_KEY, GEMINI_MODEL
from .sources.news import NewsItem

logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel(GEMINI_MODEL)


@dataclass
class AnalysisResult:
    sentiment: str          # "pozitif" | "negatif" | "nötr"
    score: int              # 0–100
    keywords: list[str] = field(default_factory=list)
    summary: str = ""
    risk: str = ""          # Kısa risk notu
    opportunity: str = ""   # Fırsat notu
    impact_duration: str = ""   # "kısa" | "orta" | "uzun" vade
    catalyst: str = ""      # Ana katalizör


PROMPT_TEMPLATE = """Sen deneyimli bir Türk finansal analistisin. Aşağıda {ticker} ile ilgili son {hours} saatteki haberler var.

Haberler:
{news_block}

Aşağıdaki JSON formatında Türkçe analiz yap. SADECE JSON döndür, başka hiçbir metin ekleme:
{{
  "sentiment": "pozitif" veya "negatif" veya "nötr",
  "score": 0-100 (sentiment şiddeti),
  "keywords": ["3-5 anahtar kelime"],
  "summary": "2-3 cümle genel değerlendirme",
  "risk": "kısa risk notu (max 1 cümle, yoksa boş string)",
  "opportunity": "kısa fırsat notu (max 1 cümle, yoksa boş string)",
  "impact_duration": "kısa" veya "orta" veya "uzun",
  "catalyst": "ana katalizör (1 cümle)"
}}
"""


def analyze(ticker: str, news: list[NewsItem], hours: int = 24) -> AnalysisResult:
    if not news:
        return AnalysisResult(
            sentiment="nötr", score=0,
            summary="Son dönemde haber bulunamadı.",
        )

    news_block = "\n".join(
        f"- {n.title}: {_clean(n.summary)}" for n in news
    )
    prompt = PROMPT_TEMPLATE.format(ticker=ticker, hours=hours, news_block=news_block)

    try:
        response = _model.generate_content(prompt)
        data = _extract_json(response.text.strip())
        return AnalysisResult(
            sentiment=str(data.get("sentiment", "nötr")).lower(),
            score=int(data.get("score", 0)),
            keywords=list(data.get("keywords", []))[:5],
            summary=str(data.get("summary", "")),
            risk=str(data.get("risk", "")),
            opportunity=str(data.get("opportunity", "")),
            impact_duration=str(data.get("impact_duration", "")),
            catalyst=str(data.get("catalyst", "")),
        )
    except Exception as exc:
        logger.exception("Gemini analizi başarısız: %s", exc)
        return AnalysisResult(
            sentiment="nötr", score=0,
            summary="Analiz sırasında bir hata oluştu.",
        )


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"JSON bulunamadı: {text[:200]}")
    return json.loads(match.group(0))


def _clean(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()[:300]
