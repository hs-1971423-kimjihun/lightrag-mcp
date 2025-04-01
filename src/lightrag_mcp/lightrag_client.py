"""
Клиент для взаимодействия с LightRAG API.
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any

import httpx

logger = logging.getLogger(__name__)

class LightRAGClient:
    """Клиент для взаимодействия с LightRAG API."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 150):
        """
        Инициализация клиента LightRAG API.
        
        Args:
            base_url (str): Базовый URL для API (например, http://localhost:9621)
            api_key (Optional[str]): API ключ для авторизации, если требуется
            timeout (int): Таймаут для запросов в секундах
        """
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {}
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    async def query(self, query_text: str, mode: str = "hybrid", 
                  top_k: int = 60, only_need_context: bool = False,
                  system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Выполнение запроса к LightRAG.
        
        Args:
            query_text (str): Текст запроса
            mode (str): Режим поиска (hybrid, semantic, keyword)
            top_k (int): Количество результатов
            only_need_context (bool): Возвращать только контекст без создания ответа LLM
            system_prompt (Optional[str]): Системный промпт для LLM
            
        Returns:
            Dict[str, Any]: Ответ от LightRAG API
        """
        url = f"{self.base_url}/query"
        
        payload = {
            "query": query_text,
            "mode": mode,
            "top_k": top_k,
            "only_need_context": only_need_context
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        logger.debug(f"Отправка запроса к LightRAG API: {url} с данными: {payload}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка HTTP при запросе {url}: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Ошибка при запросе {url}: {str(e)}")
            raise
    
    async def query_stream(self, query_text: str, mode: str = "hybrid", 
                         top_k: int = 60, only_need_context: bool = False,
                         system_prompt: Optional[str] = None):
        """
        Потоковый запрос к LightRAG API.
        
        Args:
            query_text (str): Текст запроса
            mode (str): Режим поиска (hybrid, semantic, keyword)
            top_k (int): Количество результатов
            only_need_context (bool): Возвращать только контекст без создания ответа LLM
            system_prompt (Optional[str]): Системный промпт для LLM
            
        Yields:
            str: Чанки ответа от LightRAG API
        """
        url = f"{self.base_url}/query_stream"
        
        payload = {
            "query": query_text,
            "mode": mode,
            "top_k": top_k,
            "only_need_context": only_need_context
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        logger.debug(f"Отправка потокового запроса к LightRAG API: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=payload, headers=self.headers) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            if line.startswith("data: "):
                                data = line[6:]  # Убираем "data: " из начала строки
                                try:
                                    parsed_data = json.loads(data)
                                    yield parsed_data.get("text", "")
                                except json.JSONDecodeError:
                                    logger.warning(f"Не удалось разобрать JSON из строки: {data}")
                                    yield data
                            else:
                                yield line
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка HTTP при потоковом запросе {url}: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Ошибка при потоковом запросе {url}: {str(e)}")
            raise
    
    async def insert_text(self, text: Union[str, List[str]], 
                        ids: Optional[List[str]] = None,
                        description: Optional[str] = None) -> Dict[str, Any]:
        """
        Добавление текста в LightRAG.
        
        Args:
            text (Union[str, List[str]]): Текст или список текстов для добавления
            ids (Optional[List[str]]): Список ID для текстов
            description (Optional[str]): Описание документов
            
        Returns:
            Dict[str, Any]: Результат операции
        """
        url = f"{self.base_url}/documents/text"
        
        payload = {
            "text": text
        }
        
        if ids:
            payload["ids"] = ids
        
        if description:
            payload["description"] = description
        
        logger.debug(f"Добавление текста в LightRAG: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка HTTP при добавлении текста: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Ошибка при добавлении текста: {str(e)}")
            raise
    
    async def upload_file(self, file_path: str, 
                        file_id: Optional[str] = None,
                        description: Optional[str] = None) -> Dict[str, Any]:
        """
        Загрузка файла в LightRAG.
        
        Args:
            file_path (str): Путь к файлу для загрузки
            file_id (Optional[str]): ID для файла
            description (Optional[str]): Описание файла
            
        Returns:
            Dict[str, Any]: Результат операции
        """
        url = f"{self.base_url}/documents/upload"
        
        files = {"file": open(file_path, "rb")}
        data = {}
        
        if file_id:
            data["id"] = file_id
        
        if description:
            data["description"] = description
        
        logger.debug(f"Загрузка файла в LightRAG: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, files=files, data=data, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка HTTP при загрузке файла: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Ошибка при загрузке файла: {str(e)}")
            raise
        finally:
            files["file"].close()
    
    async def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Удаление документа из LightRAG.
        
        Args:
            doc_id (str): ID документа для удаления
            
        Returns:
            Dict[str, Any]: Результат операции
        """
        url = f"{self.base_url}/documents/{doc_id}"
        
        logger.debug(f"Удаление документа из LightRAG: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка HTTP при удалении документа: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Ошибка при удалении документа: {str(e)}")
            raise
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Проверка состояния LightRAG API.
        
        Returns:
            Dict[str, Any]: Статус сервера
        """
        url = f"{self.base_url}/health"
        
        logger.debug(f"Проверка состояния LightRAG API: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(f"Ошибка при проверке состояния: {str(e)}")
            return {"status": "error", "message": "LightRAG API недоступен"}
