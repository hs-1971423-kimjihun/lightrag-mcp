-- Инициализация базы данных для LightRAG

-- Включение расширения pgvector для векторной БД
CREATE EXTENSION IF NOT EXISTS vector;

-- Проверка установки расширений
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
