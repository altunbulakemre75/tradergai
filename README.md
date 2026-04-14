# TraderGAI

BIST hisseleri için haber bazlı sentiment analizi yapan Telegram botu.

## Aşama 1 MVP Özellikleri

- `/analiz <HİSSE>` → Son 24 saatteki haberleri Google News RSS'ten çeker, Gemini ile sentiment analizi yapar, özet döner.
- `/start`, `/help` komutları.

## Kurulum (Windows)

```bash
cd noname
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Yapılandırma

`.env.example`'ı `.env` olarak kopyalayın ve token'ları doldurun:

```
TELEGRAM_BOT_TOKEN=...
GEMINI_API_KEY=...
```

- Telegram token: [@BotFather](https://t.me/BotFather) → `/newbot`
- Gemini key: https://aistudio.google.com/app/apikey

## Çalıştırma

```bash
python main.py
```

Telegram'da botunuza `/start` yazarak deneyin.

## Güvenlik Uyarısı

Token'lar `.env` içinde kalır, repoya girmez (`.gitignore`). Token sızdığında:

- Telegram: BotFather → `/revoke`
- Gemini: AI Studio'da anahtarı silip yenisini oluşturun.

## Sonraki Aşamalar

- **Aşama 2:** KAP + kripto + sabah bülteni
- **Aşama 3:** Kullanıcı yönetimi + alarmlar
- **Aşama 4:** Ödeme + Pro paketi
