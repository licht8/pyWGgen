#!/usr/bin/env python3
# test_logging.py
# Скрипт для проверки уровня логирования

import logging
from settings import LOG_LEVEL, LOG_FILE_PATH

# Настраиваем logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

def test_logging():
    """Тестирует уровни логирования."""
    logger.debug("Это сообщение DEBUG. Оно не должно отображаться при LOG_LEVEL=WARNING.")
    logger.info("Это сообщение INFO. Оно не должно отображаться при LOG_LEVEL=WARNING.")
    logger.warning("Это сообщение WARNING. Оно должно отображаться при LOG_LEVEL=WARNING.")
    logger.error("Это сообщение ERROR. Оно должно отображаться при любом уровне логирования.")

if __name__ == "__main__":
    print(f"Проверка уровня логирования: {LOG_LEVEL}")
    test_logging()
