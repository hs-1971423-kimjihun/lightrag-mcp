# LightRAG MCP Server

MCP-сервер для интеграции с LightRAG API. Этот сервер позволяет использовать возможности LightRAG через интерфейс Model Context Protocol (MCP).

## Возможности

- Интеграция с LightRAG API для поиска и извлечения информации из документов
- Предоставление доступа к WebUI LightRAG
- API для загрузки и управления документами
- Поддержка различных режимов поиска (hybrid, semantic, keyword)

## Установка

### Предварительные требования

- Python 3.10 или выше
- uv (для управления зависимостями)
- LightRAG (должен быть доступен в системе)

### Установка с помощью uv

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/lightrag-mcp.git
cd lightrag-mcp

# Установка зависимостей
uv pip install -e .

# Для разработки
uv pip install -e ".[dev]"
```

## Конфигурация

Создайте файл `.env` в корневой директории проекта:

```bash
# LightRAG API settings
LIGHTRAG_API_HOST="localhost"
LIGHTRAG_API_PORT=9621
LIGHTRAG_API_KEY="your-api-key-here"

# Параметры для MCP сервера
HOST="0.0.0.0"
PORT=8000
TIMEOUT=150

# API ключи
MCP_API_KEY="your-mcp-api-key-here"
```

## Использование

### Запуск сервера

> **ВАЖНО**: Перед запуском MCP сервера необходимо запустить LightRAG API сервер вручную. MCP сервер не запускает LightRAG API автоматически.

```bash
# Запуск MCP сервера
lightrag-mcp

# Запуск с указанием порта и хоста
lightrag-mcp --host 127.0.0.1 --port 8000

# Запуск с подробным логированием
lightrag-mcp --log-level DEBUG
```

### Использование с существующим LightRAG API

1. Запустите LightRAG API сервер отдельно:
```bash
uv run LightRAG/lightrag/api/lightrag_server.py --host localhost --port 9621 --working-dir ./rag_storage --input-dir ./input --llm-binding openai --embedding-binding openai --log-level DEBUG
```

2. Запустите MCP сервер:
```bash
lightrag-mcp
```

### Доступ к WebUI

После запуска LightRAG API (отдельно или через MCP-сервер), WebUI доступен по адресу:
```
http://localhost:9621/
```

## API

### MCP Ресурсы

- `document://{doc_id}` - Получение информации о документе по ID
- `config://lightrag` - Получение конфигурации LightRAG
- `ui://lightrag` - Получение URL для доступа к WebUI LightRAG

### MCP Инструменты

- `query_document` - Выполнение поиска в документах
- `insert_document` - Добавление документа в LightRAG
- `upload_document` - Загрузка файла в LightRAG
- `delete_document` - Удаление документа из LightRAG
- `check_lightrag_health` - Проверка состояния LightRAG API

## Разработка

```bash
# Запуск тестов
pytest

# Форматирование кода
black .
isort .

# Проверка типов
mypy .
```

## Лицензия

[MIT License](LICENSE)
