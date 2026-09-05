# Testes e Qualidade

O **Local AI Assistant** possui uma suíte de testes rigorosa para garantir estabilidade, segurança e funcionamento contínuo. 

Foram implementados dois níveis principais de testes: Testes Unitários e Testes de Integração (End-to-End). O projeto conta com 100% de cobertura nos componentes críticos.

---

## 1. Testes Unitários

Localização: `tests/unit/`

Os testes unitários validam a lógica isolada de cada módulo sem depender de serviços externos (Ollama, rede, etc.). Eles rodam extremamente rápido e cobrem as regras de negócio de cada classe.

### O que foi testado?
- **Ferramentas (Tools)**:
  - Sistema de Arquivos (Leitura/Escrita).
  - Web (Search, URL Reader, Docs Lookup).
  - Git (Status, Branch, Commit, Diff, Push).
  - GitHub (Issues, PRs).
- **Segurança**:
  - `WorkspaceBoundary`: Restrições de diretório (Path traversal).
  - `SecretProtection`: Detecção de máscaras para API keys/tokens.
  - `DestructiveOperationPolicy`: Prevenção de comandos como `rm -rf`.
  - `AuditTrail`: Verificação dos logs estruturados.
- **Memória**:
  - `SessionState`: Armazenamento de efêmeros e histórico.
  - `PersistentMemory`: Escrita e leitura de JSONL.
  - `MemoryPolicy`: Testes de limites de escopo e tamanho de memórias.
- **MCP e Skills**:
  - Comunicação de cliente/servidor (JSON-RPC) simulada.
  - Validação de schemas e políticas de acesso (Allowlist/Blocklist).

### Como rodar os Testes Unitários

```bash
# Na raiz do projeto, utilizando o ambiente virtual:
.venv\Scripts\pytest tests\unit\ -v
```

---

## 2. Testes de Integração (End-to-End)

Localização: `tests/integration/test_e2e.py`

Os testes de integração realizam validações reais, exigindo que o serviço do **Ollama** esteja rodando localmente.

### O que foi testado?
- **Ollama Connection**: Validação do Health Check e Listagem de modelos.
- **Model Generation**: Inferência simples via `/api/generate` e endpoints de Chat via `/api/chat` usando modelos configurados.
- **Harness Loop**: Integração real do `Harness` com o modelo, simulando transições de estado (`PLAN` → `ACT` → `OBSERVE` → `VERIFY` → `COMPLETE`).
- **Memória & Sessão**: Fluxo completo retendo mensagens reais entre turnos.
- **API Server**: Validação dos endpoints HTTP (`/api/health` e dashboard web).
- **Simulação Completa do Agente**: Um fluxo E2E solicitando que o agente "Resolva 2+2", passando pela chamada real do LLM e processando o resultado ("4") até a conclusão bem sucedida.

### Como rodar os Testes de Integração

> **Atenção:** O serviço do Ollama deve estar rodando na máquina padrão (`localhost:11434`).

```bash
# Executa apenas os testes E2E com logs no console
.venv\Scripts\pytest tests\integration\test_e2e.py -v -s
```

---

## 3. Ferramentas de Qualidade de Código (Lint & Type-check)

O projeto mantém um padrão de código estrito sem tolerância a falhas.

### Ruff
Utilizado para formatação e análise estática (Linting).
```bash
# Para checar:
.venv\Scripts\ruff check src\ tests\

# Para corrigir automaticamente (format):
.venv\Scripts\ruff format src\ tests\
```

### Mypy
Utilizado para garantir que os tipos estáticos do Python estejam corretos em 100% da base.
```bash
.venv\Scripts\mypy src\assistant\
```

---

## Pipeline CI

Todas essas etapas estão unificadas em um pipeline do GitHub Actions (`.github/workflows/ci.yml`), que roda sempre que código novo chega na `main` ou em `pull_requests`.

- Checkout.
- Instalação (com dependencies `[dev]`).
- Ruff Linting.
- Ruff Formatting check.
- Mypy type-checking.
- Pytest (Todos os testes suportados no runner).
