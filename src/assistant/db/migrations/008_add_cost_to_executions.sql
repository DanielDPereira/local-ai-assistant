-- Adiciona colunas de custo e energia à tabela executions
ALTER TABLE executions ADD COLUMN estimated_energy_kwh REAL DEFAULT 0.0;
ALTER TABLE executions ADD COLUMN estimated_cost REAL DEFAULT 0.0;
