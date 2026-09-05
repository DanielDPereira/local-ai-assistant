"""Validação de estrutura e metadados de Skills."""

from typing import Any, ClassVar


class SkillValidationError(Exception):
    """Erro lançado quando uma Skill é inválida."""
    pass


class SkillValidator:
    """Valida a estrutura de uma Skill."""

    REQUIRED_FIELDS: ClassVar[list[str]] = ["name", "description", "instructions"]

    @classmethod
    def validate_dict(cls, data: dict[str, Any]) -> None:
        """Valida se o dicionário possui todos os campos obrigatórios e formatos corretos.

        Args:
            data: Dicionário com os dados da Skill.

        Raises:
            SkillValidationError: Se a validação falhar.
        """
        if not isinstance(data, dict):
            raise SkillValidationError("O formato do arquivo deve ser um dicionário/objeto JSON.")

        for field in cls.REQUIRED_FIELDS:
            if field not in data:
                raise SkillValidationError(f"Campo obrigatório ausente: '{field}'.")
            if not isinstance(data[field], str) or not data[field].strip():
                raise SkillValidationError(f"Campo '{field}' deve ser uma string não vazia.")

        version = data.get("version")
        if version is not None and not isinstance(version, str):
            raise SkillValidationError("Campo 'version' deve ser uma string.")

        metadata = data.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise SkillValidationError("Campo 'metadata' deve ser um dicionário/objeto.")
