-- Criação da tabela validation_runs
CREATE TABLE IF NOT EXISTS validation_runs (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    validation_type TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    duration_ms INTEGER,
    status TEXT NOT NULL,
    exit_code INTEGER DEFAULT 0,
    error TEXT,
    FOREIGN KEY (execution_id) REFERENCES executions (id)
);
