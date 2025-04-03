"""
Клиент для взаимодействия с LightRAG API.
"""

import logging
from pathlib import Path
from typing import Any, Awaitable, Callable, List, TypeVar, Union

from lightrag_mcp.client.light_rag_server_api_client.api.default import async_get_health
from lightrag_mcp.client.light_rag_server_api_client.api.documents import (
    async_get_documents,
    async_get_pipeline_status,
    async_insert_batch,
    async_insert_document,
    async_insert_file,
    async_insert_texts,
    async_scan_for_new_documents,
    async_upload_document,
)
from lightrag_mcp.client.light_rag_server_api_client.api.graph import (
    async_get_graph_labels,
)
from lightrag_mcp.client.light_rag_server_api_client.api.query import (
    async_query_document,
)
from lightrag_mcp.client.light_rag_server_api_client.client import AuthenticatedClient
from lightrag_mcp.client.light_rag_server_api_client.models import (
    BodyInsertBatchDocumentsFileBatchPost,
    BodyInsertFileDocumentsFilePost,
    BodyUploadToInputDirDocumentsUploadPost,
    DocsStatusesResponse,
    HTTPValidationError,
    InsertResponse,
    InsertTextRequest,
    InsertTextsRequest,
    PipelineStatusResponse,
    QueryRequest,
    QueryRequestMode,
    QueryResponse,
)
from lightrag_mcp.client.light_rag_server_api_client.types import UNSET, File

from .client.light_rag_server_api_client.errors import UnexpectedStatus

logger = logging.getLogger(__name__)

# Определение типа для функций API
T = TypeVar("T", covariant=True)
ApiFunc = Callable[..., Awaitable[T]]


class LightRAGClient:
    """
    Клиент для взаимодействия с LightRAG API.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str = "NOT USED",
    ):
        """
        Инициализация клиента LightRAG API.

        Args:
            base_url (str): Базовый URL API.
            api_key (str): API ключ (токен).
        """
        self.base_url = base_url
        self.api_key = api_key
        self.client = AuthenticatedClient(base_url=base_url, token=api_key, verify_ssl=False)
        logger.info(f"Инициализирован клиент LightRAG API: {base_url}")

    async def _handle_exception(self, e: Exception, operation_name: str) -> None:
        """
        Обработка исключений при вызове API.

        Args:
            e: Исключение
            operation_name: Название операции для логирования

        Raises:
            Exception: Пробрасывает исключение дальше
        """
        if isinstance(e, UnexpectedStatus):
            # Используем !r для безопасного форматирования бинарных данных
            logger.error(f"Ошибка HTTP при {operation_name}: {e.status_code} - {e.content!r}")
        else:
            logger.error(f"Ошибка при {operation_name}: {str(e)}")

    async def _call_api(self, api_func: ApiFunc[T], operation_name: str, **kwargs) -> T:
        """
        Универсальный метод для вызова API функций.

        Args:
            api_func: Функция API для вызова
            operation_name: Название операции для логирования
            **kwargs: Аргументы для передачи в функцию API

        Returns:
            T: Результат операции (тип зависит от вызываемой функции API)
        """
        try:
            return await api_func(**kwargs)
        except Exception as e:
            await self._handle_exception(e, operation_name)
            raise

    async def query(
        self,
        query_text: str,
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
    ) -> Union[QueryResponse, HTTPValidationError, None]:
        """
        Выполнение запроса к LightRAG API.

        Args:
            query_text (str): Текст запроса
            mode (str, optional): Режим поиска (global, hybrid, local, mix, naive). По умолчанию "mix".
            top_k (int, optional): Количество результатов. По умолчанию 10.
            only_need_context (bool, optional): Возвращать только контекст без создания ответа LLM. По умолчанию False.
            only_need_prompt (bool, optional): Если True, возвращает только сгенерированный запрос без создания ответа. По умолчанию False.
            response_type (str, optional): Определяет формат ответа. Примеры: 'Несколько абзацев', 'Один абзац', 'Маркированный список'.
            max_token_for_text_unit (int, optional): Максимальное количество токенов, разрешенное для каждого полученного текстового фрагмента. По умолчанию 1000.
            max_token_for_global_context (int, optional): Максимальное количество токенов, выделенное для описания связей в глобальном поиске. По умолчанию 1000.
            max_token_for_local_context (int, optional): Максимальное количество токенов, выделенное для описания сущностей в локальном поиске. По умолчанию 1000.
            hl_keywords (list[str], optional): Список ключевых слов высокого уровня для приоритизации в поиске.
            ll_keywords (list[str], optional): Список ключевых слов низкого уровня для уточнения фокуса поиска.
            history_turns (int, optional): Количество полных ходов разговора (пары пользователь-ассистент), которые нужно учитывать в контексте ответа. По умолчанию 10.

        Returns:
            Union[QueryResponse, HTTPValidationError, None]: Результаты запроса
        """
        logger.debug("Выполнение запроса к LightRAG")

        query_request = QueryRequest(
            query=query_text,
            mode=QueryRequestMode(mode) if mode else UNSET,
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

        return await self._call_api(
            api_func=async_query_document,
            operation_name="выполнении запроса",
            client=self.client,
            body=query_request,
        )

    async def insert_text(
        self,
        text: Union[str, List[str]],
    ) -> Union[InsertResponse, HTTPValidationError, None]:
        """
        Добавление текста в LightRAG.

        Args:
            text (Union[str, List[str]]): Текст или список текстов для добавления

        Returns:
            Union[InsertResponse, HTTPValidationError]: Результат операции
        """
        logger.debug("Добавление текста в LightRAG")

        if isinstance(text, list):
            # Если передан список текстов, используем insert_texts
            return await self._call_api(
                api_func=async_insert_texts,
                operation_name="добавлении текстов",
                client=self.client,
                body=InsertTextsRequest(
                    texts=text,
                ),
            )
        else:
            # Если передан один текст, используем insert_document
            return await self._call_api(
                api_func=async_insert_document,
                operation_name="добавлении текста",
                client=self.client,
                body=InsertTextRequest(
                    text=text,
                ),
            )

    async def upload_document(self, file_path: str) -> Union[Any, HTTPValidationError]:
        """
        Загрузка документов из файла.

        Args:
            file_path (str): Путь к файлу.

        Returns:
            Union[Any, HTTPValidationError]: Результат операции.
        """
        logger.debug(f"Загрузка документов из файла: {file_path}")

        if not file_path:
            logger.error("Не указан путь к файлу")
            raise ValueError("Не указан путь к файлу")

        try:
            with open(file_path, "rb") as f:
                upload_request = BodyUploadToInputDirDocumentsUploadPost(file=File(payload=f))
                result = await self._call_api(
                    api_func=async_upload_document,
                    operation_name=f"загрузке файла {file_path}",
                    client=self.client,
                    body=upload_request,
                )
                return result
        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            raise
        except Exception as e:
            await self._handle_exception(e, f"загрузке файла {file_path}")
            raise

    async def insert_file(self, file_path: str) -> Union[HTTPValidationError, InsertResponse, None]:
        """
        Добавление документа из файла (аналогично upload_document, но другой эндпоинт).

        Args:
            file_path (str): Путь к файлу.

        Returns:
            Union[InsertResponse, HTTPValidationError]: Результат операции.
        """
        logger.debug(f"Добавление файла: {file_path}")

        # Проверка входных параметров
        if not file_path:
            logger.error("Не указан путь к файлу")
            raise ValueError("Не указан путь к файлу")

        try:
            with open(file_path, "rb") as f:
                # Используем правильный класс BodyInsertFileDocumentsFilePost
                insert_file_request = BodyInsertFileDocumentsFilePost(file=File(payload=f))
                result = await self._call_api(
                    api_func=async_insert_file,
                    operation_name=f"добавлении файла {file_path}",
                    client=self.client,
                    body=insert_file_request,
                )
                return result
        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            raise
        except Exception as e:
            await self._handle_exception(e, f"добавлении файла {file_path}")
            raise

    async def insert_batch(
        self, directory_path: str
    ) -> Union[InsertResponse, HTTPValidationError, None]:
        """
        Добавление пакета документов из директории.

        Args:
            directory_path (str): Путь к директории.

        Returns:
            Union[InsertResponse, HTTPValidationError]: Результат операции.
        """
        logger.debug(f"Добавление пакета файлов из директории: {directory_path}")

        # Проверка входных параметров
        if not directory_path:
            logger.error("Не указан путь к директории")
            raise ValueError("Не указан путь к директории")

        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Директория не существует или не является директорией: {directory_path}")
            raise ValueError(
                f"Директория не существует или не является директорией: {directory_path}"
            )

        # Получаем список всех файлов в директории (без рекурсии)
        files_list = []
        for file_path in directory.iterdir():
            if file_path.is_file():
                try:
                    # Открываем файл и добавляем его в список
                    with open(file_path, "rb") as f:
                        files_list.append(File(payload=f))
                except Exception as e:
                    logger.warning(f"Не удалось открыть файл {file_path}: {e}")

        if not files_list:
            logger.warning(f"В директории {directory_path} не найдено файлов")
            return None

        try:
            # Создаем запрос для пакетной обработки
            batch_request = BodyInsertBatchDocumentsFileBatchPost(files=files_list)

            # Отправляем запрос
            result = await self._call_api(
                api_func=async_insert_batch,
                operation_name=f"добавлении пакета из {directory_path}",
                client=self.client,
                body=batch_request,
            )
            return result
        except Exception as e:
            await self._handle_exception(e, f"добавлении пакета из {directory_path}")
            raise

    async def scan_for_new_documents(self) -> Union[Any, HTTPValidationError]:
        """
        Запуск сканирования директории на наличие новых документов.

        Returns:
            Union[Any, HTTPValidationError]: Результат операции.
        """
        logger.debug("Запуск сканирования директории")

        # Функция async_scan_for_new_documents не принимает параметр body, только client
        return await self._call_api(
            api_func=async_scan_for_new_documents,
            operation_name="сканировании директории",
            client=self.client,
        )

    async def get_documents(
        self,
    ) -> Union[DocsStatusesResponse, HTTPValidationError, None]:
        """
        Получение списка всех загруженных документов.

        Returns:
            Union[DocsStatusesResponse, HTTPValidationError]: Список документов.
        """
        logger.debug("Получение списка документов...")
        return await self._call_api(
            api_func=async_get_documents,
            operation_name="получении списка документов",
            client=self.client,
        )

    async def get_pipeline_status(
        self,
    ) -> Union[PipelineStatusResponse, HTTPValidationError, None]:
        """
        Получение статуса обработки документов в пайплайне.

        Returns:
            Union[PipelineStatusResponse, HTTPValidationError]: Статус пайплайна.
        """
        logger.debug("Получение статуса пайплайна...")
        return await self._call_api(
            api_func=async_get_pipeline_status,
            operation_name="получении статуса обработки",
            client=self.client,
        )

    async def get_graph_labels(self) -> Union[Any, HTTPValidationError]:
        """
        Получение меток (типов узлов и связей) из графа знаний.

        Returns:
            Union[Any, HTTPValidationError]: Метки графа.
        """
        logger.debug("Получение меток графа...")
        return await self._call_api(
            api_func=async_get_graph_labels,
            operation_name="получении меток графа",
            client=self.client,
        )

    async def get_health(self) -> Union[Any, HTTPValidationError]:
        """
        Проверка состояния здоровья сервиса LightRAG.

        Returns:
            Union[Any, HTTPValidationError]: Статус здоровья.
        """
        logger.debug("Проверка состояния здоровья сервиса...")
        return await self._call_api(
            api_func=async_get_health,
            operation_name="проверке состояния",
            client=self.client,
        )

    async def close(self):
        """Закрытие HTTP клиента."""
        await self.client.get_async_client().aclose()
        logger.info("Клиент LightRAG API закрыт.")
