"""
Точка входа для MCP-сервера LightRAG.
"""

import logging
import os
import sys

from lightrag_mcp import config
from lightrag_mcp.server import mcp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("lightrag-mcp.log"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Основная функция запуска сервера."""
    try:
        # Настройка уровня логирования
        log_level = getattr(logging, "DEBUG")
        logging.getLogger().setLevel(log_level)

        # Настройка переменных окружения для увеличения таймаутов
        os.environ["STARLETTE_KEEP_ALIVE_TIMEOUT"] = str(config.TIMEOUT)
        os.environ["UVICORN_TIMEOUT_KEEP_ALIVE"] = str(config.TIMEOUT)

        # Запуск MCP сервера
        logger.info("Запуск LightRAG MCP сервера")
        logger.info(f"Установлен таймаут: {config.TIMEOUT} секунд")
        logger.info(
            f"Ожидается, что LightRAG API сервер уже запущен и доступен по адресу: {config.LIGHTRAG_API_BASE_URL}"
        )
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Сервер остановлен пользователем")
    except Exception as e:
        logger.exception(f"Ошибка при запуске сервера: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
