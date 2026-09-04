"""Gerenciador de migrações para o banco de dados."""

from __future__ import annotations

import logging
from pathlib import Path

from assistant.db.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """Erro ocorrido durante o processo de migração."""


class MigrationRunner:
    """Aplica migrações de esquema no banco de dados SQLite."""

    def __init__(self, db: DatabaseConnection, migrations_dir: str | Path | None = None) -> None:
        """Inicializa o gerenciador de migrações.

        Args:
            db: Conexão do banco de dados.
            migrations_dir: Diretório opcional contendo arquivos .sql.
                            Se não fornecido, procura por uma pasta 'migrations' próxima a este arquivo.
        """
        self._db = db
        if migrations_dir is None:
            self._migrations_dir = Path(__file__).parent / "migrations"
        else:
            self._migrations_dir = Path(migrations_dir).resolve()

    def _ensure_migrations_table(self) -> None:
        """Garante que a tabela de controle de migrações exista."""
        query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self._db.get_connection() as conn:
            conn.execute(query)

    def _get_applied_migrations(self) -> set[str]:
        """Obtém as migrações já aplicadas."""
        self._ensure_migrations_table()
        with self._db.get_connection() as conn:
            cursor = conn.execute("SELECT version FROM schema_migrations")
            return {row["version"] for row in cursor.fetchall()}

    def _get_available_migrations(self) -> list[Path]:
        """Obtém arquivos .sql ordenados alfabeticamente no diretório de migrações."""
        if not self._migrations_dir.exists():
            return []

        files = list(self._migrations_dir.glob("*.sql"))
        files.sort(key=lambda p: p.name)
        return files

    def run_migrations(self) -> int:
        """Aplica todas as migrações pendentes.

        Returns:
            Número de migrações aplicadas.

        Raises:
            MigrationError: Em caso de falha em alguma migração.
        """
        applied = self._get_applied_migrations()
        available = self._get_available_migrations()

        count = 0
        for migration_file in available:
            version = migration_file.name

            if version in applied:
                continue

            logger.info("Aplicando migração: %s", version)
            sql = migration_file.read_text(encoding="utf-8")

            try:
                with self._db.get_connection() as conn:
                    # executescript permite multiplos comandos (';')
                    conn.executescript(sql)
                    conn.execute(
                        "INSERT INTO schema_migrations (version) VALUES (?)",
                        (version,)
                    )
                count += 1
                logger.info("Migração %s aplicada com sucesso.", version)
            except Exception as e:
                logger.error("Erro ao aplicar migração %s: %s", version, e)
                raise MigrationError(f"Falha na migração {version}: {e}") from e

        return count
