"""Testes para o gerenciador de migrações."""

from __future__ import annotations

from pathlib import Path

import pytest

from assistant.db.connection import DatabaseConnection
from assistant.db.migrations_runner import MigrationError, MigrationRunner


class TestMigrationRunner:
    """Testes para a classe MigrationRunner."""

    def test_run_migrations(self, tmp_path: Path) -> None:
        """Verifica a execução de migrações válidas."""
        db_file = tmp_path / "test.db"
        migrations_dir = tmp_path / "migrations"
        migrations_dir.mkdir()

        # Cria migrações
        (migrations_dir / "001_initial.sql").write_text("CREATE TABLE users (id INTEGER PRIMARY KEY);")
        (migrations_dir / "002_add_name.sql").write_text("ALTER TABLE users ADD COLUMN name TEXT;")

        db = DatabaseConnection(db_path=str(db_file))
        runner = MigrationRunner(db=db, migrations_dir=migrations_dir)

        # Executa a primeira vez (aplica 2)
        count = runner.run_migrations()
        assert count == 2

        # Verifica se as tabelas foram criadas
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            assert cursor.fetchone() is not None

            cursor = conn.execute("PRAGMA table_info(users)")
            columns = [row["name"] for row in cursor.fetchall()]
            assert "id" in columns
            assert "name" in columns

        # Executa a segunda vez (não deve aplicar nenhuma)
        count_again = runner.run_migrations()
        assert count_again == 0

    def test_run_migrations_failure(self, tmp_path: Path) -> None:
        """Verifica se uma migração com erro falha corretamente."""
        db_file = tmp_path / "fail.db"
        migrations_dir = tmp_path / "migrations_fail"
        migrations_dir.mkdir()

        # Sql inválido
        (migrations_dir / "001_invalid.sql").write_text("CREATE TABLE X (;")

        db = DatabaseConnection(db_path=str(db_file))
        runner = MigrationRunner(db=db, migrations_dir=migrations_dir)

        with pytest.raises(MigrationError):
            runner.run_migrations()

        # Verifica que não marcou como aplicada
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT count(*) as c FROM schema_migrations")
            assert cursor.fetchone()["c"] == 0

    def test_real_migrations(self, tmp_path: Path) -> None:
        """Verifica se as migrações reais do projeto rodam com sucesso num banco vazio."""
        db_file = tmp_path / "real.db"
        db = DatabaseConnection(db_path=str(db_file))
        # runner sem passar diretório usará as migrações reais do código-fonte
        runner = MigrationRunner(db=db)

        count = runner.run_migrations()
        assert count >= 1  # Temos pelo menos 1 migração real

        # Confirma que a tabela schema_migrations registrou
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT count(*) as c FROM schema_migrations")
            assert cursor.fetchone()["c"] == count

            # Garante que a tabela executions existe
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='executions'")
            assert cursor.fetchone() is not None

            # Garante que a tabela model_runs existe
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_runs'")
            assert cursor.fetchone() is not None
