"""
Модуль настройки и конфигурации для MCP-сервера LightRAG.
"""

import os
import pathlib
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Директории
WORKING_DIR = os.getenv("WORKING_DIR", "./rag_storage")
INPUT_DIR = os.getenv("INPUT_DIR", "./input")

# LightRAG API settings
LIGHTRAG_API_HOST = os.getenv("LIGHTRAG_API_HOST", "localhost")
LIGHTRAG_API_PORT = int(os.getenv("LIGHTRAG_API_PORT", "9621"))
LIGHTRAG_API_KEY = os.getenv("LIGHTRAG_API_KEY", "")
LIGHTRAG_API_BASE_URL = f"http://{LIGHTRAG_API_HOST}:{LIGHTRAG_API_PORT}"
# Сервер LightRAG должен быть запущен пользователем вручную

# Параметры для MCP сервера
SERVER_HOST = os.getenv("HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", "8000"))  # Другой порт, чтобы не конфликтовать с LightRAG
TIMEOUT = int(os.getenv("TIMEOUT", "150"))

# API ключи и безопасность
MCP_API_KEY = os.getenv("MCP_API_KEY", "")

# Базовая директория проекта
BASE_DIR = str(pathlib.Path(__file__).parent.parent.parent.absolute())
