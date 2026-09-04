-- Criação da tabela hardware_samples
CREATE TABLE IF NOT EXISTS hardware_samples (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    cpu_percent REAL NOT NULL,
    ram_percent REAL NOT NULL,
    ram_used_mb REAL NOT NULL,
    gpu_percent REAL,
    gpu_memory_used_mb REAL,
    gpu_memory_percent REAL,
    gpu_temperature REAL,
    power_watts REAL,
    FOREIGN KEY (execution_id) REFERENCES executions (id)
);
