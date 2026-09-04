"""Testes para a abstração de ferramentas."""

from __future__ import annotations

from typing import Any

from assistant.tools.base import BaseTool, ToolResult


class FakeTool(BaseTool):
    """Ferramenta fake para testes da abstração."""

    @property
    def name(self) -> str:
        return "fake_tool"

    @property
    def description(self) -> str:
        return "A fake tool for testing purposes."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "input_value": {"type": "string"},
            },
            "required": ["input_value"],
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execução fake."""
        input_value = kwargs.get("input_value")
        if not input_value:
            return ToolResult(
                success=False,
                output="Missing required argument 'input_value'",
                error_code="MISSING_ARG",
            )
        return ToolResult(
            success=True,
            output=f"Processed: {input_value}",
            data={"original": input_value},
        )


class TestToolAbstraction:
    """Testes para a interface e classes base de tools."""

    def test_tool_result_success(self) -> None:
        """Testa criação de ToolResult de sucesso."""
        result = ToolResult(success=True, output="OK")
        assert result.success is True
        assert result.output == "OK"
        assert result.data is None
        assert result.error_code is None

    def test_tool_result_failure(self) -> None:
        """Testa criação de ToolResult de falha."""
        result = ToolResult(success=False, output="Error", error_code="E01")
        assert result.success is False
        assert result.output == "Error"
        assert result.error_code == "E01"

    def test_fake_tool_properties(self) -> None:
        """Testa propriedades implementadas na ferramenta concreta."""
        tool = FakeTool()
        assert tool.name == "fake_tool"
        assert tool.description.startswith("A fake tool")
        assert tool.schema["type"] == "object"
        assert "input_value" in tool.schema["properties"]

    def test_fake_tool_execute_success(self) -> None:
        """Testa execução de sucesso da ferramenta concreta."""
        tool = FakeTool()
        result = tool.execute(input_value="test")
        assert result.success is True
        assert result.output == "Processed: test"
        assert result.data == {"original": "test"}

    def test_fake_tool_execute_failure(self) -> None:
        """Testa execução com falha da ferramenta concreta."""
        tool = FakeTool()
        result = tool.execute()  # Missing required arg
        assert result.success is False
        assert result.error_code == "MISSING_ARG"
        assert "Missing required argument" in result.output
