"""
Модуль настройки и конфигурации для MCP-сервера LightRAG.
"""

import os
import pathlib

from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# LightRAG API settings
LIGHTRAG_API_HOST = os.getenv("LIGHTRAG_API_HOST", "localhost")
LIGHTRAG_API_PORT = int(os.getenv("LIGHTRAG_API_PORT", "9621"))
LIGHTRAG_API_KEY = os.getenv("LIGHTRAG_API_KEY", "")
LIGHTRAG_API_BASE_URL = f"http://{LIGHTRAG_API_HOST}:{LIGHTRAG_API_PORT}"

# Параметры для MCP сервера
TIMEOUT = int(os.getenv("TIMEOUT", "300"))

# Базовая директория проекта
BASE_DIR = str(pathlib.Path(__file__).parent.parent.parent.absolute())
