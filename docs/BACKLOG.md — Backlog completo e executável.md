# Backlog de Desenvolvimento

## Assistente de IA Local

**Versão:** 2.0.0

---

# 1. Como utilizar este backlog

Este documento define as tarefas que deverão ser executadas durante o desenvolvimento.

Cada tarefa possui:

- identificador;
- título;
- prioridade;
- dependências;
- objetivo;
- implementação esperada;
- arquivos/componentes envolvidos;
- critérios de aceitação;
- testes obrigatórios;
- resultado esperado.

O agente de desenvolvimento deverá executar as tarefas na ordem recomendada, respeitando dependências.

Não deverá implementar várias tarefas grandes em uma única alteração.

Cada tarefa deverá resultar em uma alteração lógica pequena e revisável.

---

# 2. Prioridades

## P0 — Obrigatória

Sem essa funcionalidade, o MVP não está completo.

## P1 — Alta

Necessária para a versão funcional completa.

## P2 — Média

Importante para evolução do sistema.

## P3 — Baixa

Melhoria posterior.

---

# 3. Estados

Cada tarefa poderá estar em:

```text
[ ] Pendente
[~] Em desenvolvimento
[x] Concluída
[!] Bloqueada
```

O agente deverá atualizar o estado após concluir cada tarefa.

---

# EPIC 0 — Fundação do projeto

---

## [x] TASK-001 — Criar estrutura inicial do projeto

**Prioridade:** P0  
**Dependências:** Nenhuma

### Objetivo

Criar a estrutura inicial do projeto Python.

### Deve criar

```text
src/
tests/
docs/
scripts/
.github/
```

Além de:

```text
pyproject.toml
README.md
.gitignore
.env.example
```

### Critérios de aceitação

- projeto inicia sem erros;
- pacote Python pode ser importado;
- ambiente virtual pode ser criado;
- pytest pode ser executado;
- estrutura de testes funciona;
- Git reconhece o projeto.

### Testes

Executar:

```bash
pytest
```

Resultado esperado:

```text
sem erros de importação
```

### Commit

```text
feat: initialize assistant project
```

---

## [x] TASK-002 — Configuração central

**Prioridade:** P0  
**Dependências:** TASK-001

### Objetivo

Criar sistema centralizado de configuração.

### Configurações obrigatórias

- Ollama URL;
- modelo geral;
- modelo de código;
- modelo leve;
- workspace;
- timeout;
- Harness;
- banco;
- telemetry;
- hardware sampling;
- retenção;
- custo energético.

### Critérios

Nenhum componente deverá precisar definir configurações diretamente no código.

### Testes

Testar:

- valores padrão;
- valores configurados;
- configuração inválida;
- variáveis de ambiente.

### Commit

```text
feat: add application configuration
```

---

# EPIC 1 — Ollama

---

## [x] TASK-010 — Implementar adapter Ollama

**Prioridade:** P0  
**Dependências:** TASK-002

### Objetivo

Criar cliente isolado para comunicação com Ollama.

### Responsabilidades

- enviar prompt;
- receber resposta;
- lidar com timeout;
- lidar com erros;
- retornar resposta estruturada.

### Não deve

- controlar Harness;
- executar ferramentas;
- acessar banco;
- implementar Agent.

### Critérios

O Agent deverá conseguir utilizar Ollama através de uma abstração.

### Testes

Criar mocks para:

- sucesso;
- timeout;
- erro HTTP;
- resposta inválida.

### Commit

```text
feat: add Ollama model adapter
```

---

## [x] TASK-011 — Configurar modelos

**Prioridade:** P0  
**Dependências:** TASK-010

### Objetivo

Configurar modelos por tipo de tarefa.

### Configuração

```text
general
coding
lightweight
```

### Critérios

Alterar o modelo deve exigir apenas alteração de configuração.

### Testes

Validar seleção dos modelos.

### Commit

```text
feat: add configurable model selection
```

---

# EPIC 2 — Agent

---

## [x] TASK-020 — Implementar Agent mínimo

**Prioridade:** P0  
**Dependências:** TASK-011

### Objetivo

Criar Agent capaz de receber uma solicitação e consultar o modelo.

### Fluxo

```text
input
→ Agent
→ Model
→ response
```

### Critérios

- recebe entrada;
- envia ao modelo;
- retorna resposta;
- trata erros.

### Testes

Testar:

- entrada válida;
- resposta;
- timeout;
- erro do modelo.

### Commit

```text
feat: implement basic agent
```

---

## [x] TASK-021 — Criar abstração de ferramentas

**Prioridade:** P0  
**Dependências:** TASK-020

### Objetivo

Criar interface comum para Tools.

### Cada ferramenta deverá possuir

- nome;
- descrição;
- schema;
- execução;
- resultado;
- erro.

### Critérios

Agent não poderá depender da implementação concreta de uma ferramenta.

### Testes

Criar ferramenta fake para teste.

### Commit

```text
feat: add tool abstraction
```

---

# EPIC 3 — Filesystem

---

## [x] TASK-030 — Implementar leitura de arquivos

**Prioridade:** P0  
**Dependências:** TASK-021

### Objetivo

Permitir que o agente leia arquivos do workspace.

### Requisitos

- aceitar caminho;
- validar workspace;
- impedir path traversal;
- retornar conteúdo;
- retornar erro estruturado.

### Testes

Testar:

- arquivo existente;
- arquivo inexistente;
- diretório;
- path traversal;
- arquivo sem permissão.

### Commit

```text
feat: add filesystem read tool
```

---

## [x] TASK-031 — Implementar escrita de arquivos

**Prioridade:** P0  
**Dependências:** TASK-030

### Objetivo

Permitir criação e edição de arquivos.

### Requisitos

- validar workspace;
- criar arquivo;
- substituir conteúdo;
- preservar erros;
- impedir acesso externo.

### Testes

Testar criação, edição e proteção de caminho.

### Commit

```text
feat: add filesystem write tool
```

---

## [x] TASK-032 — Implementar listagem

**Prioridade:** P0  
**Dependências:** TASK-030

### Objetivo

Permitir listar diretórios.

### Critérios

- respeitar workspace;
- não seguir caminhos proibidos;
- retornar estrutura previsível.

### Commit

```text
feat: add filesystem listing tool
```

---

# EPIC 4 — Terminal

---

## [x] TASK-040 — Implementar execução de comandos

**Prioridade:** P0  
**Dependências:** TASK-021

### Objetivo

Executar comandos dentro do workspace.

### Resultado

Deverá retornar:

- comando;
- exit code;
- stdout;
- stderr;
- duração;
- status.

### Critérios

Comando deverá possuir timeout.

### Testes

Testar:

- comando bem-sucedido;
- comando falho;
- timeout;
- saída;
- diretório de trabalho.

### Commit

```text
feat: add terminal execution tool
```

---

## [x] TASK-041 — Implementar política de comandos

**Prioridade:** P0  
**Dependências:** TASK-040

### Objetivo

Impedir comandos perigosos.

### Deve considerar

- exclusão;
- formatação;
- alterações fora do workspace;
- comandos administrativos;
- operações potencialmente destrutivas.

### Critérios

Comandos bloqueados não deverão ser executados.

### Testes

Criar testes para comandos permitidos e proibidos.

### Commit

```text
feat: add terminal command policy
```

---

# EPIC 5 — Harness

---

## [x] TASK-050 — Implementar ciclo básico

**Prioridade:** P0  
**Dependências:** TASK-020, TASK-021, TASK-030, TASK-040

### Objetivo

Criar o primeiro Harness funcional.

### Fluxo

```text
PLAN
ACT
OBSERVE
VERIFY
COMPLETE
```

### Critérios

O Harness deverá controlar a execução e não permitir que o Agent execute indefinidamente.

### Commit

```text
feat: implement basic harness
```

---

## [x] TASK-051 — Limite de iterações

**Prioridade:** P0  
**Dependências:** TASK-050

### Objetivo

Impedir loops infinitos.

### Configuração

```text
max_iterations
```

### Critérios

Ao atingir o limite, a execução deverá terminar com status apropriado.

### Testes

Simular agente que nunca conclui.

### Commit

```text
feat: add harness iteration limit
```

---

## [x] TASK-052 — Timeout global

**Prioridade:** P0  
**Dependências:** TASK-050

### Objetivo

Impedir execução infinita por tempo.

### Critérios

Timeout deverá encerrar execução de maneira segura.

### Commit

```text
feat: add harness execution timeout
```

---

## [x] TASK-053 — Detecção de loop

**Prioridade:** P1  
**Dependências:** TASK-051

### Objetivo

Detectar quando o agente repete as mesmas ações sem progresso.

### Critérios

O Harness deverá identificar padrões repetitivos.

### Commit

```text
feat: add harness loop detection
```

---

# EPIC 6 — Validação

---

## [x] TASK-060 — Executor de validações

**Prioridade:** P0  
**Dependências:** TASK-040, TASK-050

### Objetivo

Criar componente responsável por executar verificações.

### Deve suportar

- Ruff;
- Mypy;
- Pytest;
- build.

### Critérios

Resultado deverá ser estruturado.

### Commit

```text
feat: add validation runner
```

---

## [x] TASK-061 — Integração do Harness com validação

**Prioridade:** P0  
**Dependências:** TASK-060

### Objetivo

Harness deverá utilizar validações para decidir se uma tarefa foi concluída.

### Critérios

Falha em validação deverá impedir conclusão.

### Commit

```text
feat: integrate validation with harness
```

---

# EPIC 7 — Observabilidade

Esta Epic é obrigatória antes do desenvolvimento do dashboard.

---

## [x] TASK-070 — Criar modelo de evento

**Prioridade:** P0  
**Dependências:** TASK-050

### Objetivo

Criar estrutura padronizada de eventos.

### Campos

```text
event_id
execution_id
timestamp
event_type
status
metadata
```

### Critérios

Todos os eventos devem possuir estrutura consistente.

### Commit

```text
feat: add telemetry event model
```

---

## [x] TASK-071 — Criar Execution Context

**Prioridade:** P0  
**Dependências:** TASK-070

### Objetivo

Criar contexto que acompanhe uma execução inteira.

### Deve possuir

```text
execution_id
started_at
status
task_type
model
```

### Critérios

Agent, Harness e Tools devem conseguir associar eventos à mesma execução.

### Commit

```text
feat: add execution context
```

---

## [x] TASK-072 — Registrar início e término

**Prioridade:** P0  
**Dependências:** TASK-071

### Eventos

```text
execution_started
execution_completed
execution_failed
execution_cancelled
```

### Critérios

Toda execução deverá possuir evento inicial e evento final.

### Commit

```text
feat: track execution lifecycle
```

---

## [x] TASK-073 — Telemetria de modelos

**Prioridade:** P0  
**Dependências:** TASK-072, TASK-010

### Registrar

- modelo;
- início;
- fim;
- duração;
- tokens;
- tokens/s;
- status.

### Critérios

Não inventar valores ausentes.

### Commit

```text
feat: add model execution telemetry
```

---

## [x] TASK-074 — Telemetria de ferramentas

**Prioridade:** P0  
**Dependências:** TASK-072, TASK-021

### Registrar

- ferramenta;
- operação;
- início;
- fim;
- duração;
- status;
- erro.

### Commit

```text
feat: add tool execution telemetry
```

---

## [x] TASK-075 — Telemetria do Harness

**Prioridade:** P0  
**Dependências:** TASK-071, TASK-050

### Registrar

- iteração;
- início;
- fim;
- resultado;
- erro;
- retry.

### Commit

```text
feat: add harness telemetry
```

---

## [x] TASK-076 — Telemetria de validações

**Prioridade:** P1  
**Dependências:** TASK-060

### Registrar

- validação;
- duração;
- resultado;
- saída resumida;
- erro.

### Commit

```text
feat: add validation telemetry
```

---

# EPIC 8 — Banco de dados

---

## [x] TASK-080 — Configurar SQLite

**Prioridade:** P0  
**Dependências:** TASK-070

### Objetivo

Criar banco local.

### Critérios

- banco criado automaticamente;
- caminho configurável;
- aplicação consegue conectar;
- conexão pode ser testada.

### Commit

```text
feat: add SQLite database
```

---

## [x] TASK-081 — Criar migrations

**Prioridade:** P1  
**Dependências:** TASK-080

### Objetivo

Permitir evolução segura do schema.

### Commit

```text
feat: add database migrations
```

---

## [x] TASK-082 — Criar tabela executions

**Prioridade:** P0  
**Dependências:** TASK-080

### Campos

```text
id
started_at
finished_at
duration_ms
task_type
status
model
workspace
iterations
tool_calls
retries
success
human_intervention
error_count
prompt_tokens
completion_tokens
total_tokens
```

### Commit

```text
feat: persist execution records
```

---

## [x] TASK-083 — Criar tabela model_runs

**Prioridade:** P0  
**Dependências:** TASK-082

### Campos

```text
id
execution_id
model
started_at
finished_at
duration_ms
prompt_tokens
completion_tokens
total_tokens
tokens_per_second
status
error
```

### Commit

```text
feat: persist model runs
```

---

## [x] TASK-084 — Criar tabela tool_runs

**Prioridade:** P0  
**Dependências:** TASK-082

### Campos

```text
id
execution_id
tool_name
operation
started_at
finished_at
duration_ms
status
error
```

### Commit

```text
feat: persist tool runs
```

---

## [x] TASK-085 — Criar tabela harness_iterations

**Prioridade:** P0  
**Dependências:** TASK-082

### Campos

```text
id
execution_id
iteration_number
started_at
finished_at
duration_ms
status
retry
error
```

### Commit

```text
feat: persist harness iterations
```

---

## [x] TASK-086 — Criar tabela validation_runs

**Prioridade:** P1  
**Dependências:** TASK-060

### Campos

```text
id
execution_id
validation_type
started_at
finished_at
duration_ms
status
exit_code
error
```

### Commit

```text
feat: persist validation runs
```

---

# EPIC 9 — Hardware

---

## [x] TASK-090 — Implementar hardware sampler

**Prioridade:** P1  
**Dependências:** TASK-071

### Objetivo

Coletar:

- CPU;
- RAM;
- GPU quando disponível.

### Critérios

Sampling configurável.

### Commit

```text
feat: add hardware monitoring
```

---

## TASK-091 — Criar tabela hardware_samples

**Prioridade:** P1  
**Dependências:** TASK-090, TASK-080

### Campos

```text
id
execution_id
timestamp
cpu_percent
ram_percent
ram_used_mb
gpu_percent
gpu_memory_used_mb
gpu_memory_percent
gpu_temperature
power_watts
```

### Critérios

Campos indisponíveis deverão aceitar NULL.

### Commit

```text
feat: persist hardware samples
```

---

## TASK-092 — Agregar hardware por execução

**Prioridade:** P1  
**Dependências:** TASK-091

### Calcular

- CPU média;
- CPU máxima;
- RAM média;
- RAM máxima;
- GPU média;
- GPU máxima.

### Commit

```text
feat: aggregate execution hardware metrics
```

---

# EPIC 10 — Custos

---

## TASK-100 — Configurar preço de energia

**Prioridade:** P1  
**Dependências:** TASK-002

### Configuração

```text
electricity_price_per_kwh
```

### Commit

```text
feat: add electricity cost configuration
```

---

## TASK-101 — Implementar estimativa de energia

**Prioridade:** P1  
**Dependências:** TASK-092, TASK-100

### Fórmula

```text
energia = potência × tempo
```

Converter corretamente para kWh.

### Critérios

Resultado deverá ser marcado como estimativa.

### Commit

```text
feat: estimate computational energy usage
```

---

## TASK-102 — Implementar custo por execução

**Prioridade:** P1  
**Dependências:** TASK-101

### Resultado

Cada execução poderá possuir:

```text
estimated_energy_kwh
estimated_cost
```

### Commit

```text
feat: calculate execution computational cost
```

---

## TASK-103 — Agregar custos

**Prioridade:** P1  
**Dependências:** TASK-102

### Agregações

- dia;
- mês;
- modelo;
- tarefa;
- execução.

### Commit

```text
feat: aggregate computational costs
```

---

# EPIC 11 — API

---

## TASK-110 — Criar FastAPI

**Prioridade:** P1  
**Dependências:** TASK-082

### Objetivo

Criar backend HTTP.

### Endpoint

```text
GET /api/health
```

### Critérios

Deve retornar status da aplicação.

### Commit

```text
feat: add FastAPI backend
```

---

## TASK-111 — Overview API

**Prioridade:** P1  
**Dependências:** TASK-110, TASK-103

### Endpoint

```text
GET /api/metrics/overview
```

### Deve retornar

- total de execuções;
- sucesso;
- falhas;
- taxa de sucesso;
- duração média;
- tokens;
- ferramentas;
- erros;
- custo.

### Commit

```text
feat: add metrics overview endpoint
```

---

## TASK-112 — Executions API

**Prioridade:** P1  
**Dependências:** TASK-110

### Endpoints

```text
GET /api/metrics/executions
GET /api/metrics/executions/{execution_id}
```

### Deve possuir

- paginação;
- filtros;
- ordenação.

### Commit

```text
feat: add executions metrics API
```

---

## TASK-113 — Models API

**Prioridade:** P1  
**Dependências:** TASK-083

### Endpoint

```text
GET /api/metrics/models
```

### Deve calcular

- quantidade;
- sucesso;
- falha;
- latência;
- tokens/s;
- tokens;
- custo.

### Commit

```text
feat: add model metrics endpoint
```

---

## TASK-114 — Hardware API

**Prioridade:** P1  
**Dependências:** TASK-092

### Endpoint

```text
GET /api/metrics/hardware
```

### Commit

```text
feat: add hardware metrics endpoint
```

---

## TASK-115 — Costs API

**Prioridade:** P1  
**Dependências:** TASK-103

### Endpoint

```text
GET /api/metrics/costs
```

### Commit

```text
feat: add computational cost endpoint
```

---

## TASK-116 — Errors API

**Prioridade:** P1  
**Dependências:** TASK-084

### Endpoint

```text
GET /api/metrics/errors
```

### Commit

```text
feat: add error metrics endpoint
```

---

## TASK-117 — Harness API

**Prioridade:** P2  
**Dependências:** TASK-085

### Endpoint

```text
GET /api/metrics/harness
```

### Commit

```text
feat: add harness metrics endpoint
```

---

# EPIC 12 — Dashboard

---

## TASK-120 — Criar dashboard base

**Prioridade:** P1  
**Dependências:** TASK-110

### Objetivo

Criar interface web local.

### Requisitos

- layout;
- navegação;
- integração com API;
- tratamento de erros;
- estado de carregamento.

### Commit

```text
feat: add dashboard foundation
```

---

## TASK-121 — Dashboard Overview

**Prioridade:** P1  
**Dependências:** TASK-111, TASK-120

### Exibir

- total de execuções;
- sucesso;
- falha;
- duração;
- tokens;
- custo.

### Commit

```text
feat: add dashboard overview
```

---

## TASK-122 — Gráficos temporais

**Prioridade:** P1  
**Dependências:** TASK-121

### Gráficos

- execuções por dia;
- duração;
- taxa de sucesso;
- custo;
- consumo de hardware.

### Commit

```text
feat: add dashboard time series
```

---

## TASK-123 — Dashboard de modelos

**Prioridade:** P1  
**Dependências:** TASK-113

### Exibir comparação de modelos.

### Commit

```text
feat: add model performance dashboard
```

---

## TASK-124 — Dashboard de hardware

**Prioridade:** P1  
**Dependências:** TASK-114

### Exibir

- CPU;
- RAM;
- GPU;
- picos;
- médias.

### Commit

```text
feat: add hardware dashboard
```

---

## TASK-125 — Dashboard de custos

**Prioridade:** P1  
**Dependências:** TASK-115

### Exibir

- custo total;
- custo diário;
- custo mensal;
- custo por modelo;
- custo por tarefa.

### Commit

```text
feat: add cost dashboard
```

---

## TASK-126 — Lista de execuções

**Prioridade:** P1  
**Dependências:** TASK-112

### Deve possuir

- paginação;
- filtros;
- ordenação;
- status;
- modelo;
- tarefa;
- data.

### Commit

```text
feat: add executions dashboard
```

---

## TASK-127 — Detalhes da execução

**Prioridade:** P1  
**Dependências:** TASK-126

### Mostrar

- resumo;
- timeline;
- modelo;
- tools;
- Harness;
- validações;
- hardware;
- erros;
- custo.

### Commit

```text
feat: add execution detail dashboard
```

---

## TASK-128 — Dashboard do Harness

**Prioridade:** P2  
**Dependências:** TASK-117

### Mostrar

- iterações;
- retries;
- loops;
- timeouts;
- primeira tentativa;
- intervenção.

### Commit

```text
feat: add harness dashboard
```

---

## TASK-129 — Dashboard de erros

**Prioridade:** P2  
**Dependências:** TASK-116

### Mostrar erros agrupados.

### Commit

```text
feat: add error dashboard
```

---

# EPIC 13 — Git

---

## TASK-130 — Git status

**Prioridade:** P1

### Commit

```text
feat: add git status tool
```

---

## TASK-131 — Git diff

**Prioridade:** P1

### Commit

```text
feat: add git diff tool
```

---

## TASK-132 — Branch management

**Prioridade:** P1

### Commit

```text
feat: add git branch management
```

---

## TASK-133 — Semantic commit

**Prioridade:** P1

### Critérios

O Agent deverá conseguir criar commits seguindo Conventional Commits.

### Commit

```text
feat: add semantic git commits
```

---

## TASK-134 — Push controlado

**Prioridade:** P1

### Critérios

Push deverá respeitar policy.

### Commit

```text
feat: add controlled git push
```

---

# EPIC 14 — GitHub

---

## TASK-140 — GitHub client

**Prioridade:** P2

Implementar cliente.

### Commit

```text
feat: add GitHub client
```

---

## TASK-141 — Issues

**Prioridade:** P2

Permitir consulta e gerenciamento controlado de issues.

### Commit

```text
feat: add GitHub issues integration
```

---

## TASK-142 — Pull Requests

**Prioridade:** P2

Permitir consulta e criação controlada de PRs.

### Commit

```text
feat: add GitHub pull request integration
```

---

# EPIC 15 — Web

---

## TASK-150 — Web search

**Prioridade:** P2

Implementar pesquisa web controlada.

### Commit

```text
feat: add web search tool
```

---

## TASK-151 — URL reader

**Prioridade:** P2

Permitir abertura e leitura de URLs.

### Commit

```text
feat: add URL reader
```

---

## TASK-152 — Documentation mode

**Prioridade:** P2

Permitir consulta especializada de documentação.

### Commit

```text
feat: add documentation lookup
```

---

# EPIC 16 — Skills

---

## TASK-160 — Skill loader

**Prioridade:** P2

Criar carregador de Skills.

### Commit

```text
feat: add skill loader
```

---

## TASK-161 — Skill validation

**Prioridade:** P2

Validar estrutura e metadata.

### Commit

```text
feat: add skill validation
```

---

## TASK-162 — Skill telemetry

**Prioridade:** P2

Registrar:

- Skill utilizada;
- execução;
- duração;
- resultado.

### Commit

```text
feat: add skill telemetry
```

---

# EPIC 17 — MCP

---

## TASK-170 — MCP client

**Prioridade:** P2

Implementar cliente MCP.

### Commit

```text
feat: add MCP client
```

---

## TASK-171 — MCP tool discovery

**Prioridade:** P2

Descobrir ferramentas.

### Commit

```text
feat: add MCP tool discovery
```

---

## TASK-172 — MCP policy

**Prioridade:** P2

Controlar permissões.

### Commit

```text
feat: add MCP security policy
```

---

## TASK-173 — MCP telemetry

**Prioridade:** P2

Registrar operações MCP.

### Commit

```text
feat: add MCP telemetry
```

---

# EPIC 18 — Memória

---

## TASK-180 — Session state

**Prioridade:** P2

Implementar estado temporário.

### Commit

```text
feat: add session state
```

---

## TASK-181 — Persistent memory

**Prioridade:** P3

Implementar memória persistente.

### Requisitos

- origem;
- timestamp;
- escopo;
- remoção.

### Commit

```text
feat: add persistent memory
```

---

## TASK-182 — Memory policies

**Prioridade:** P3

Controlar o que pode ser persistido.

### Commit

```text
feat: add memory policies
```

---

# EPIC 19 — Segurança

---

## TASK-190 — Workspace boundary

**Prioridade:** P0

Garantir que ferramentas não acessem caminhos externos.

### Commit

```text
feat: enforce workspace boundaries
```

---

## TASK-191 — Secret protection

**Prioridade:** P0

Impedir secrets no código e logs.

### Commit

```text
feat: add secret protection
```

---

## TASK-192 — Destructive operation policy

**Prioridade:** P0

Controlar operações destrutivas.

### Commit

```text
feat: add destructive operation policy
```

---

## TASK-193 — Audit trail

**Prioridade:** P1

Registrar operações críticas.

### Commit

```text
feat: add security audit trail
```

---

# EPIC 20 — Qualidade

---

## TASK-200 — Ruff

**Prioridade:** P0

Configurar lint e formatação.

### Critérios

Código deve passar sem erros.

### Commit

```text
chore: configure Ruff
```

---

## TASK-201 — Mypy

**Prioridade:** P0

Configurar type checking.

### Commit

```text
chore: configure mypy
```

---

## TASK-202 — Pytest

**Prioridade:** P0

Configurar suíte de testes.

### Commit

```text
chore: configure pytest
```

---

## TASK-203 — CI

**Prioridade:** P1

Criar GitHub Actions.

Pipeline mínimo:

```text
install
↓
lint
↓
type-check
↓
tests
```

### Commit

```text
ci: add quality pipeline
```

---

# 4. Fases de entrega

## FASE 1 — MVP

Concluir:

```text
TASK-001
TASK-002
TASK-010
TASK-011
TASK-020
TASK-021
TASK-030
TASK-031
TASK-032
TASK-040
TASK-041
TASK-050
TASK-051
TASK-052
TASK-060
TASK-061
```

Resultado:

> Agente local capaz de trabalhar com arquivos e terminal, sob controle do Harness, com validação.

---

# FASE 2 — Observabilidade

Concluir:

```text
TASK-070
TASK-071
TASK-072
TASK-073
TASK-074
TASK-075
TASK-076
TASK-080
TASK-082
TASK-083
TASK-084
TASK-085
```

Resultado:

> Todas as execuções importantes passam a ser registradas.

---

# FASE 3 — Hardware e custos

Concluir:

```text
TASK-090
TASK-091
TASK-092
TASK-100
TASK-101
TASK-102
TASK-103
```

Resultado:

> O sistema consegue medir desempenho, consumo e estimar custo.

---

# FASE 4 — Dashboard

Concluir:

```text
TASK-110
TASK-111
TASK-112
TASK-113
TASK-114
TASK-115
TASK-116
TASK-120
TASK-121
TASK-122
TASK-123
TASK-124
TASK-125
TASK-126
TASK-127
```

Resultado:

> Dashboard operacional completo.

---

# FASE 5 — Desenvolvimento de software

Concluir:

```text
TASK-130
TASK-131
TASK-132
TASK-133
TASK-134
TASK-140
TASK-141
TASK-142
```

Resultado:

> Agente capaz de trabalhar com Git e GitHub.

---

# FASE 6 — Expansão

Concluir:

```text
TASK-150
TASK-151
TASK-152
TASK-160
TASK-161
TASK-162
TASK-170
TASK-171
TASK-172
TASK-173
TASK-180
TASK-181
TASK-182
```

Resultado:

> Agente com Web, Skills, MCP e memória.

---

# 5. Ordem de prioridade

A ordem geral deverá ser:

```text
Fundação
↓
Ollama
↓
Agent
↓
Filesystem
↓
Terminal
↓
Harness
↓
Validation
↓
Observability
↓
Database
↓
Hardware
↓
Costs
↓
API
↓
Dashboard
↓
Git
↓
GitHub
↓
Web
↓
Skills
↓
MCP
↓
Memory
```

---

# 6. Regra de desenvolvimento

Nunca iniciar uma tarefa que possua dependência pendente.

Antes de implementar:

1. ler a tarefa;
2. verificar dependências;
3. inspecionar código existente;
4. identificar arquivos afetados;
5. planejar;
6. implementar;
7. testar;
8. validar;
9. revisar diff;
10. atualizar backlog;
11. realizar commit.

---

# 7. Regra de commits

Uma tarefa lógica deverá preferencialmente possuir seu próprio commit.

Caso uma tarefa precise de vários commits, cada commit deverá possuir finalidade clara.

Não misturar:

```text
feature
+
refactor
+
documentation
+
unrelated bug fix
```

no mesmo commit.

---

# 8. Critério global de conclusão

O projeto estará pronto quando:

```text
Usuário
   ↓
Agent
   ↓
Harness
   ↓
Tools
   ↓
Validation
   ↓
Observability
   ↓
SQLite
   ↓
FastAPI
   ↓
Dashboard
```

estiver funcionando de maneira integrada.

O dashboard deverá fornecer uma visão clara do comportamento do agente e de sua eficiência computacional.

---

# 9. Métricas mínimas do produto final

O sistema deverá conseguir responder:

```text
Quantas execuções ocorreram?

Qual a taxa de sucesso?

Qual o tempo médio?

Qual o tempo mediano?

Qual o P95?

Quantos tokens foram usados?

Qual modelo foi mais utilizado?

Qual modelo foi mais rápido?

Qual modelo foi mais eficiente?

Quantas ferramentas foram utilizadas?

Qual ferramenta apresentou mais erros?

Quantas iterações do Harness ocorreram?

Quantos retries ocorreram?

Quantas execuções terminaram na primeira tentativa?

Qual foi o maior consumo de RAM?

Qual foi o maior consumo de CPU?

Qual foi o maior consumo de GPU disponível?

Qual o custo computacional estimado?

Qual o custo por modelo?

Qual o custo por tarefa?

Quais erros são mais frequentes?

O desempenho está melhorando ao longo do tempo?
```

Essas perguntas representam parte fundamental do propósito do dashboard.