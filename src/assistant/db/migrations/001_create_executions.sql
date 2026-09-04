-- Criação da tabela executions
CREATE TABLE IF NOT EXISTS executions (
    id TEXT PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    duration_ms INTEGER,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL,
    model TEXT NOT NULL,
    workspace TEXT,
    iterations INTEGER DEFAULT 0,
    tool_calls INTEGER DEFAULT 0,
    retries INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT 0,
    human_intervention BOOLEAN DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0
);
