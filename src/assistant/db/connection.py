"""Gerenciamento de conexão com o banco de dados SQLite."""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


class DatabaseConnection:
    """Gerencia a conexão com o banco de dados SQLite local."""

    def __init__(self, db_path: str = "assistant.db") -> None:
        """Inicializa o gerenciador.

        Args:
            db_path: Caminho para o arquivo do banco de dados.
                     Diretórios pai serão criados automaticamente.
        """
        self._db_path = Path(db_path).resolve()

        # Garante que o diretório pai existe
        if not self._db_path.parent.exists():
            self._db_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> str:
        """Retorna o caminho atual configurado para o banco."""
        return str(self._db_path)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Fornece uma conexão gerenciada para o banco de dados.

        Uso:
            with db.get_connection() as conn:
                conn.execute(...)
        """
        conn = sqlite3.connect(self._db_path)
        # Permite acessar colunas por nome
        conn.row_factory = sqlite3.Row

        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def test_connection(self) -> bool:
        """Testa se o banco de dados está acessível.

        Returns:
            True se conseguir conectar e executar uma query simples, False caso contrário.
        """
        try:
            with self.get_connection() as conn:
                conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False
