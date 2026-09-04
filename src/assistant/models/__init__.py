"""Models — adaptadores para modelos de IA (Ollama).

Fornece abstrações para comunicação com modelos de IA locais.
"""

from assistant.models.ollama_client import OllamaClient, OllamaResponse

__all__ = ["OllamaClient", "OllamaResponse"]
