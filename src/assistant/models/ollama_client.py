"""Cliente isolado para comunicação com Ollama.

Responsabilidades:
- Enviar prompt ao modelo
- Receber resposta estruturada
- Lidar com timeout
- Lidar com erros de conexão e HTTP
- Retornar resposta estruturada (OllamaResponse)

Não é responsável por:
- Controlar Harness
- Executar ferramentas
- Acessar banco
- Implementar Agent
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from http.client import HTTPConnection, HTTPException
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class OllamaResponse:
    """Resposta estruturada de uma chamada ao Ollama.

    Attributes:
        content: Texto da resposta do modelo.
        model: Nome do modelo utilizado.
        done: Se a geração foi concluída.
        total_duration_ns: Duração total em nanosegundos (se disponível).
        load_duration_ns: Duração de carregamento em nanosegundos.
        prompt_eval_count: Número de tokens do prompt avaliados.
        eval_count: Número de tokens gerados.
        eval_duration_ns: Duração da geração em nanosegundos.
        tokens_per_second: Tokens gerados por segundo (calculado).
        raw: Resposta bruta do Ollama.
    """

    content: str
    model: str
    done: bool
    total_duration_ns: int | None = None
    load_duration_ns: int | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None
    eval_duration_ns: int | None = None
    tokens_per_second: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class OllamaError(Exception):
    """Erro base para operações Ollama."""


class OllamaConnectionError(OllamaError):
    """Erro de conexão com Ollama."""


class OllamaTimeoutError(OllamaError):
    """Timeout ao comunicar com Ollama."""


class OllamaResponseError(OllamaError):
    """Resposta inválida ou erro HTTP do Ollama."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class OllamaClient:
    """Cliente para comunicação com o servidor Ollama.

    Utiliza http.client (stdlib) para manter dependências mínimas.
    Cada chamada abre e fecha a conexão — adequado para uso local
    com baixa frequência de requisições.
    """

    def __init__(self, base_url: str, timeout_seconds: int = 120) -> None:
        """Inicializa o cliente Ollama.

        Args:
            base_url: URL base do servidor Ollama (ex: http://localhost:11434).
            timeout_seconds: Timeout para requisições HTTP.
        """
        parsed = urlparse(base_url)
        self._host = parsed.hostname or "localhost"
        self._port = parsed.port or 11434
        self._timeout = timeout_seconds

    def generate(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
    ) -> OllamaResponse:
        """Envia um prompt ao modelo e retorna a resposta.

        Args:
            model: Nome do modelo (ex: "qwen3:4b").
            prompt: Texto do prompt.
            system: System prompt opcional.
            temperature: Temperatura de geração (0.0-1.0).

        Returns:
            OllamaResponse com o resultado.

        Raises:
            OllamaConnectionError: Quando não é possível conectar ao Ollama.
            OllamaTimeoutError: Quando a requisição excede o timeout.
            OllamaResponseError: Quando a resposta é inválida ou HTTP erro.
        """
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        if system is not None:
            payload["system"] = system

        if temperature is not None:
            payload["options"] = {"temperature": temperature}

        return self._post("/api/generate", payload)

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
    ) -> OllamaResponse:
        """Envia mensagens de chat ao modelo.

        Args:
            model: Nome do modelo.
            messages: Lista de mensagens [{"role": "user", "content": "..."}].
            temperature: Temperatura de geração.

        Returns:
            OllamaResponse com o resultado.
        """
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        if temperature is not None:
            payload["options"] = {"temperature": temperature}

        raw = self._post_raw("/api/chat", payload)

        # Chat endpoint retorna "message" em vez de "response"
        message = raw.get("message", {})
        content = message.get("content", "") if isinstance(message, dict) else ""

        return self._build_response(content, raw)

    def list_models(self) -> list[dict[str, Any]]:
        """Lista modelos disponíveis no Ollama.

        Returns:
            Lista de dicionários com informações dos modelos.

        Raises:
            OllamaConnectionError: Quando não é possível conectar.
        """
        raw = self._get("/api/tags")
        models: list[dict[str, Any]] = raw.get("models", [])
        return models

    def health_check(self) -> bool:
        """Verifica se o Ollama está acessível.

        Returns:
            True se o servidor está respondendo.
        """
        try:
            self._get("/")
            return True
        except OllamaError:
            return False

    def _post(self, path: str, payload: dict[str, Any]) -> OllamaResponse:
        """Faz POST e retorna OllamaResponse."""
        raw = self._post_raw(path, payload)
        content = raw.get("response", "")
        return self._build_response(content, raw)

    def _build_response(self, content: str, raw: dict[str, Any]) -> OllamaResponse:
        """Constrói OllamaResponse a partir da resposta bruta."""
        eval_count = raw.get("eval_count")
        eval_duration_ns = raw.get("eval_duration")

        tokens_per_second: float | None = None
        if eval_count and eval_duration_ns and eval_duration_ns > 0:
            tokens_per_second = eval_count / (eval_duration_ns / 1_000_000_000)

        return OllamaResponse(
            content=content,
            model=raw.get("model", ""),
            done=raw.get("done", False),
            total_duration_ns=raw.get("total_duration"),
            load_duration_ns=raw.get("load_duration"),
            prompt_eval_count=raw.get("prompt_eval_count"),
            eval_count=eval_count,
            eval_duration_ns=eval_duration_ns,
            tokens_per_second=tokens_per_second,
            raw=raw,
        )

    def _post_raw(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Faz POST HTTP e retorna o JSON parseado."""
        body = json.dumps(payload).encode("utf-8")
        conn = self._connect()

        try:
            conn.request(
                "POST",
                path,
                body=body,
                headers={"Content-Type": "application/json"},
            )
            response = conn.getresponse()
            data = response.read().decode("utf-8")

            if response.status != 200:
                raise OllamaResponseError(
                    f"Ollama retornou HTTP {response.status}: {data}",
                    status_code=response.status,
                )

            result: dict[str, Any] = json.loads(data)
            return result

        except OllamaError:
            raise
        except json.JSONDecodeError as e:
            raise OllamaResponseError(f"Resposta inválida do Ollama: {e}") from e
        except TimeoutError as e:
            raise OllamaTimeoutError(
                f"Timeout após {self._timeout}s aguardando Ollama"
            ) from e
        except (OSError, HTTPException) as e:
            raise OllamaConnectionError(
                f"Erro de conexão com Ollama ({self._host}:{self._port}): {e}"
            ) from e
        finally:
            conn.close()

    def _get(self, path: str) -> dict[str, Any]:
        """Faz GET HTTP e retorna o JSON parseado."""
        conn = self._connect()

        try:
            conn.request("GET", path)
            response = conn.getresponse()
            data = response.read().decode("utf-8")

            if response.status != 200:
                raise OllamaResponseError(
                    f"Ollama retornou HTTP {response.status}: {data}",
                    status_code=response.status,
                )

            try:
                result: dict[str, Any] = json.loads(data)
                return result
            except json.JSONDecodeError:
                # Alguns endpoints retornam texto puro (ex: /)
                return {"status": "ok", "raw_response": data}

        except OllamaError:
            raise
        except TimeoutError as e:
            raise OllamaTimeoutError(
                f"Timeout após {self._timeout}s aguardando Ollama"
            ) from e
        except (OSError, HTTPException) as e:
            raise OllamaConnectionError(
                f"Erro de conexão com Ollama ({self._host}:{self._port}): {e}"
            ) from e
        finally:
            conn.close()

    def _connect(self) -> HTTPConnection:
        """Cria conexão HTTP com o Ollama."""
        try:
            conn = HTTPConnection(self._host, self._port, timeout=self._timeout)
            return conn
        except (OSError, HTTPException) as e:
            raise OllamaConnectionError(
                f"Não foi possível conectar ao Ollama ({self._host}:{self._port}): {e}"
            ) from e
