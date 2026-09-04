-- Criação da tabela harness_iterations
CREATE TABLE IF NOT EXISTS harness_iterations (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    iteration_number INTEGER NOT NULL,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    duration_ms INTEGER,
    status TEXT NOT NULL,
    retry BOOLEAN DEFAULT 0,
    error TEXT,
    FOREIGN KEY (execution_id) REFERENCES executions (id)
);
