"""Testes para o gerenciamento de conexão do banco de dados."""

from __future__ import annotations

from pathlib import Path

from assistant.db.connection import DatabaseConnection


class TestDatabaseConnection:
    """Testes para a classe DatabaseConnection."""

    def test_database_creation(self, tmp_path: Path) -> None:
        """Verifica se o banco de dados e os diretórios são criados."""
        db_file = tmp_path / "data" / "assistant.db"

        # Inicializa a conexão e garante que diretórios não existem ainda
        assert not db_file.parent.exists()

        db = DatabaseConnection(db_path=str(db_file))

        # O construtor deve criar o diretório pai
        assert db_file.parent.exists()

        # Verifica se criar a conexão cria o arquivo
        with db.get_connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")

        assert db_file.exists()
        assert db_file.is_file()

    def test_test_connection_success(self, tmp_path: Path) -> None:
        """Verifica se test_connection retorna True para um banco válido."""
        db_file = tmp_path / "assistant.db"
        db = DatabaseConnection(db_path=str(db_file))

        assert db.test_connection() is True

    def test_test_connection_failure(self, tmp_path: Path) -> None:
        """Verifica falha no teste de conexão."""
        # Se for um diretório em vez de arquivo, deve falhar
        db_file = tmp_path / "assistant.db"
        db_file.mkdir()

        db = DatabaseConnection(db_path=str(db_file))
        assert db.test_connection() is False

    def test_connection_rollback_on_error(self, tmp_path: Path) -> None:
        """Verifica se a transação sofre rollback em caso de exceção."""
        db_file = tmp_path / "assistant.db"
        db = DatabaseConnection(db_path=str(db_file))

        with db.get_connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")

        try:
            with db.get_connection() as conn:
                conn.execute("INSERT INTO test (value) VALUES ('a')")
                raise ValueError("Force rollback")
        except ValueError:
            pass

        # O registro 'a' não deve existir pois a transação sofreu rollback
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM test")
            results = cursor.fetchall()
            assert len(results) == 0
