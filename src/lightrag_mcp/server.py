"""
Основной модуль MCP сервера для LightRAG.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from mcp.server.fastmcp import FastMCP, Context

from lightrag_mcp import config
from lightrag_mcp.lightrag_client import LightRAGClient
from lightrag_mcp.process_manager import start_lightrag_server, stop_lightrag_server, is_lightrag_server_running

logger = logging.getLogger(__name__)

# Создание MCP-сервера
mcp = FastMCP("LightRAG MCP Server")

# Глобальная переменная для клиента LightRAG
lightrag_client = None

@mcp.lifespan
async def setup_lightrag(server: FastMCP):
    """
    Инициализация LightRAG API клиента и при необходимости запуск сервера.
    
    Этот контекст выполняется при запуске и завершении работы MCP сервера.
    """
    global lightrag_client
    
    logger.info("Инициализация LightRAG MCP Server")
    
    # Запуск LightRAG API сервера при необходимости
    if config.LIGHTRAG_AUTOSTART:
        logger.info("Автоматический запуск LightRAG API сервера")
        
        # Подготовка переменных окружения для LightRAG
        env_vars = {
            "LLM_BINDING": config.LIGHTRAG_LLM_BINDING,
            "LLM_MODEL": config.LIGHTRAG_LLM_MODEL,
            "LLM_BINDING_HOST": config.LIGHTRAG_LLM_BINDING_HOST,
            "LLM_BINDING_API_KEY": config.LIGHTRAG_LLM_BINDING_API_KEY,
            
            "EMBEDDING_BINDING": config.LIGHTRAG_EMBEDDING_BINDING,
            "EMBEDDING_MODEL": config.LIGHTRAG_EMBEDDING_MODEL,
            "EMBEDDING_BINDING_HOST": config.LIGHTRAG_EMBEDDING_BINDING_HOST,
            "EMBEDDING_BINDING_API_KEY": config.LIGHTRAG_EMBEDDING_BINDING_API_KEY,
            
            "WORKING_DIR": config.WORKING_DIR,
            "INPUT_DIR": config.INPUT_DIR,
        }
        
        success = start_lightrag_server(
            host=config.LIGHTRAG_API_HOST,
            port=config.LIGHTRAG_API_PORT,
            api_key=config.LIGHTRAG_API_KEY,
            env_vars=env_vars
        )
        
        if not success:
            logger.error("Не удалось запустить LightRAG API сервер")
    
    # Создание клиента для LightRAG API
    lightrag_client = LightRAGClient(
        base_url=config.LIGHTRAG_API_BASE_URL,
        api_key=config.LIGHTRAG_API_KEY,
        timeout=config.TIMEOUT
    )
    
    # Проверка доступности LightRAG API
    health = await lightrag_client.check_health()
    if health.get("status") == "error":
        logger.warning(f"Предупреждение: {health.get('message')}")
    else:
        logger.info("LightRAG API доступен")
    
    # Этот контекст будет доступен во всех функциях MCP
    yield {"lightrag_client": lightrag_client}
    
    # Действия при завершении работы сервера
    logger.info("Завершение работы LightRAG MCP Server")
    
    # Остановка LightRAG API сервера при необходимости
    if config.LIGHTRAG_AUTOSTART and is_lightrag_server_running():
        logger.info("Остановка LightRAG API сервера")
        stop_lightrag_server()


# === MCP Ресурсы ===

@mcp.resource("document://{doc_id}")
async def get_document(doc_id: str, ctx: Context) -> Dict[str, Any]:
    """
    Получение информации о документе по ID.
    
    Args:
        doc_id (str): Идентификатор документа
        ctx (Context): Контекст MCP запроса
        
    Returns:
        Dict[str, Any]: Информация о документе
    """
    logger.info(f"Запрос информации о документе: {doc_id}")
    # TODO: Реализовать получение документа через LightRAG API
    # Этот эндпоинт требует дополнительной реализации в LightRAG API
    return {"id": doc_id, "status": "not_implemented"}


@mcp.resource("config://lightrag")
async def get_lightrag_config(ctx: Context) -> Dict[str, Any]:
    """
    Получение конфигурации LightRAG.
    
    Args:
        ctx (Context): Контекст MCP запроса
        
    Returns:
        Dict[str, Any]: Конфигурация LightRAG
    """
    logger.info("Запрос конфигурации LightRAG")
    
    # Маскируем конфиденциальные данные
    return {
        "api": {
            "host": config.LIGHTRAG_API_HOST,
            "port": config.LIGHTRAG_API_PORT,
            "autostart": config.LIGHTRAG_AUTOSTART,
            "base_url": config.LIGHTRAG_API_BASE_URL,
        },
        "llm": {
            "binding": config.LIGHTRAG_LLM_BINDING,
            "model": config.LIGHTRAG_LLM_MODEL,
            "binding_host": config.LIGHTRAG_LLM_BINDING_HOST,
        },
        "embedding": {
            "binding": config.LIGHTRAG_EMBEDDING_BINDING,
            "model": config.LIGHTRAG_EMBEDDING_MODEL,
            "binding_host": config.LIGHTRAG_EMBEDDING_BINDING_HOST,
        },
        "server": {
            "host": config.SERVER_HOST,
            "port": config.SERVER_PORT,
            "timeout": config.TIMEOUT,
        },
        "directories": {
            "working_dir": config.WORKING_DIR,
            "input_dir": config.INPUT_DIR,
        }
    }


@mcp.resource("ui://lightrag")
async def get_lightrag_ui_url(ctx: Context) -> str:
    """
    Возвращает URL для доступа к WebUI LightRAG.
    
    Args:
        ctx (Context): Контекст MCP запроса
        
    Returns:
        str: URL для доступа к WebUI
    """
    logger.info("Запрос URL для WebUI LightRAG")
    return f"http://{config.LIGHTRAG_API_HOST}:{config.LIGHTRAG_API_PORT}/"


# === MCP Инструменты ===

@mcp.tool()
async def query_document(query: str, ctx: Context, mode: str = "hybrid", top_k: int = 60, 
                       only_need_context: bool = False, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Выполнение поиска в документах через LightRAG API.
    
    Args:
        query (str): Текст запроса
        ctx (Context): Контекст MCP запроса
        mode (str): Режим поиска (hybrid, semantic, keyword)
        top_k (int): Количество результатов
        only_need_context (bool): Возвращать только контекст без создания ответа LLM
        system_prompt (Optional[str]): Системный промпт для LLM
        
    Returns:
        Dict[str, Any]: Результаты запроса
    """
    logger.info(f"Запрос к документам: {query}, режим: {mode}")
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
async def insert_document(text: Union[str, List[str]], ctx: Context, ids: Optional[List[str]] = None,
                        description: Optional[str] = None) -> Dict[str, Any]:
    """
    Добавление документа через LightRAG API.
    
    Args:
        text (Union[str, List[str]]): Текст или список текстов для добавления
        ctx (Context): Контекст MCP запроса
        ids (Optional[List[str]]): Список ID для текстов
        description (Optional[str]): Описание документов
        
    Returns:
        Dict[str, Any]: Результат операции
    """
    logger.info(f"Добавление документа, описание: {description}")
    lightrag_client = ctx.request_context.lifespan_context["lightrag_client"]
    
    result = await lightrag_client.insert_text(
        text=text,
        ids=ids,
        description=description
    )
    
    return result


@mcp.tool()
async def upload_document(file_path: str, ctx: Context, file_id: Optional[str] = None,
                        description: Optional[str] = None) -> Dict[str, Any]:
    """
    Загрузка файла в LightRAG.
    
    Args:
        file_path (str): Путь к файлу для загрузки
        ctx (Context): Контекст MCP запроса
        file_id (Optional[str]): ID для файла
        description (Optional[str]): Описание файла
        
    Returns:
        Dict[str, Any]: Результат операции
    """
    logger.info(f"Загрузка файла: {file_path}, описание: {description}")
    lightrag_client = ctx.request_context.lifespan_context["lightrag_client"]
    
    result = await lightrag_client.upload_file(
        file_path=file_path,
        file_id=file_id,
        description=description
    )
    
    return result


@mcp.tool()
async def delete_document(doc_id: str, ctx: Context) -> Dict[str, Any]:
    """
    Удаление документа из LightRAG.
    
    Args:
        doc_id (str): ID документа для удаления
        ctx (Context): Контекст MCP запроса
        
    Returns:
        Dict[str, Any]: Результат операции
    """
    logger.info(f"Удаление документа: {doc_id}")
    lightrag_client = ctx.request_context.lifespan_context["lightrag_client"]
    
    result = await lightrag_client.delete_document(doc_id=doc_id)
    
    return result


@mcp.tool()
async def check_lightrag_health(ctx: Context) -> Dict[str, Any]:
    """
    Проверка состояния LightRAG API.
    
    Args:
        ctx (Context): Контекст MCP запроса
        
    Returns:
        Dict[str, Any]: Статус сервера
    """
    logger.info("Проверка состояния LightRAG API")
    lightrag_client = ctx.request_context.lifespan_context["lightrag_client"]
    
    result = await lightrag_client.check_health()
    
    return result
