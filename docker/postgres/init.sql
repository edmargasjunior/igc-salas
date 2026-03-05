-- Inicialização do banco PostgreSQL para IGC Salas
-- Configurações de performance e charset

-- Configurar timezone
SET timezone = 'America/Sao_Paulo';

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- Busca por similaridade de texto
CREATE EXTENSION IF NOT EXISTS unaccent; -- Busca sem acentos
CREATE EXTENSION IF NOT EXISTS btree_gin; -- Índices GIN

-- Configurar search path
ALTER DATABASE igc_salas_db SET search_path TO public;
