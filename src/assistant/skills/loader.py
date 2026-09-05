"""Carregador de Skills do sistema."""

import json
from pathlib import Path

from assistant.skills.models import Skill
from assistant.skills.validator import SkillValidationError, SkillValidator


class SkillLoader:
    """Descobre e carrega Skills a partir do sistema de arquivos."""

    def __init__(self, skills_dir: str | Path) -> None:
        """Inicializa o carregador.
        
        Args:
            skills_dir: Caminho para o diretório de skills.
        """
        self.skills_dir = Path(skills_dir)

    def discover(self) -> list[str]:
        """Descobre todas as skills disponíveis (arquivos .json).
        
        Returns:
            Lista com os nomes dos arquivos de skill (sem extensão).
        """
        if not self.skills_dir.exists() or not self.skills_dir.is_dir():
            return []

        return [f.stem for f in self.skills_dir.glob("*.json")]

    def load(self, skill_name: str) -> Skill:
        """Carrega e valida uma Skill pelo nome.
        
        Args:
            skill_name: Nome do arquivo da skill (sem extensão).
            
        Returns:
            Objeto Skill populado.
            
        Raises:
            FileNotFoundError: Se o arquivo não existir.
            SkillValidationError: Se o arquivo for inválido.
        """
        skill_path = self.skills_dir / f"{skill_name}.json"

        if not skill_path.exists():
            raise FileNotFoundError(f"Skill não encontrada: {skill_path}")

        try:
            with open(skill_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SkillValidationError(f"Formato JSON inválido: {e}") from e

        SkillValidator.validate_dict(data)

        return Skill(
            name=data["name"],
            description=data["description"],
            instructions=data["instructions"],
            version=data.get("version", "1.0"),
            metadata=data.get("metadata", {})
        )
