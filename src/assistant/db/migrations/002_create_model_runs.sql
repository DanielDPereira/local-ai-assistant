-- Criação da tabela model_runs
CREATE TABLE IF NOT EXISTS model_runs (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    model TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    duration_ms INTEGER,
    prompt TEXT,
    response TEXT,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    tokens_per_second REAL DEFAULT 0.0,
    success BOOLEAN DEFAULT 0,
    error_message TEXT,
    FOREIGN KEY (execution_id) REFERENCES executions (id)
);
