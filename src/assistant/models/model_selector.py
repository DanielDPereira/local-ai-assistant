"""Seleção de modelos por tipo de tarefa.

Permite selecionar o modelo correto com base no tipo de tarefa,
utilizando a configuração centralizada. Alterar o modelo exige
apenas alterar a configuração (variável de ambiente ou padrão).
"""

from __future__ import annotations

from enum import Enum

from assistant.config.settings import ModelSettings


class TaskType(Enum):
    """Tipo de tarefa para seleção de modelo."""

    GENERAL = "general"
    CODING = "coding"
    LIGHTWEIGHT = "lightweight"


class ModelSelector:
    """Seleciona o modelo apropriado com base no tipo de tarefa.

    A seleção é baseada na configuração centralizada (ModelSettings).
    Nenhum nome de modelo é definido nesta classe.
    """

    def __init__(self, model_settings: ModelSettings) -> None:
        """Inicializa o seletor com as configurações de modelos.

        Args:
            model_settings: Configurações centralizadas dos modelos.
        """
        self._settings = model_settings
        self._model_map: dict[TaskType, str] = {
            TaskType.GENERAL: model_settings.general,
            TaskType.CODING: model_settings.coding,
            TaskType.LIGHTWEIGHT: model_settings.lightweight,
        }

    def select(self, task_type: TaskType) -> str:
        """Seleciona o modelo para um tipo de tarefa.

        Args:
            task_type: Tipo de tarefa.

        Returns:
            Nome do modelo configurado para esse tipo.
        """
        return self._model_map[task_type]

    def get_all_models(self) -> dict[TaskType, str]:
        """Retorna mapa de todos os modelos configurados.

        Returns:
            Dicionário TaskType → nome do modelo.
        """
        return dict(self._model_map)

    @property
    def general(self) -> str:
        """Modelo para tarefas gerais."""
        return self._model_map[TaskType.GENERAL]

    @property
    def coding(self) -> str:
        """Modelo para tarefas de código."""
        return self._model_map[TaskType.CODING]

    @property
    def lightweight(self) -> str:
        """Modelo para tarefas simples/leves."""
        return self._model_map[TaskType.LIGHTWEIGHT]
