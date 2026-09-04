# Assistente de IA Local

Assistente pessoal de Inteligência Artificial executado localmente utilizando [Ollama](https://ollama.com/).

## Visão Geral

Sistema de IA local capaz de:

- Compreender e planejar tarefas
- Executar ferramentas (filesystem, terminal, Git, GitHub, web)
- Validar resultados com evidências objetivas
- Registrar execuções com telemetria completa
- Medir desempenho, consumo de hardware e custo computacional
- Apresentar métricas em dashboard web

## Pré-requisitos

- Python >= 3.12
- [Ollama](https://ollama.com/) instalado e executando
- Git

### Modelos recomendados

```bash
ollama pull qwen3:4b
ollama pull qwen2.5-coder:3b
```

## Setup

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.venv\Scripts\activate

# Ativar (Linux/macOS)
source .venv/bin/activate

# Instalar em modo desenvolvimento
pip install -e ".[dev]"

# Configurar variáveis de ambiente
copy .env.example .env
```

## Desenvolvimento

```bash
# Executar testes
pytest

# Lint e formatação
ruff check src/ tests/
ruff format src/ tests/

# Type checking
mypy src/
```

## Estrutura do Projeto

```
src/assistant/     — Código-fonte principal
tests/             — Testes (unit, integration, e2e)
docs/              — Documentação do projeto
scripts/           — Scripts utilitários
dashboard/         — Dashboard web (futuro)
```

## Documentação

- [Especificação Técnica](docs/PROJECT.md)
- [Backlog](docs/BACKLOG.md)

## Licença

MIT