# Спецификация MCP-сервера с использованием LightRAG

## 1. Обзор

Данный документ описывает спецификацию MCP-сервера (Model Context Protocol), интегрирующего LightRAG для эффективного поиска и предоставления релевантной информации из документов. Сервер предоставит LLM-моделям возможность использовать функциональность LightRAG через стандартизированный протокол MCP.

### 1.1 Определение и назначение

MCP-сервер с LightRAG — это решение, объединяющее преимущества интеллектуального поиска и извлечения информации из LightRAG с универсальным интерфейсом MCP для взаимодействия с LLM-моделями. 

### 1.2 Основные возможности

- Добавление документов в базу знаний LightRAG через интерфейс MCP
- Поиск и извлечение информации из документов с использованием различных режимов LightRAG (local, global, hybrid, naive, mix)
- Визуализация графа знаний и связей между сущностями
- Редактирование и управление сущностями и отношениями
- Возможность использования различных моделей вложений и языковых моделей
- Масштабируемое хранилище на основе PostgreSQL с поддержкой векторных, графовых и KV-операций
- Интеграция с различными LLM и Embedding бэкендами (OpenAI, Ollama, Azure OpenAI, lollms)
- Потоковая передача ответов для улучшения пользовательского опыта

## 2. Архитектура

### 2.1 Основные компоненты

1. **MCP Server**: Основа системы, реализующая протокол MCP и управляющая взаимодействием с клиентами.
2. **LightRAG Engine**: Ядро системы поиска и извлечения информации, предоставляющее функциональность RAG (Retrieval-Augmented Generation).
3. **Storage Manager**: Компонент, отвечающий за управление хранилищами (векторная БД, граф знаний, KV-хранилище, хранилище статусов документов).
4. **Model Interface**: Абстракция для взаимодействия с различными моделями (LLM, Embedding).
5. **Authentication Module**: Компонент, обеспечивающий безопасность и авторизацию доступа к API сервера.

### 2.2 Схема взаимодействия компонентов

```
┌────────────┐     ┌───────────────┐     ┌───────────────┐     ┌─────────────────┐
│ MCP Client │────▶│   MCP Server  │────▶│  LightRAG API │────▶│  LightRAG Engine │
└────────────┘     └───────────────┘     └───────────────┘     └─────────────────┘
                          │                       │                       │
                          │                       │                       ▼
                          │                       │               ┌─────────────────┐
                          │                       │               │ Storage Backend │
                          │                       │               └─────────────────┘
                          │                       ▼
                          │               ┌─────────────────┐
                          │               │   LightRAG UI   │
                          │               └─────────────────┘
```

## 3. Ресурсы MCP

### 3.1 Ресурсы для управления документами

- **document://{doc_id}** — получение информации о документе по ID
- **documents://list?limit={limit}&offset={offset}** — получение списка документов
- **entity://{entity_name}** — получение информации о сущности
- **entities://list?limit={limit}&offset={offset}** — получение списка сущностей
- **relation://{source_entity}/{target_entity}** — получение информации о связи между сущностями
- **document://status/{doc_id}** — получение статуса индексации документа

### 3.2 Ресурсы для управления конфигурацией

- **config://system** — получение системной конфигурации
- **config://models** — получение информации о доступных моделях
- **config://storage** — получение информации о настройках хранилища
- **stats://system** — получение статистики системы
- **stats://storage** — получение статистики хранилища
- **stats://processing** — получение информации о текущих процессах индексации

## 4. Инструменты MCP

### 4.1 Инструменты для работы с документами

- **insert_document** — добавление документа в базу знаний
  - Параметры: 
    - `text`: строка или список строк с текстами документов
    - `ids`: опционально, список ID для документов
    - `file_paths`: опционально, список путей к файлам
    - `description`: опционально, описание документа

- **delete_document** — удаление документа из базы знаний
  - Параметры:
    - `doc_id`: ID документа

- **query_document** — поиск информации в документах
  - Параметры:
    - `query`: строка запроса
    - `mode`: режим поиска ("local", "global", "hybrid", "naive", "mix")
    - `top_k`: количество результатов (по умолчанию 60)
    - `only_need_context`: только контекст без генерации ответа (по умолчанию false)
    - `system_prompt`: опционально, системный промпт для настройки ответа
    - `stream`: опционально, использовать потоковую передачу ответа (по умолчанию false)

- **scan_documents** — сканирование директории input_dir для обнаружения новых документов и их индексации
  - Параметры:
    - `input_dir`: опционально, директория для сканирования (по умолчанию из конфигурации)

### 4.2 Инструменты для работы с графом знаний

- **create_entity** — создание новой сущности
  - Параметры:
    - `entity_name`: имя сущности
    - `properties`: свойства сущности (описание, тип и т.д.)

- **edit_entity** — редактирование сущности
  - Параметры:
    - `entity_name`: имя сущности
    - `properties`: новые свойства сущности

- **create_relation** — создание связи между сущностями
  - Параметры:
    - `source_entity`: исходная сущность
    - `target_entity`: целевая сущность
    - `properties`: свойства связи

- **edit_relation** — редактирование связи
  - Параметры:
    - `source_entity`: исходная сущность
    - `target_entity`: целевая сущность
    - `properties`: новые свойства связи

- **export_graph** — экспорт графа знаний
  - Параметры:
    - `format`: формат экспорта (csv, excel, md, txt)
    - `include_vector_data`: включать ли векторные данные

- **visualize_graph** — визуализация графа знаний или его части
  - Параметры:
    - `center_entity`: опционально, центральная сущность для визуализации
    - `depth`: опционально, глубина обхода графа от центральной сущности
    - `limit`: опционально, максимальное количество отображаемых сущностей

## 5. Интеграция с LightRAG

### 5.1 Архитектура взаимодействия с LightRAG API

MCP-сервер будет работать со внешним API-сервером LightRAG, который может быть либо запущен отдельно, либо запускаться MCP-сервером при необходимости. Такой подход позволяет гибко настраивать систему и использовать имеющийся WebUI от LightRAG.

```
┌────────────┐     ┌───────────────┐     ┌───────────────┐     ┌─────────────────┐
│ MCP Client │────▶│   MCP Server  │────▶│  LightRAG API │────▶│  LightRAG Engine │
└────────────┘     └───────────────┘     └───────────────┘     └─────────────────┘
                          │                       │                       │
                          │                       │                       ▼
                          │                       │               ┌─────────────────┐
                          │                       │               │ Storage Backend │
                          │                       │               └─────────────────┘
                          │                       ▼
                          │               ┌─────────────────┐
                          │               │   LightRAG UI   │
                          │               └─────────────────┘
```

### 5.2 Настройка подключения к LightRAG API

MCP-сервер будет подключаться к LightRAG API по HTTP, используя следующие параметры конфигурации:

```python
# config.py
# LightRAG API settings
LIGHTRAG_API_HOST = os.getenv("LIGHTRAG_API_HOST", "localhost")
LIGHTRAG_API_PORT = int(os.getenv("LIGHTRAG_API_PORT", "9621"))
LIGHTRAG_API_KEY = os.getenv("LIGHTRAG_API_KEY", "")
LIGHTRAG_API_BASE_URL = f"http://{LIGHTRAG_API_HOST}:{LIGHTRAG_API_PORT}"
LIGHTRAG_AUTOSTART = os.getenv("LIGHTRAG_AUTOSTART", "false").lower() == "true"
```

### 5.3 Запуск LightRAG API сервера

Если параметр `LIGHTRAG_AUTOSTART` установлен в `true`, MCP-сервер будет запускать LightRAG API сервер в отдельном процессе:

```python
import subprocess
import os
import signal
import atexit

# Глобальная переменная для хранения процесса
lightrag_process = None

def start_lightrag_server():
    """Запуск LightRAG API сервера в отдельном процессе"""
    global lightrag_process
    
    lightrag_cmd = [
        "lightrag-server",
        "--host", config.LIGHTRAG_API_HOST,
        "--port", str(config.LIGHTRAG_API_PORT)
    ]
    
    if config.LIGHTRAG_API_KEY:
        lightrag_cmd.extend(["--key", config.LIGHTRAG_API_KEY])
    
    # Запуск процесса LightRAG
    lightrag_process = subprocess.Popen(
        lightrag_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Регистрация функции для остановки процесса при завершении MCP сервера
    atexit.register(stop_lightrag_server)
    
    return lightrag_process

def stop_lightrag_server():
    """Остановка LightRAG API сервера"""
    global lightrag_process
    if lightrag_process and lightrag_process.poll() is None:
        os.kill(lightrag_process.pid, signal.SIGTERM)
        lightrag_process.wait()
        lightrag_process = None
```

### 5.4 Клиент для LightRAG API

MCP-сервер будет использовать HTTP-клиент для взаимодействия с LightRAG API:

```python
import httpx
import json
from typing import Dict, List, Optional, Union, Any

class LightRAGClient:
    """Клиент для взаимодействия с LightRAG API"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 150):
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {}
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    async def query(self, query_text: str, mode: str = "hybrid", 
                  top_k: int = 60, only_need_context: bool = False,
                  system_prompt: Optional[str] = None) -> str:
        """Выполнение запроса к LightRAG"""
        url = f"{self.base_url}/query"
        
        payload = {
            "query": query_text,
            "mode": mode,
            "top_k": top_k,
            "only_need_context": only_need_context
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()["response"]
    
    async def insert_text(self, text: Union[str, List[str]], 
                        ids: Optional[List[str]] = None,
                        description: Optional[str] = None) -> Dict[str, Any]:
        """Добавление текста в LightRAG"""
        url = f"{self.base_url}/documents/text"
        
        payload = {
            "text": text
        }
        
        if ids:
            payload["ids"] = ids
        
        if description:
            payload["description"] = description
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def check_health(self) -> Dict[str, Any]:
        """Проверка состояния LightRAG API"""
        url = f"{self.base_url}/health"
        
        async with httpx.AsyncClient(timeout=5) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError):
                return {"status": "error", "message": "LightRAG API недоступен"}
```

### 5.5 Связь MCP и LightRAG API

```python
# server.py
from mcp.server.fastmcp import FastMCP, Context
import config
from lightrag_client import LightRAGClient

# Создание MCP-сервера
mcp = FastMCP("LightRAG MCP Server")

# Глобальная переменная для клиента LightRAG
lightrag_client = None

@mcp.lifespan
async def setup_lightrag(server: FastMCP):
    """Инициализация LightRAG API клиента и при необходимости запуск сервера"""
    global lightrag_client
    
    # Запуск LightRAG API сервера при необходимости
    if config.LIGHTRAG_AUTOSTART:
        start_lightrag_server()
    
    # Создание клиента для LightRAG API
    lightrag_client = LightRAGClient(
        base_url=config.LIGHTRAG_API_BASE_URL,
        api_key=config.LIGHTRAG_API_KEY,
        timeout=config.TIMEOUT
    )
    
    # Проверка доступности LightRAG API
    health = await lightrag_client.check_health()
    if health.get("status") == "error":
        print(f"Предупреждение: {health.get('message')}")
    
    yield {"lightrag_client": lightrag_client}
    
    # Остановка LightRAG API сервера при необходимости
    if config.LIGHTRAG_AUTOSTART:
        stop_lightrag_server()

@mcp.resource("document://{doc_id}")
async def get_document(doc_id: str, ctx: Context) -> str:
    """Получение информации о документе по ID - прямой проксирование запроса к LightRAG API"""
    # Этот эндпоинт требует дополнительной реализации в LightRAG API
    return f"Документ с ID: {doc_id}"

@mcp.tool()
async def query_document(query: str, mode: str = "hybrid", top_k: int = 60, 
                       only_need_context: bool = False, system_prompt: str = None, 
                       ctx: Context) -> str:
    """Выполнение поиска в документах через LightRAG API"""
    lightrag_client = ctx.request_context.lifespan_context["lightrag_client"]
    
    result = await lightrag_client.query(
        query_text=query,
        mode=mode,
        top_k=top_k,
        only_need_context=only_need_context,
        system_prompt=system_prompt
    )
    return result

@mcp.tool()
async def insert_document(text: Union[str, List[str]], ids: Optional[List[str]] = None,
                        description: Optional[str] = None, ctx: Context) -> str:
    """Добавление документа через LightRAG API"""
    lightrag_client = ctx.request_context.lifespan_context["lightrag_client"]
    
    result = await lightrag_client.insert_text(
        text=text,
        ids=ids,
        description=description
    )
    
    return f"Документ успешно добавлен: {result}"
```

## 6. Настройка и конфигурация

### 6.1 Использование uv для управления проектом

Для управления проектом будет использоваться uv. Создадим файл `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "lightrag-mcp"
version = "0.1.0"
description = "MCP Server для LightRAG"
requires-python = ">=3.10"
license = {file = "LICENSE"}
readme = "README.md"
authors = [
    {name = "Author", email = "author@example.com"},
]
dependencies = [
    "mcp>=0.2.0",
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "mypy>=1.5.0",
    "black>=23.7.0",
    "isort>=5.12.0",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.1",
]

[project.scripts]
lightrag-mcp = "lightrag_mcp.main:main"

[tool.hatch.build.targets.wheel]
packages = ["src/lightrag_mcp"]
```

### 6.2 Основные параметры конфигурации

```python
# config.py
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
```

### 6.3 Файл с переменными окружения

```bash
# .env
WORKING_DIR="./rag_storage"
INPUT_DIR="./input"

# LightRAG API settings
LIGHTRAG_API_HOST="localhost"
LIGHTRAG_API_PORT=9621
LIGHTRAG_API_KEY="your-api-key-here"
# Автоматический запуск LightRAG API или подключение к существующему
LIGHTRAG_AUTOSTART=false

# Параметры для LightRAG API, если он запускается MCP-сервером
LLM_BINDING="openai"  # openai, ollama, azure_openai
LLM_MODEL="gpt-4o-mini"
LLM_BINDING_API_KEY="your-openai-api-key"

EMBEDDING_BINDING="openai"
EMBEDDING_MODEL="text-embedding-3-large"
EMBEDDING_BINDING_HOST="https://api.openai.com/v1"
EMBEDDING_BINDING_API_KEY="your-openai-api-key"

# Параметры для MCP сервера
HOST="0.0.0.0"
PORT=8000
TIMEOUT=150

# API ключи
MCP_API_KEY="your-mcp-api-key-here"
```

## 7. Запуск и развертывание

### 7.1 Структура проекта

```
lightrag-mcp/
├── pyproject.toml         # Конфигурация проекта
├── README.md              # Документация
├── .env                   # Переменные окружения
├── src/
│   └── lightrag_mcp/
│       ├── __init__.py
│       ├── main.py        # Точка входа
│       ├── server.py      # Реализация MCP сервера
│       ├── config.py      # Конфигурация
│       └── lightrag_client.py  # Клиент для LightRAG API
└── tests/
    └── test_server.py     # Тесты
```

### 7.2 Установка и запуск

```bash
# Установка зависимостей через uv
uv pip install -e .

# Запуск MCP сервера напрямую
python -m lightrag_mcp.main

# Или через скрипт
lightrag-mcp

# Установка MCP сервера в Claude Desktop
mcp install src/lightrag_mcp/main.py

# Запуск в режиме разработки с MCP Inspector
mcp dev src/lightrag_mcp/main.py
```

### 7.3 Доступ к WebUI LightRAG

Поскольку мы будем использовать существующий WebUI LightRAG, MCP-сервер может предоставить информацию для доступа:

```python
@mcp.resource("ui://lightrag")
async def get_lightrag_ui_url(ctx: Context) -> str:
    """Возвращает URL для доступа к WebUI LightRAG"""
    return f"http://{config.LIGHTRAG_API_HOST}:{config.LIGHTRAG_API_PORT}/"
```

## 8. Сценарии использования

### 8.1 Использование с существующим API сервером LightRAG

1. Запустить LightRAG API сервер:
```bash
lightrag-server --port 9621
```

2. Настроить MCP сервер для подключения к существующему API:
```
LIGHTRAG_API_HOST="localhost"
LIGHTRAG_API_PORT=9621
LIGHTRAG_AUTOSTART=false
```

3. Запустить MCP сервер:
```bash
lightrag-mcp
```

### 8.2 Автоматический запуск LightRAG API сервера

1. Настроить MCP сервер для автозапуска LightRAG API:
```
LIGHTRAG_AUTOSTART=true
LLM_BINDING="openai"
LLM_MODEL="gpt-4o-mini"
LLM_BINDING_API_KEY="your-api-key"
```

2. Запустить MCP сервер, который автоматически запустит LightRAG API:
```bash
lightrag-mcp
```

### 8.3 Использование WebUI

После запуска LightRAG API (отдельно или через MCP-сервер), WebUI доступен по адресу:
```
http://localhost:9621/
```

## 9. Расширение функциональности

### 9.1 Поддержка дополнительных моделей

Система поддерживает различные LLM и Embedding модели:
- OpenAI API (ChatGPT, GPT-4o, etc.)
- Hugging Face модели
- Ollama модели (локальное развертывание)
- Azure OpenAI API
- lollms (локальные модели)
- LlamaIndex интеграция

### 9.2 Альтернативные хранилища

Поддержка различных типов хранилищ:
- Neo4J для графа знаний
- PostgreSQL с pgvector (универсальное решение)
- FAISS для векторного хранилища
- MongoDB для всех типов хранилищ
- Oracle для всех типов хранилищ

### 9.3 Интеграция с существующими системами

MCP-сервер можно интегрировать с:
- Claude Desktop
- Облачными LLM решениями
- Локальными Ollama моделями
- Другими MCP-совместимыми клиентами

## 10. Сценарии использования

### 10.1 Интеллектуальная обработка документации

- **Индексирование корпоративной документации**:
  - Добавление документов через MCP tool `insert_document`
  - Автоматическое извлечение сущностей и отношений
  - Доступ к знаниям через запросы

- **Многоязычный поиск и ответы на вопросы**:
  - Поддержка различных языков в зависимости от используемых моделей
  - Индексация документов на разных языках
  - Запросы и ответы на языке пользователя

### 10.2 Аналитика данных

- **Интерактивный анализ данных**:
  - Использование различных режимов запросов (local, global, hybrid, mix)
  - Визуализация связей между сущностями
  - Экспорт данных для дальнейшего анализа

- **Генерация отчетов на основе документов**:
  - Агрегация информации из различных источников
  - Создание структурированных отчетов с цитированием источников
  - Предоставление контекста для генерируемых выводов

### 10.3 Интеграции с внешними системами

- **Интеграция в существующие системы с LLM**:
  - Подключение через MCP к любой LLM-системе
  - Обогащение ответов LLM релевантной информацией из документов
  - Расширение контекстного окна модели через эффективное извлечение данных

- **Использование в корпоративном чат-боте**:
  - Интеграция с существующими платформами (через совместимость с Ollama API)
  - Доступ к корпоративной документации через естественный язык
  - Ответы на вопросы с учетом организационного контекста