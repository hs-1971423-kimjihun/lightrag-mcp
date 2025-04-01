"""
Модуль для управления процессом LightRAG API.
"""

import os
import signal
import subprocess
import atexit
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class LightRAGProcessManager:
    """Менеджер процесса LightRAG API."""
    
    def __init__(self):
        """Инициализация менеджера процесса."""
        self.process: Optional[subprocess.Popen] = None
    
    def start(self, cmd: List[str], env: Optional[Dict[str, str]] = None) -> subprocess.Popen:
        """
        Запуск процесса LightRAG API.
        
        Args:
            cmd (List[str]): Команда для запуска процесса
            env (Optional[Dict[str, str]]): Переменные окружения для процесса
            
        Returns:
            subprocess.Popen: Запущенный процесс
        """
        if self.process and self.is_running():
            logger.warning("Процесс LightRAG API уже запущен")
            return self.process
        
        logger.info(f"Запуск LightRAG API: {' '.join(cmd)}")
        
        # Объединяем текущее окружение с переданными переменными
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
        
        # Запуск процесса с перенаправлением вывода в логи
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=process_env
        )
        
        # Регистрация функции для остановки процесса при завершении работы
        atexit.register(self.stop)
        
        # Запускаем логирование вывода в отдельных потоках
        self._start_logging()
        
        logger.info(f"Процесс LightRAG API запущен с PID: {self.process.pid}")
        return self.process
    
    def _start_logging(self):
        """Запуск логирования вывода процесса в отдельных потоках."""
        if self.process is None:
            return
        
        import threading
        
        def log_output(stream, level):
            for line in iter(stream.readline, ''):
                if level == logging.INFO:
                    logger.info(f"LightRAG API: {line.strip()}")
                else:
                    logger.error(f"LightRAG API Error: {line.strip()}")
            
            if not stream.closed:
                stream.close()
        
        # Запуск потоков для логирования stdout и stderr
        if self.process.stdout:
            threading.Thread(
                target=log_output,
                args=(self.process.stdout, logging.INFO),
                daemon=True
            ).start()
        
        if self.process.stderr:
            threading.Thread(
                target=log_output,
                args=(self.process.stderr, logging.ERROR),
                daemon=True
            ).start()
    
    def stop(self):
        """Остановка процесса LightRAG API."""
        if self.process and self.is_running():
            logger.info(f"Остановка процесса LightRAG API (PID: {self.process.pid})")
            
            try:
                # Отправляем сигнал SIGTERM для корректного завершения
                os.kill(self.process.pid, signal.SIGTERM)
                
                # Даем процессу время на завершение (3 секунды)
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # Если процесс не завершился за отведенное время, принудительно завершаем
                    logger.warning("Процесс не завершился вовремя, принудительное завершение")
                    os.kill(self.process.pid, signal.SIGKILL)
                    self.process.wait()
            except (ProcessLookupError, OSError) as e:
                logger.error(f"Ошибка при остановке процесса: {str(e)}")
            
            # Закрываем потоки вывода, если они еще открыты
            if self.process.stdout and not self.process.stdout.closed:
                self.process.stdout.close()
            
            if self.process.stderr and not self.process.stderr.closed:
                self.process.stderr.close()
            
            # Снимаем регистрацию функции остановки
            atexit.unregister(self.stop)
            
            logger.info("Процесс LightRAG API остановлен")
            self.process = None
    
    def is_running(self) -> bool:
        """
        Проверка, запущен ли процесс.
        
        Returns:
            bool: True, если процесс запущен, иначе False
        """
        if self.process is None:
            return False
        
        # Проверяем, запущен ли процесс (poll() возвращает None для запущенных процессов)
        return self.process.poll() is None
    
    def get_pid(self) -> Optional[int]:
        """
        Получение PID процесса.
        
        Returns:
            Optional[int]: PID процесса или None, если процесс не запущен
        """
        if self.process and self.is_running():
            return self.process.pid
        return None


# Глобальный экземпляр менеджера процесса
process_manager = LightRAGProcessManager()

def start_lightrag_server(host: str = "localhost", port: int = 9621, 
                        api_key: Optional[str] = None, 
                        env_vars: Optional[Dict[str, str]] = None) -> bool:
    """
    Запуск LightRAG API сервера.
    
    Args:
        host (str): Хост для прослушивания
        port (int): Порт для прослушивания
        api_key (Optional[str]): API ключ для сервера
        env_vars (Optional[Dict[str, str]]): Дополнительные переменные окружения
        
    Returns:
        bool: True, если сервер был успешно запущен, иначе False
    """
    cmd = [
        "lightrag-server",
        "--host", host,
        "--port", str(port)
    ]
    
    if api_key:
        cmd.extend(["--key", api_key])
    
    try:
        process_manager.start(cmd, env=env_vars)
        return process_manager.is_running()
    except Exception as e:
        logger.error(f"Ошибка при запуске LightRAG API сервера: {str(e)}")
        return False

def stop_lightrag_server() -> bool:
    """
    Остановка LightRAG API сервера.
    
    Returns:
        bool: True, если сервер был успешно остановлен или не был запущен, иначе False
    """
    try:
        process_manager.stop()
        return True
    except Exception as e:
        logger.error(f"Ошибка при остановке LightRAG API сервера: {str(e)}")
        return False

def is_lightrag_server_running() -> bool:
    """
    Проверка, запущен ли LightRAG API сервер.
    
    Returns:
        bool: True, если сервер запущен, иначе False
    """
    return process_manager.is_running()
