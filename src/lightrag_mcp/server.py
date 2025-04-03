"""
Основной модуль MCP сервера для LightRAG.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Union, cast

from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

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


@dataclass
class AppContext:
    """Контекст приложения с типизированными ресурсами."""

    lightrag_client: LightRAGClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Управление жизненным циклом приложения с типизированным контекстом.
    Инициализирует LightRAG API клиент при запуске и закрывает его при остановке.
    """
    logger.info("Инициализация LightRAG MCP Server")

    # Создаем экземпляр клиента LightRAG
    lightrag_client = LightRAGClient(
        base_url=config.LIGHTRAG_API_BASE_URL,
        api_key=config.LIGHTRAG_API_KEY,
    )

    # Проверка доступности LightRAG API
    try:
        health = await lightrag_client.get_health()
        # Проверяем, что health - это словарь, прежде чем вызывать метод get()
        if isinstance(health, dict) and health.get("status") == "ok":
            logger.info("LightRAG API доступен")
        else:
            status = health.get("status", "unknown") if isinstance(health, dict) else "unknown"
            logger.warning(f"Предупреждение: LightRAG API вернул статус: {status}")
    except Exception as e:
        logger.error(f"Ошибка: LightRAG API недоступен: {str(e)}")
        logger.error(
            "Убедитесь, что LightRAG API сервер запущен и доступен по адресу: "
            + config.LIGHTRAG_API_BASE_URL
        )

    try:
        yield AppContext(lightrag_client=lightrag_client)
    finally:
        # Закрываем клиент при завершении работы
        await lightrag_client.close()
        logger.info("LightRAG MCP Server остановлен")


# Применяем lifespan к серверу
mcp = FastMCP("LightRAG MCP Server", lifespan=app_lifespan)


async def execute_lightrag_operation(
    operation_name: str, operation_func: Callable, ctx: Context
) -> Dict[str, Any]:
    """
    Универсальная функция-обертка для выполнения операций с LightRAG API.

    Автоматически обрабатывает:
    - Получение клиента из контекста
    - Приведение типов
    - Обработку исключений
    - Форматирование ответа

    Args:
        operation_name: Название операции для логирования
        operation_func: Функция для выполнения, которая принимает клиента как первый аргумент

    Returns:
        Dict[str, Any]: Отформатированный ответ
    """
    try:
        # Получаем контекст запроса
        if not ctx or not ctx.request_context or not ctx.request_context.lifespan_context:
            return format_response(
                f"Ошибка: Контекст запроса недоступен при {operation_name}", is_error=True
            )

        # Получаем клиент из контекста
        app_ctx = cast(AppContext, ctx.request_context.lifespan_context)
        client = app_ctx.lightrag_client

        # Выполняем операцию
        logger.info(f"Выполнение операции: {operation_name}")
        result = await operation_func(client)
        logger.info(f"Операция выполнена успешно: {operation_name}")

        return format_response(result)
    except Exception as e:
        logger.exception(f"Ошибка при {operation_name}: {str(e)}")
        return format_response(str(e), is_error=True)


# === MCP Инструменты ===


@mcp.tool(
    name="query_document",
    description="Выполнение запроса к документам через LightRAG API",
)
async def query_document(
    ctx: Context,
    query: str = Field(description="Текст запроса"),
    mode: str = Field(
        description="Режим поиска (mix, semantic, keyword, global, hybrid, local, naive)",
        default="mix",
    ),
    top_k: int = Field(description="Количество результатов", default=10),
    only_need_context: bool = Field(
        description="Возвращать только контекст без создания ответа LLM", default=False
    ),
    only_need_prompt: bool = Field(
        description="Если True, возвращает только сгенерированный запрос без создания ответа",
        default=False,
    ),
    response_type: str = Field(
        description="Определяет формат ответа. Примеры: 'Multiple Paragraphs', 'Single Paragraph', 'Bullet Points'",
        default="Multiple Paragraphs",
    ),
    max_token_for_text_unit: int = Field(
        description="Максимальное количество токенов для каждого текстового фрагмента",
        default=1000,
    ),
    max_token_for_global_context: int = Field(
        description="Максимальное количество токенов для глобального контекста", default=1000
    ),
    max_token_for_local_context: int = Field(
        description="Максимальное количество токенов для локального контекста", default=1000
    ),
    hl_keywords: list[str] = Field(
        description="Список ключевых слов высокого уровня для приоритизации", default=[]
    ),
    ll_keywords: list[str] = Field(
        description="Список ключевых слов низкого уровня для уточнения поиска", default=[]
    ),
    history_turns: int = Field(
        description="Количество ходов разговора в контексте ответа", default=10
    ),
) -> Dict[str, Any]:
    async def _operation(client: LightRAGClient) -> Any:
        return await client.query(
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

    return await execute_lightrag_operation(
        operation_name=f"запросе '{query}'", operation_func=_operation, ctx=ctx
    )


@mcp.tool(name="insert_document", description="Добавление документов через LightRAG API")
async def insert_document(
    ctx: Context,
    text: Union[str, List[str]] = Field(description="Текст или список текстов для добавления"),
) -> Dict[str, Any]:
    async def _operation(client: LightRAGClient) -> Any:
        return await client.insert_text(text=text)

    return await execute_lightrag_operation(
        operation_name="добавлении документа", operation_func=_operation, ctx=ctx
    )


@mcp.tool(name="upload_document", description="Загрузка документов из файла в LightRAG")
async def upload_document(
    ctx: Context,
    file_path: str = Field(description="Путь к файлу для загрузки"),
) -> Dict[str, Any]:
    async def _operation(client: LightRAGClient) -> Any:
        return await client.upload_document(file_path=file_path)

    return await execute_lightrag_operation(
        operation_name=f"загрузка файла {file_path}", operation_func=_operation, ctx=ctx
    )


@mcp.tool(name="insert_file", description="Добавление документа из файла в LightRAG")
async def insert_file(
    ctx: Context,
    file_path: str = Field(description="Путь к файлу для загрузки"),
) -> Dict[str, Any]:
    async def _operation(client: LightRAGClient) -> Any:
        return await client.insert_file(file_path=file_path)

    return await execute_lightrag_operation(
        operation_name=f"добавление файла {file_path}", operation_func=_operation, ctx=ctx
    )


@mcp.tool(name="insert_batch", description="Добавление пакета документов из директории в LightRAG")
async def insert_batch(
    ctx: Context,
    directory_path: str = Field(description="Путь к директории с файлами для добавления"),
) -> Dict[str, Any]:
    async def _operation(client: LightRAGClient) -> Any:
        return await client.insert_batch(directory_path=directory_path)

    return await execute_lightrag_operation(
        operation_name=f"добавление пакета документов из директории {directory_path}",
        operation_func=_operation,
        ctx=ctx,
    )


@mcp.tool(
    name="scan_for_new_documents",
    description="Запуск сканирования директории на наличие новых документов",
)
async def scan_for_new_documents(ctx: Context) -> Dict[str, Any]:
    async def _operation(client: LightRAGClient) -> Any:
        return await client.scan_for_new_documents()

    return await execute_lightrag_operation(
        operation_name="сканирование директории на наличие новых документов",
        operation_func=_operation,
        ctx=ctx,
    )


@mcp.tool(name="get_documents", description="Получение списка всех загруженных документов")
async def get_documents(ctx: Context) -> Dict[str, Any]:
    async def _operation(client: LightRAGClient) -> Any:
        return await client.get_documents()

    return await execute_lightrag_operation(
        operation_name="получение списка документов", operation_func=_operation, ctx=ctx
    )


@mcp.tool(
    name="get_pipeline_status", description="Получение статуса обработки документов в пайплайне"
)
async def get_pipeline_status(ctx: Context) -> Dict[str, Any]:
    async def _operation(client: LightRAGClient) -> Any:
        return await client.get_pipeline_status()

    return await execute_lightrag_operation(
        operation_name="получение статуса обработки документов в пайплайне",
        operation_func=_operation,
        ctx=ctx,
    )


@mcp.tool(
    name="get_graph_labels", description="Получение меток (типов узлов и связей) из графа знаний"
)
async def get_graph_labels(ctx: Context) -> Dict[str, Any]:
    async def _operation(client: LightRAGClient) -> Any:
        return await client.get_graph_labels()

    return await execute_lightrag_operation(
        operation_name="получение меток из графа знаний", operation_func=_operation, ctx=ctx
    )


@mcp.tool(name="check_lightrag_health", description="Проверка состояния LightRAG API")
async def check_lightrag_health(ctx: Context) -> Dict[str, Any]:
    async def _operation(client: LightRAGClient) -> Any:
        result = await client.get_health()
        # Проверяем, что result не является HTTPValidationError и имеет метод get
        if isinstance(result, dict) and "status" in result:
            if result["status"] != "ok":
                logger.warning(f"LightRAG API вернул статус: {result['status']}")
        return result

    return await execute_lightrag_operation(
        operation_name="проверка состояния LightRAG API", operation_func=_operation, ctx=ctx
    )
