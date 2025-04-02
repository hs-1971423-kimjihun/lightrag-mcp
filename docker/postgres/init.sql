-- Инициализация базы данных для LightRAG

-- Включение расширения pgvector для векторной БД
CREATE EXTENSION IF NOT EXISTS vector;

-- Создание рабочей схемы
CREATE SCHEMA IF NOT EXISTS lightrag;

-- Проверка установки расширений
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
