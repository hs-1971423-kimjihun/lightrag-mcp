"""
Модуль настройки и конфигурации для MCP-сервера LightRAG.
"""

import os
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
LIGHTRAG_AUTOSTART = os.getenv("LIGHTRAG_AUTOSTART", "false").lower() == "true"

# Параметры запуска LightRAG
LIGHTRAG_LLM_BINDING = os.getenv("LLM_BINDING", "openai")  # openai, ollama, azure_openai, lollms
LIGHTRAG_LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LIGHTRAG_LLM_BINDING_HOST = os.getenv("LLM_BINDING_HOST", "https://api.openai.com/v1")
LIGHTRAG_LLM_BINDING_API_KEY = os.getenv("LLM_BINDING_API_KEY", "")

LIGHTRAG_EMBEDDING_BINDING = os.getenv("EMBEDDING_BINDING", "openai")
LIGHTRAG_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
LIGHTRAG_EMBEDDING_BINDING_HOST = os.getenv("EMBEDDING_BINDING_HOST", "https://api.openai.com/v1")
LIGHTRAG_EMBEDDING_BINDING_API_KEY = os.getenv("EMBEDDING_BINDING_API_KEY", "")

# Параметры для MCP сервера
SERVER_HOST = os.getenv("HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", "8000"))  # Другой порт, чтобы не конфликтовать с LightRAG
TIMEOUT = int(os.getenv("TIMEOUT", "150"))

# API ключи и безопасность
MCP_API_KEY = os.getenv("MCP_API_KEY", "")
