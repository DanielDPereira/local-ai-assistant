-- Criação da tabela tool_runs
CREATE TABLE IF NOT EXISTS tool_runs (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    operation TEXT,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    duration_ms INTEGER,
    success BOOLEAN DEFAULT 0,
    error_message TEXT,
    FOREIGN KEY (execution_id) REFERENCES executions (id)
);
