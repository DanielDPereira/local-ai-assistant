"""Testes para seleção de modelos por tipo de tarefa."""

from __future__ import annotations

from assistant.config.settings import ModelSettings
from assistant.models.model_selector import ModelSelector, TaskType


class TestModelSelector:
    """Verificar seleção de modelos por tipo de tarefa."""

    def test_select_general(self) -> None:
        """Deve retornar modelo geral para TaskType.GENERAL."""
        settings = ModelSettings()
        selector = ModelSelector(settings)
        assert selector.select(TaskType.GENERAL) == "qwen3:4b"

    def test_select_coding(self) -> None:
        """Deve retornar modelo de código para TaskType.CODING."""
        settings = ModelSettings()
        selector = ModelSelector(settings)
        assert selector.select(TaskType.CODING) == "qwen2.5-coder:3b"

    def test_select_lightweight(self) -> None:
        """Deve retornar modelo leve para TaskType.LIGHTWEIGHT."""
        settings = ModelSettings()
        selector = ModelSelector(settings)
        assert selector.select(TaskType.LIGHTWEIGHT) == "qwen3:1.7b"

    def test_custom_models(self) -> None:
        """Deve respeitar modelos customizados da configuração."""
        settings = ModelSettings(
            general="llama3:8b",
            coding="codellama:7b",
            lightweight="phi3:mini",
        )
        selector = ModelSelector(settings)
        assert selector.select(TaskType.GENERAL) == "llama3:8b"
        assert selector.select(TaskType.CODING) == "codellama:7b"
        assert selector.select(TaskType.LIGHTWEIGHT) == "phi3:mini"

    def test_properties(self) -> None:
        """Propriedades devem retornar modelos corretos."""
        settings = ModelSettings()
        selector = ModelSelector(settings)
        assert selector.general == "qwen3:4b"
        assert selector.coding == "qwen2.5-coder:3b"
        assert selector.lightweight == "qwen3:1.7b"

    def test_get_all_models(self) -> None:
        """get_all_models deve retornar mapa completo."""
        settings = ModelSettings()
        selector = ModelSelector(settings)
        all_models = selector.get_all_models()
        assert len(all_models) == 3
        assert all_models[TaskType.GENERAL] == "qwen3:4b"
        assert all_models[TaskType.CODING] == "qwen2.5-coder:3b"
        assert all_models[TaskType.LIGHTWEIGHT] == "qwen3:1.7b"

    def test_changing_config_changes_selection(self) -> None:
        """Alterar modelo exige apenas alterar configuração."""
        settings_v1 = ModelSettings(general="qwen3:4b")
        settings_v2 = ModelSettings(general="llama3:70b")

        selector_v1 = ModelSelector(settings_v1)
        selector_v2 = ModelSelector(settings_v2)

        assert selector_v1.general == "qwen3:4b"
        assert selector_v2.general == "llama3:70b"


class TestTaskType:
    """Verificar enumeração TaskType."""

    def test_task_type_values(self) -> None:
        """TaskType deve ter valores corretos."""
        assert TaskType.GENERAL.value == "general"
        assert TaskType.CODING.value == "coding"
        assert TaskType.LIGHTWEIGHT.value == "lightweight"

    def test_all_task_types(self) -> None:
        """Deve ter exatamente 3 tipos."""
        assert len(TaskType) == 3
