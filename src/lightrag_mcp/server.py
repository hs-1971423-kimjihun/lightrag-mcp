"""
Основной модуль MCP сервера для LightRAG.
"""

import logging
from typing import Any, Dict, List, Optional, Union, cast

from mcp.server.fastmcp import FastMCP

from lightrag_mcp import config
from lightrag_mcp.lightrag_client import LightRAGClient

logger = logging.getLogger(__name__)

# Создание MCP-сервера
mcp = FastMCP("LightRAG MCP Server")


def format_response(result: Any, is_error: bool = False) -> Dict[str, Any]:
    """
    Форматирует ответ в стандартный формат.

    Args:
        result: Результат операции
        is_error: Флаг ошибки

    Returns:
        Dict[str, Any]: Стандартизированный ответ
    """
    if is_error:
        if isinstance(result, str):
            return {"status": "error", "error": result}
        return {"status": "error", "error": str(result)}

    # Если результат уже словарь, возвращаем его в обертке
    if isinstance(result, dict):
        return {"status": "success", "response": result}

    # Если результат имеет метод dict() или __dict__, используем его
    if hasattr(result, "dict") and callable(getattr(result, "dict")):
        return {"status": "success", "response": result.dict()}
    if hasattr(result, "__dict__"):
        return {"status": "success", "response": result.__dict__}
    if hasattr(result, "to_dict") and callable(getattr(result, "to_dict")):
        return {"status": "success", "response": result.to_dict()}

    # В остальных случаях преобразуем в строку
    return {"status": "success", "response": str(result)}


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
    )

    # Проверка доступности LightRAG API
    try:
        health = await lightrag_client.get_health()
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


# === MCP Инструменты ===


@mcp.tool()
async def query_document(
    query: str,
    mode: str = "mix",
    top_k: int = 10,
    only_need_context: bool = False,
    only_need_prompt: bool = False,
    response_type: str = "Multiple Paragraphs",
    max_token_for_text_unit: int = 1000,
    max_token_for_global_context: int = 1000,
    max_token_for_local_context: int = 1000,
    hl_keywords: list[str] = [],
    ll_keywords: list[str] = [],
    history_turns: int = 10,
) -> Dict[str, Any]:
    """
    Выполнение поиска в документах через LightRAG API.

    Args:
        query (str): Текст запроса
        mode (str): Режим поиска (mix, semantic, keyword, global, hybrid, local, naive)
        top_k (int): Количество результатов
        only_need_context (bool): Возвращать только контекст без создания ответа LLM
        only_need_prompt (bool): Если True, возвращает только сгенерированный запрос без создания ответа
        response_type (str): Определяет формат ответа. Примеры: 'Multiple Paragraphs', 'Single Paragraph', 'Bullet Points'
        max_token_for_text_unit (int): Максимальное количество токенов для каждого текстового фрагмента
        max_token_for_global_context (int): Максимальное количество токенов для глобального контекста
        max_token_for_local_context (int): Максимальное количество токенов для локального контекста
        hl_keywords (list[str]): Список ключевых слов высокого уровня для приоритизации
        ll_keywords (list[str]): Список ключевых слов низкого уровня для уточнения поиска
        history_turns (int): Количество ходов разговора в контексте ответа

    Returns:
        Dict[str, Any]: Результаты запроса
    """
    logger.info(f"Запрос к документам: {query}, режим: {mode}")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()
        if lightrag_client is None:
            return format_response("Не удалось инициализировать LightRAG API клиент", is_error=True)

    # Явное утверждение типа для mypy
    client = cast(LightRAGClient, lightrag_client)

    try:
        result = await client.query(
            query_text=query,
            mode=mode,
            top_k=top_k,
            only_need_context=only_need_context,
            only_need_prompt=only_need_prompt,
            response_type=response_type,
            max_token_for_text_unit=max_token_for_text_unit,
            max_token_for_global_context=max_token_for_global_context,
            max_token_for_local_context=max_token_for_local_context,
            hl_keywords=hl_keywords,
            ll_keywords=ll_keywords,
            history_turns=history_turns,
        )

        # Проверка результата
        if result is None:
            logger.error("LightRAG API вернул пустой результат (None)")
            return format_response("Получен пустой ответ от LightRAG API", is_error=True)

        return format_response(result)
    except Exception as e:
        error_msg = f"Ошибка при выполнении запроса к LightRAG API: {str(e)}"
        logger.error(error_msg)
        return format_response(error_msg, is_error=True)


@mcp.tool()
async def insert_document(
    text: Union[str, List[str]],
    ids: Optional[List[str]] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Добавление документов через LightRAG API.

    Args:
        text (Union[str, List[str]]): Текст или список текстов для добавления
        ids (Optional[List[str]]): Список ID для текстов (примечание: в текущей версии API не используется)
        description (Optional[str]): Описание документов (примечание: в текущей версии API не используется)

    Returns:
        Dict[str, Any]: Результат операции
    """
    logger.info(f"Добавление документов, описание: {description}")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()
        if lightrag_client is None:
            return format_response("Не удалось инициализировать LightRAG API клиент", is_error=True)

    # Явное утверждение типа для mypy
    client = cast(LightRAGClient, lightrag_client)
    try:
        result = await client.insert_text(text=text)
        if result is None:
            return format_response("Не удалось добавить текст", is_error=True)
        return format_response(result)
    except Exception as e:
        error_msg = f"Ошибка при добавлении текста: {str(e)}"
        logger.error(error_msg)
        return format_response(error_msg, is_error=True)


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
        if lightrag_client is None:
            return format_response("Не удалось инициализировать LightRAG API клиент", is_error=True)

    # Явное утверждение типа для mypy
    client = cast(LightRAGClient, lightrag_client)
    try:
        result = await client.upload_document(file_path=file_path)
        return format_response(result)
    except Exception as e:
        error_msg = f"Ошибка при загрузке файла: {str(e)}"
        logger.error(error_msg)
        return format_response(error_msg, is_error=True)


@mcp.tool()
async def insert_file(file_path: str) -> Dict[str, Any]:
    """
    Добавление документа из файла в LightRAG.

    Args:
        file_path (str): Путь к файлу для загрузки

    Returns:
        Dict[str, Any]: Результат операции
    """
    logger.info(f"Добавление файла: {file_path}")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()
        if lightrag_client is None:
            return format_response("Не удалось инициализировать LightRAG API клиент", is_error=True)

    # Явное утверждение типа для mypy
    client = cast(LightRAGClient, lightrag_client)
    try:
        result = await client.insert_file(file_path=file_path)
        return format_response(result)
    except Exception as e:
        error_msg = f"Ошибка при добавлении файла в LightRAG API: {str(e)}"
        logger.error(error_msg)
        return format_response(error_msg, is_error=True)


@mcp.tool()
async def insert_batch(directory_path: str) -> Dict[str, Any]:
    """
    Добавление пакета документов из директории в LightRAG.

    Args:
        directory_path (str): Путь к директории с файлами для добавления

    Returns:
        Dict[str, Any]: Результат операции
    """
    logger.info(f"Добавление пакета документов из директории: {directory_path}")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()
        if lightrag_client is None:
            return format_response("Не удалось инициализировать LightRAG API клиент", is_error=True)

    # Явное утверждение типа для mypy
    client = cast(LightRAGClient, lightrag_client)
    try:
        result = await client.insert_batch(directory_path=directory_path)
        if result is None:
            return format_response("Не удалось добавить документы из директории", is_error=True)
        return format_response(result)
    except Exception as e:
        error_msg = f"Ошибка при добавлении документов из директории в LightRAG API: {str(e)}"
        logger.error(error_msg)
        return format_response(error_msg, is_error=True)


@mcp.tool()
async def scan_for_new_documents() -> Dict[str, Any]:
    """
    Запуск сканирования директории на наличие новых документов.

    Returns:
        Dict[str, Any]: Результат операции
    """
    logger.info("Запуск сканирования директории на наличие новых документов")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()
        if lightrag_client is None:
            return format_response("Не удалось инициализировать LightRAG API клиент", is_error=True)

    # Явное утверждение типа для mypy
    client = cast(LightRAGClient, lightrag_client)
    try:
        result = await client.scan_for_new_documents()
        return format_response(result)
    except Exception as e:
        error_msg = f"Ошибка при сканировании директории: {str(e)}"
        logger.error(error_msg)
        return format_response(error_msg, is_error=True)


@mcp.tool()
async def get_documents() -> Dict[str, Any]:
    """
    Получение списка всех загруженных документов.

    Returns:
        Dict[str, Any]: Список документов
    """
    logger.info("Получение списка загруженных документов")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()
        if lightrag_client is None:
            return format_response("Не удалось инициализировать LightRAG API клиент", is_error=True)

    # Явное утверждение типа для mypy
    client = cast(LightRAGClient, lightrag_client)
    try:
        result = await client.get_documents()
        if result is None:
            return format_response("Не удалось получить список документов", is_error=True)
        return format_response(result)
    except Exception as e:
        error_msg = f"Ошибка при получении списка документов: {str(e)}"
        logger.error(error_msg)
        return format_response(error_msg, is_error=True)


@mcp.tool()
async def get_pipeline_status() -> Dict[str, Any]:
    """
    Получение статуса обработки документов в пайплайне.

    Returns:
        Dict[str, Any]: Статус пайплайна
    """
    logger.info("Получение статуса обработки документов в пайплайне")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()
        if lightrag_client is None:
            return format_response("Не удалось инициализировать LightRAG API клиент", is_error=True)

    # Явное утверждение типа для mypy
    client = cast(LightRAGClient, lightrag_client)
    try:
        result = await client.get_pipeline_status()
        if result is None:
            return format_response("Не удалось получить статус пайплайна", is_error=True)
        return format_response(result)
    except Exception as e:
        error_msg = f"Ошибка при получении статуса пайплайна: {str(e)}"
        logger.error(error_msg)
        return format_response(error_msg, is_error=True)


@mcp.tool()
async def get_graph_labels() -> Dict[str, Any]:
    """
    Получение меток (типов узлов и связей) из графа знаний.

    Returns:
        Dict[str, Any]: Метки графа
    """
    logger.info("Получение меток из графа знаний")
    global lightrag_client

    if lightrag_client is None:
        await init_lightrag()
        if lightrag_client is None:
            return format_response("Не удалось инициализировать LightRAG API клиент", is_error=True)

    # Явное утверждение типа для mypy
    client = cast(LightRAGClient, lightrag_client)
    try:
        result = await client.get_graph_labels()
        return format_response(result)
    except Exception as e:
        error_msg = f"Ошибка при получении меток графа: {str(e)}"
        logger.error(error_msg)
        return format_response(error_msg, is_error=True)


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
        if lightrag_client is None:
            return format_response("Не удалось инициализировать LightRAG API клиент", is_error=True)

    # Явное утверждение типа для mypy
    client = cast(LightRAGClient, lightrag_client)
    try:
        result = await client.get_health()
        return format_response(result)
    except Exception as e:
        error_msg = f"Ошибка при проверке состояния LightRAG API: {str(e)}"
        logger.error(error_msg)
        logger.error(
            f"Убедитесь, что LightRAG API сервер запущен и доступен по адресу: {config.LIGHTRAG_API_BASE_URL}"
        )
        return format_response(error_msg, is_error=True)
