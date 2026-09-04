"""Testes para o cliente Ollama.

Utiliza mocks para simular respostas do servidor Ollama,
conforme especificado na TASK-010:
- sucesso
- timeout
- erro HTTP
- resposta inválida
"""

from __future__ import annotations

import json
from http.client import HTTPResponse
from typing import Any
from unittest import mock

import pytest

from assistant.models.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaResponse,
    OllamaResponseError,
    OllamaTimeoutError,
)


def _mock_response(
    status: int = 200,
    body: dict[str, Any] | str = "",
) -> mock.MagicMock:
    """Cria mock de HTTPResponse."""
    resp = mock.MagicMock(spec=HTTPResponse)
    resp.status = status
    if isinstance(body, dict):
        resp.read.return_value = json.dumps(body).encode("utf-8")
    else:
        resp.read.return_value = body.encode("utf-8")
    return resp


def _ollama_generate_response(
    content: str = "Hello!",
    model: str = "qwen3:4b",
    done: bool = True,
    total_duration: int = 5_000_000_000,
    eval_count: int = 42,
    eval_duration: int = 2_000_000_000,
    prompt_eval_count: int = 10,
) -> dict[str, Any]:
    """Cria resposta simulada do /api/generate."""
    return {
        "model": model,
        "response": content,
        "done": done,
        "total_duration": total_duration,
        "load_duration": 1_000_000_000,
        "prompt_eval_count": prompt_eval_count,
        "eval_count": eval_count,
        "eval_duration": eval_duration,
    }


class TestOllamaClientInit:
    """Testes de inicialização do cliente."""

    def test_default_host_port(self) -> None:
        """Deve parsear host e port da URL."""
        client = OllamaClient("http://localhost:11434")
        assert client._host == "localhost"
        assert client._port == 11434

    def test_custom_host_port(self) -> None:
        """Deve suportar host e port customizados."""
        client = OllamaClient("http://192.168.1.10:8080")
        assert client._host == "192.168.1.10"
        assert client._port == 8080

    def test_custom_timeout(self) -> None:
        """Deve respeitar timeout customizado."""
        client = OllamaClient("http://localhost:11434", timeout_seconds=60)
        assert client._timeout == 60


class TestOllamaGenerate:
    """Testes para o método generate."""

    def test_generate_success(self) -> None:
        """Deve retornar OllamaResponse com conteúdo correto."""
        client = OllamaClient("http://localhost:11434")
        body = _ollama_generate_response(content="Test response")

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.getresponse.return_value = _mock_response(200, body)
            mock_conn.return_value = conn

            result = client.generate("qwen3:4b", "Hello")

        assert isinstance(result, OllamaResponse)
        assert result.content == "Test response"
        assert result.model == "qwen3:4b"
        assert result.done is True

    def test_generate_with_system_prompt(self) -> None:
        """Deve incluir system prompt na requisição."""
        client = OllamaClient("http://localhost:11434")
        body = _ollama_generate_response()

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.getresponse.return_value = _mock_response(200, body)
            mock_conn.return_value = conn

            client.generate("qwen3:4b", "Hello", system="You are helpful")

            # Verificar que o body incluiu system
            call_args = conn.request.call_args
            sent_body = json.loads(call_args[1]["body"] if "body" in call_args[1] else call_args[0][2])
            assert sent_body["system"] == "You are helpful"

    def test_generate_with_temperature(self) -> None:
        """Deve incluir temperature nas options."""
        client = OllamaClient("http://localhost:11434")
        body = _ollama_generate_response()

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.getresponse.return_value = _mock_response(200, body)
            mock_conn.return_value = conn

            client.generate("qwen3:4b", "Hello", temperature=0.7)

            call_args = conn.request.call_args
            sent_body = json.loads(call_args[1]["body"] if "body" in call_args[1] else call_args[0][2])
            assert sent_body["options"]["temperature"] == 0.7

    def test_generate_tokens_per_second(self) -> None:
        """Deve calcular tokens/s corretamente."""
        client = OllamaClient("http://localhost:11434")
        body = _ollama_generate_response(
            eval_count=100,
            eval_duration=2_000_000_000,  # 2 seconds
        )

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.getresponse.return_value = _mock_response(200, body)
            mock_conn.return_value = conn

            result = client.generate("qwen3:4b", "Hello")

        assert result.tokens_per_second is not None
        assert result.tokens_per_second == pytest.approx(50.0)

    def test_generate_metrics_populated(self) -> None:
        """Deve preencher métricas quando disponíveis."""
        client = OllamaClient("http://localhost:11434")
        body = _ollama_generate_response(
            total_duration=5_000_000_000,
            eval_count=42,
            eval_duration=2_000_000_000,
            prompt_eval_count=10,
        )

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.getresponse.return_value = _mock_response(200, body)
            mock_conn.return_value = conn

            result = client.generate("qwen3:4b", "Hello")

        assert result.total_duration_ns == 5_000_000_000
        assert result.eval_count == 42
        assert result.prompt_eval_count == 10


class TestOllamaErrors:
    """Testes para cenários de erro."""

    def test_connection_error(self) -> None:
        """Deve gerar OllamaConnectionError quando servidor indisponível."""
        client = OllamaClient("http://localhost:11434")

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.request.side_effect = OSError("Connection refused")
            mock_conn.return_value = conn

            with pytest.raises(OllamaConnectionError, match="Connection refused"):
                client.generate("qwen3:4b", "Hello")

    def test_timeout_error(self) -> None:
        """Deve gerar OllamaTimeoutError quando excede timeout."""
        client = OllamaClient("http://localhost:11434", timeout_seconds=1)

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.request.side_effect = TimeoutError("timed out")
            mock_conn.return_value = conn

            with pytest.raises(OllamaTimeoutError, match="Timeout"):
                client.generate("qwen3:4b", "Hello")

    def test_http_error(self) -> None:
        """Deve gerar OllamaResponseError para HTTP != 200."""
        client = OllamaClient("http://localhost:11434")

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.getresponse.return_value = _mock_response(500, "Internal Server Error")
            mock_conn.return_value = conn

            with pytest.raises(OllamaResponseError, match="HTTP 500"):
                client.generate("qwen3:4b", "Hello")

    def test_invalid_json_response(self) -> None:
        """Deve gerar OllamaResponseError para JSON inválido."""
        client = OllamaClient("http://localhost:11434")

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            resp = mock.MagicMock(spec=HTTPResponse)
            resp.status = 200
            resp.read.return_value = b"not json"
            mock_conn.return_value = conn
            conn.getresponse.return_value = resp

            with pytest.raises(OllamaResponseError, match="Resposta inválida"):
                client.generate("qwen3:4b", "Hello")

    def test_http_error_has_status_code(self) -> None:
        """OllamaResponseError deve conter o status code."""
        client = OllamaClient("http://localhost:11434")

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.getresponse.return_value = _mock_response(404, "Not found")
            mock_conn.return_value = conn

            with pytest.raises(OllamaResponseError) as exc_info:
                client.generate("qwen3:4b", "Hello")

            assert exc_info.value.status_code == 404


class TestOllamaChat:
    """Testes para o método chat."""

    def test_chat_success(self) -> None:
        """Deve extrair conteúdo da resposta chat."""
        client = OllamaClient("http://localhost:11434")
        body = {
            "model": "qwen3:4b",
            "message": {"role": "assistant", "content": "Chat response"},
            "done": True,
            "total_duration": 3_000_000_000,
            "eval_count": 20,
            "eval_duration": 1_000_000_000,
        }

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.getresponse.return_value = _mock_response(200, body)
            mock_conn.return_value = conn

            result = client.chat("qwen3:4b", [{"role": "user", "content": "Hi"}])

        assert result.content == "Chat response"
        assert result.model == "qwen3:4b"


class TestOllamaListModels:
    """Testes para listagem de modelos."""

    def test_list_models_success(self) -> None:
        """Deve retornar lista de modelos."""
        client = OllamaClient("http://localhost:11434")
        body = {
            "models": [
                {"name": "qwen3:4b", "size": 2_500_000_000},
                {"name": "qwen2.5-coder:3b", "size": 1_900_000_000},
            ]
        }

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.getresponse.return_value = _mock_response(200, body)
            mock_conn.return_value = conn

            models = client.list_models()

        assert len(models) == 2
        assert models[0]["name"] == "qwen3:4b"


class TestOllamaHealthCheck:
    """Testes para verificação de saúde."""

    def test_health_check_ok(self) -> None:
        """Deve retornar True quando servidor responde."""
        client = OllamaClient("http://localhost:11434")

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.getresponse.return_value = _mock_response(200, "Ollama is running")
            mock_conn.return_value = conn

            assert client.health_check() is True

    def test_health_check_fail(self) -> None:
        """Deve retornar False quando servidor indisponível."""
        client = OllamaClient("http://localhost:11434")

        with mock.patch.object(client, "_connect") as mock_conn:
            conn = mock.MagicMock()
            conn.request.side_effect = OSError("Connection refused")
            mock_conn.return_value = conn

            assert client.health_check() is False


class TestOllamaResponse:
    """Testes para a estrutura de resposta."""

    def test_response_is_frozen(self) -> None:
        """OllamaResponse deve ser imutável."""
        resp = OllamaResponse(content="test", model="test", done=True)
        with pytest.raises(AttributeError):
            resp.content = "other"  # type: ignore[misc]

    def test_response_defaults(self) -> None:
        """Campos opcionais devem ser None por padrão."""
        resp = OllamaResponse(content="test", model="test", done=True)
        assert resp.total_duration_ns is None
        assert resp.eval_count is None
        assert resp.tokens_per_second is None
        assert resp.raw == {}
