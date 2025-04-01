"""
Точка входа для MCP-сервера LightRAG.
"""

import argparse
import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("lightrag-mcp.log")
    ]
)
logger = logging.getLogger(__name__)

# Импорт после настройки логирования
from lightrag_mcp.server import mcp
from lightrag_mcp import config


def parse_args() -> Dict[str, Any]:
    """
    Разбор аргументов командной строки.
    
    Returns:
        Dict[str, Any]: Словарь с аргументами
    """
    parser = argparse.ArgumentParser(description="LightRAG MCP Server")
    parser.add_argument(
        "--host", 
        type=str, 
        default=config.SERVER_HOST,
        help=f"Хост для прослушивания (по умолчанию: {config.SERVER_HOST})"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=config.SERVER_PORT,
        help=f"Порт для прослушивания (по умолчанию: {config.SERVER_PORT})"
    )
    parser.add_argument(
        "--lightrag-autostart", 
        action="store_true", 
        default=config.LIGHTRAG_AUTOSTART,
        help="Автоматически запускать LightRAG API сервер"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Уровень логирования"
    )
    
    return vars(parser.parse_args())


def main():
    """Основная функция запуска сервера."""
    try:
        # Разбор аргументов командной строки
        args = parse_args()
        
        # Обновление настроек на основе аргументов
        config.SERVER_HOST = args["host"]
        config.SERVER_PORT = args["port"]
        config.LIGHTRAG_AUTOSTART = args["lightrag_autostart"]
        
        # Настройка уровня логирования
        log_level = getattr(logging, args["log_level"])
        logging.getLogger().setLevel(log_level)
        
        # Создание необходимых директорий
        os.makedirs(config.WORKING_DIR, exist_ok=True)
        os.makedirs(config.INPUT_DIR, exist_ok=True)
        
        # Запуск MCP сервера
        logger.info(f"Запуск LightRAG MCP сервера на {config.SERVER_HOST}:{config.SERVER_PORT}")
        mcp.run(host=config.SERVER_HOST, port=config.SERVER_PORT)
        
    except KeyboardInterrupt:
        logger.info("Сервер остановлен пользователем")
    except Exception as e:
        logger.exception(f"Ошибка при запуске сервера: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
