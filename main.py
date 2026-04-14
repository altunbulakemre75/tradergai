import logging

from src import config
from src.bot import build_application
from src.db import init_db


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    config.validate()
    init_db()

    app = build_application()

    logging.getLogger(__name__).info("TraderGAI başlatıldı.")
    app.run_polling(allowed_updates=None)


if __name__ == "__main__":
    main()

