"""Configuração centralizada da aplicação.

Todas as configurações do sistema são definidas aqui.
Nenhum componente deve definir valores de configuração diretamente no código.

Configurações podem ser sobrescritas via variáveis de ambiente.
"""

from assistant.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
