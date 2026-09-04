-- Criação da tabela events
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    metadata TEXT, -- JSON payload
    FOREIGN KEY (execution_id) REFERENCES executions (id)
);
