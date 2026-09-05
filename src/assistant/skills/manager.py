"""Gerenciador central de Skills."""

from pathlib import Path

from assistant.skills.loader import SkillLoader
from assistant.skills.models import Skill
from assistant.skills.telemetry import SkillTelemetry


class SkillManager:
    """Fachada para descoberta, carregamento, validação e telemetria de Skills."""

    def __init__(self, skills_dir: str | Path | None = None, telemetry_file: str | Path | None = None) -> None:
        """Inicializa o gerenciador.

        Args:
            skills_dir: Diretório onde as skills estão salvas. Padrão: ~/.local-ai-assistant/skills
            telemetry_file: Arquivo de log para telemetria. Padrão: ~/.local-ai-assistant/telemetry.jsonl
        """
        default_base_dir = Path.home() / ".local-ai-assistant"

        self.skills_dir = Path(skills_dir) if skills_dir else (default_base_dir / "skills")
        self.telemetry_file = Path(telemetry_file) if telemetry_file else (default_base_dir / "telemetry.jsonl")

        # Garante a existência do diretório de skills
        self.skills_dir.mkdir(parents=True, exist_ok=True)

        self.loader = SkillLoader(self.skills_dir)
        self.telemetry = SkillTelemetry(self.telemetry_file)

        # Cache em memória
        self._loaded_skills: dict[str, Skill] = {}

    def discover_skills(self) -> list[str]:
        """Retorna uma lista de nomes das skills disponíveis no diretório."""
        return self.loader.discover()

    def apply_skill(self, skill_name: str, context: str = "") -> Skill:
        """Carrega (se não estiver em cache), valida e registra o uso da skill.

        Args:
            skill_name: Nome da skill.
            context: Contexto de uso para telemetria.

        Returns:
            O modelo validado da Skill para ser injetado no prompt do Agent.

        Raises:
            FileNotFoundError: Se a skill não existir.
            SkillValidationError: Se a skill tiver formato inválido.
        """
        if skill_name not in self._loaded_skills:
            self._loaded_skills[skill_name] = self.loader.load(skill_name)

        skill = self._loaded_skills[skill_name]

        # Registra telemetria de uso
        self.telemetry.record_usage(skill_name, context)

        return skill
