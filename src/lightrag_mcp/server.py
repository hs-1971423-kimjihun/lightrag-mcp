"""
Основной модуль MCP сервера для LightRAG.
"""

import logging
from typing import Dict, List, Optional, Union, Any
from mcp.server.fastmcp import FastMCP
from lightrag_mcp import config
from lightrag_mcp.lightrag_client import LightRAGClient

logger = logging.getLogger(__name__)

# Создание MCP-сервера
mcp = FastMCP("LightRAG MCP Server")

# Глобальная переменная для клиента LightRAG
lightrag_client = None
is_initialized = False


# Инициализация LightRAG API клиента
async def init_lightrag():
    """
    Инициализация LightRAG API клиента и проверка доступности сервера.
    """
    global lightrag_client, is_initialized

    if is_initialized:
        return

    logger.info("Инициализация LightRAG MCP Server")

    # Создаем экземпляр клиента LightRAG
    lightrag_client = LightRAGClient(
        base_url=config.LIGHTRAG_API_BASE_URL,
        api_key=config.LIGHTRAG_API_KEY,
        timeout=config.TIMEOUT,
    )

    # Проверка доступности LightRAG API
    try:
        health = await lightrag_client.health_check()
        if health.get("status") == "ok":
            logger.info("LightRAG API доступен")
        else:
            logger.warning(
                f"Предупреждение: LightRAG API вернул статус: {health.get('status', 'unknown')}"
            )
    except Exception as e:
        logger.error(f"Ошибка: LightRAG API недоступен: {str(e)}")
        logger.error(
            "Убедитесь, что LightRAG API сервер запущен и доступен по адресу: "
            + config.LIGHTRAG_API_BASE_URL
        )

    is_initialized = True


# === MCP Ресурсы ===


@mcp.resource("document://{doc_id}")
async def get_document(doc_id: str) -> Dict[str, Any]:
    """
    Получение информации о документе по ID.

    Args:
        doc_id (str): Идентификатор документа

    Returns:
        Dict[str, Any]: Информация о документе
    """
    logger.info(f"Запрос информации о документе: {doc_id}")

    global lightrag_client
    if lightrag_client is None:
        await init_lightrag()

    # Эта функция требует дополнительной реализации в LightRAG API
    # В текущей версии LightRAG API нет прямого метода для получения информации о документе по ID
    logger.warning(
        f"Метод получения документа по ID {doc_id} не реализован в текущей версии LightRAG API"
    )
    return {
        "id": doc_id,
        "status": "not_implemented",
        "message": "Метод получения документа по ID не реализован в текущей версии LightRAG API",
    }


@mcp.resource("config://lightrag")
async def get_lightrag_config() -> Dict[str, Any]:
    """
    Получение конфигурации LightRAG.

    Returns:
        Dict[str, Any]: Конфигурация LightRAG
    """
    logger.info("Запрос конфигурации LightRAG")

    # Маскируем конфиденциальные данные
    return {
        "api": {
            "host": config.LIGHTRAG_API_HOST,
            "port": config.LIGHTRAG_API_PORT,
            "base_url": config.LIGHTRAG_API_BASE_URL,
        },
        "server": {
            "host": config.SERVER_HOST,
            "port": config.SERVER_PORT,
            "timeout": config.TIMEOUT,
        },
        "directories": {
            "working_dir": config.WORKING_DIR,
            "input_dir": config.INPUT_DIR,
        },
    }


@mcp.resource("ui://lightrag")
async def get_lightrag_ui_url() -> str:
    """
    Возвращает URL для доступа к WebUI LightRAG.

    Returns:
        str: URL для доступа к WebUI
    """
    logger.info("Запрос URL для WebUI LightRAG")
    return f"http://{config.LIGHTRAG_API_HOST}:{config.LIGHTRAG_API_PORT}/"


# === MCP Инструменты ===


@mcp.tool()
async def query_document(
    query: str,
    mode: str = "mix",
    top_k: int = 60,
    only_need_context: bool = False,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Выполнение поиска в документах через LightRAG API.

    Args:
        query (str): Текст запроса
        mode (str): Режим поиска (mix, semantic, keyword)
        top_k (int): Количество результатов
        only_need_context (bool): Возвращать только контекст без создания ответа LLM
        system_prompt (Optional[str]): Системный промпт для LLM

    Returns:
        Dict[str, Any]: Результаты запроса
    """
    logger.info(f"Запрос к документам: {query}, режим: {mode}")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()

    result = await lightrag_client.query(
        query_text=query,
        mode=mode,
        top_k=top_k,
        only_need_context=only_need_context,
        system_prompt=system_prompt,
    )
    return result


@mcp.tool()
async def insert_document(
    text: Union[str, List[str]],
    ids: Optional[List[str]] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Добавление документа через LightRAG API.

    Args:
        text (Union[str, List[str]]): Текст или список текстов для добавления
        ids (Optional[List[str]]): Список ID для текстов
        description (Optional[str]): Описание документов

    Returns:
        Dict[str, Any]: Результат операции
    """
    logger.info(f"Добавление документа, описание: {description}")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()

    result = await lightrag_client.insert_text(
        text=text, ids=ids, description=description
    )

    return result


@mcp.tool()
async def upload_document(
    file_path: str, file_id: Optional[str] = None, description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Загрузка файла в LightRAG.

    Args:
        file_path (str): Путь к файлу для загрузки
        file_id (Optional[str]): ID для файла
        description (Optional[str]): Описание файла

    Returns:
        Dict[str, Any]: Результат операции
    """
    logger.info(f"Загрузка файла: {file_path}, описание: {description}")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()

    result = await lightrag_client.upload_file(
        file_path=file_path, file_id=file_id, description=description
    )

    return result


@mcp.tool()
async def delete_document(doc_id: str) -> Dict[str, Any]:
    """
    Удаление документа из LightRAG.

    Args:
        doc_id (str): ID документа для удаления

    Returns:
        Dict[str, Any]: Результат операции
    """
    logger.info(f"Удаление документа: {doc_id}")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()

    result = await lightrag_client.delete_document(doc_id=doc_id)

    return result


@mcp.tool()
async def check_lightrag_health() -> Dict[str, Any]:
    """
    Проверка состояния LightRAG API.

    Returns:
        Dict[str, Any]: Статус сервера
    """
    logger.info("Проверка состояния LightRAG API")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()

    try:
        result = await lightrag_client.health_check()
        logger.info(f"LightRAG API статус: {result.get('status', 'unknown')}")
        return result
    except Exception as e:
        error_msg = f"Ошибка при проверке состояния LightRAG API: {str(e)}"
        logger.error(error_msg)
        logger.error(
            f"Убедитесь, что LightRAG API сервер запущен и доступен по адресу: {config.LIGHTRAG_API_BASE_URL}"
        )
        return {"status": "error", "message": error_msg}
