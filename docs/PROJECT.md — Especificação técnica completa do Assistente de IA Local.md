# Assistente de IA Local

## Especificação Técnica, Arquitetural e Funcional

**Versão:** 2.0.0  
**Status:** Documento-base para desenvolvimento  
**Idioma do projeto:** Português  
**Plataforma principal:** Windows + WSL2  
**Runtime de modelos:** Ollama  
**Linguagem principal:** Python  
**Backend/API:** FastAPI  
**Banco inicial:** SQLite  
**Frontend:** Web local  
**Controle de versão:** Git + GitHub  
**Arquitetura:** modular, orientada a componentes, com separação de responsabilidades  
**Execução de modelos:** 100% local

---

# 1. Objetivo do documento

Este documento define os requisitos, arquitetura, princípios, componentes, responsabilidades, regras de desenvolvimento, segurança, observabilidade, testes e critérios de conclusão do projeto.

Ele deve ser tratado como a principal referência técnica durante o desenvolvimento.

Qualquer alteração importante na arquitetura deverá ser justificada e documentada.

O agente de desenvolvimento não deve:

- ignorar requisitos deste documento;
- implementar funcionalidades não previstas sem justificativa;
- remover requisitos para simplificar a implementação;
- criar dependências desnecessárias;
- substituir componentes fundamentais sem justificativa;
- considerar uma funcionalidade concluída sem testes e validação;
- inventar métricas;
- declarar sucesso baseado apenas na resposta do modelo;
- armazenar informações sensíveis sem autorização explícita.

---

# 2. Visão geral

O projeto consiste em um assistente pessoal de Inteligência Artificial executado localmente.

O assistente deverá utilizar modelos locais através do Ollama e deverá evoluir progressivamente de um assistente conversacional para um agente capaz de executar tarefas.

O sistema deverá ser capaz de:

1. receber uma solicitação;
2. compreender a solicitação;
3. planejar a execução;
4. selecionar ferramentas;
5. executar ações;
6. observar resultados;
7. validar resultados;
8. corrigir erros;
9. repetir etapas quando necessário;
10. finalizar somente quando houver evidências de sucesso;
11. registrar a execução;
12. medir desempenho;
13. medir consumo de hardware;
14. estimar custo computacional;
15. disponibilizar métricas através de uma API;
16. apresentar essas métricas em um dashboard web.

O objetivo final não é criar apenas um chatbot.

O objetivo é criar um:

> **Agente pessoal de IA local, autônomo dentro de limites definidos, observável, auditável, testável, seguro e eficiente em hardware limitado.**

---

# 3. Requisitos fundamentais

Os requisitos abaixo são obrigatórios.

## 3.1 Execução local

A inferência principal deverá ocorrer localmente.

O projeto deverá utilizar Ollama para execução dos modelos.

Não deverá existir dependência obrigatória de:

- OpenAI API;
- Anthropic API;
- Gemini API;
- Groq API;
- qualquer outra API paga de inferência.

O sistema poderá futuramente possuir integrações externas para outras finalidades, mas o funcionamento principal deverá permanecer local.

---

# 4. Hardware de referência

O sistema será desenvolvido considerando como hardware de referência:

- Intel Core i7-1255U;
- 16 GB de RAM;
- Intel Iris Xe Graphics;
- aproximadamente 512 GB de SSD;
- Windows;
- WSL2;
- Ollama.

O projeto deverá considerar que a máquina possui recursos limitados.

Portanto, todas as decisões técnicas deverão considerar:

- consumo de RAM;
- consumo de CPU;
- consumo de armazenamento;
- latência;
- número de processos;
- tamanho dos modelos;
- quantidade de dependências;
- frequência de coleta de métricas;
- impacto do dashboard;
- impacto do banco;
- impacto do próprio agente.

Não é aceitável resolver um problema adicionando um serviço pesado sem necessidade.

---

# 5. Estratégia de modelos

Os modelos deverão ser configuráveis.

Modelos iniciais esperados:

- Qwen3 4B para tarefas gerais;
- Qwen2.5-Coder 3B para programação;
- modelo menor opcional para tarefas extremamente simples.

Os nomes dos modelos não deverão estar espalhados pelo código.

A aplicação deverá possuir uma configuração centralizada.

Exemplo conceitual:

```yaml
models:
  general: qwen3:4b
  coding: qwen2.5-coder:3b
  lightweight: qwen3:1.7b
```

Os valores acima representam configuração inicial e podem ser alterados sem modificar o código-fonte.

---

# 6. Princípios arquiteturais

O projeto deverá seguir:

- Separation of Concerns;
- SOLID;
- Dependency Inversion;
- KISS;
- DRY;
- composição sobre herança quando apropriado;
- baixo acoplamento;
- alta coesão;
- interfaces para componentes substituíveis;
- configuração externa;
- responsabilidade única;
- testes automatizados.

DRY não deverá ser utilizado para criar abstrações artificiais.

O projeto deve preferir código simples e explícito quando uma abstração não trouxer benefício real.

---

# 7. Design Patterns

Padrões de projeto poderão ser utilizados quando resolverem problemas concretos.

Padrões potencialmente úteis:

- Strategy;
- Adapter;
- Factory;
- Repository;
- Dependency Injection;
- Command;
- Observer;
- Event Bus;
- State.

Não implementar um padrão somente para aumentar a sofisticação arquitetural.

---

# 8. Arquitetura geral

A arquitetura deverá possuir as seguintes camadas:

```text
Interface
    |
    v
Application
    |
    v
Agent
    |
    v
Harness
    |
    v
Policies
    |
    v
Tools
    |
    +------------------+
    |                  |
    v                  v
 Ollama           External Services
                       |
                       +-- GitHub
                       +-- Web
                       +-- MCP
```

A observabilidade será transversal:

```text
Agent
  |
Harness
  |
Tools
  |
Validation
  |
  +------> Observability
               |
               v
            SQLite
               |
               v
            FastAPI
               |
               v
          Web Dashboard
```

---

# 9. Componentes principais

## 9.1 Interface

A interface será responsável por receber solicitações e apresentar resultados.

A implementação inicial poderá ser:

- CLI;
- interface web simples.

O projeto deverá evitar criar uma interface complexa antes do núcleo estar funcionando.

---

# 10. Agent

O Agent será responsável pela inteligência de execução.

Responsabilidades:

- interpretar a solicitação;
- identificar objetivo;
- determinar tipo de tarefa;
- elaborar plano;
- selecionar ferramentas;
- produzir ações;
- analisar resultados;
- decidir próximos passos.

O Agent não deverá implementar diretamente:

- acesso a arquivos;
- execução de comandos;
- Git;
- GitHub;
- banco;
- coleta de hardware;
- cálculo de custo.

Essas responsabilidades pertencem a outros componentes.

---

# 11. Harness

O Harness é um componente central do projeto.

Ele será responsável por controlar o ciclo de execução do agente.

Fluxo:

```text
PLAN
  |
  v
ACT
  |
  v
OBSERVE
  |
  v
VERIFY
  |
  +---- sucesso ----> COMPLETE
  |
  +---- falha ------> FIX
                         |
                         v
                       ACT
```

O Harness deverá possuir:

- limite máximo de iterações;
- timeout global;
- timeout por ferramenta;
- cancelamento;
- detecção de loops;
- detecção de ausência de progresso;
- registro de erros;
- execução de validações;
- controle de permissões;
- telemetria;
- identificação da execução.

---

# 12. Regra de conclusão

O modelo nunca poderá determinar sozinho que uma tarefa foi concluída.

A conclusão deverá ser baseada em evidências.

Exemplo:

```text
O agente afirma que corrigiu o código.

O Harness executa:

1. Ruff
2. Mypy
3. Pytest
4. Build

Resultado:

Ruff: aprovado
Mypy: aprovado
Pytest: aprovado
Build: aprovado

A tarefa pode ser considerada concluída.
```

Se qualquer validação obrigatória falhar, a tarefa não deverá ser considerada concluída.

---

# 13. Ferramentas

As ferramentas deverão ser independentes do Agent.

Ferramentas planejadas:

```text
Filesystem
Terminal
Git
GitHub
Web
Skills
MCP
```

Cada ferramenta deverá possuir:

- nome;
- descrição;
- schema de entrada;
- resultado estruturado;
- tratamento de erro;
- timeout;
- política de segurança;
- telemetria.

---

# 14. Filesystem Tool

A ferramenta deverá permitir:

- listar diretórios;
- ler arquivos;
- criar arquivos;
- editar arquivos;
- excluir arquivos somente quando permitido;
- criar diretórios.

Deverá existir proteção contra:

- path traversal;
- acesso fora do workspace;
- arquivos proibidos;
- operações destrutivas não autorizadas.

O workspace deverá ser configurável.

---

# 15. Terminal Tool

A ferramenta deverá permitir execução de comandos dentro do workspace.

Cada execução deverá registrar:

- comando;
- diretório;
- início;
- fim;
- duração;
- stdout;
- stderr;
- exit code;
- status.

Deverá possuir:

- timeout;
- limite de saída;
- cancelamento;
- política de comandos;
- bloqueio de operações perigosas.

Comandos destrutivos deverão exigir confirmação ou ser bloqueados conforme a policy.

---

# 16. Git Tool

A ferramenta Git deverá permitir:

- status;
- diff;
- log;
- branch;
- checkout;
- criação de branch;
- commit;
- eventualmente push.

O Git deverá ser utilizado de forma incremental.

Branches esperadas:

```text
main
feature/<nome>
fix/<nome>
refactor/<nome>
test/<nome>
docs/<nome>
chore/<nome>
```

---

# 17. GitHub Tool

A integração com GitHub deverá ser adicionada após o núcleo estar estável.

Possibilidades:

- consultar repositório;
- consultar issues;
- consultar pull requests;
- criar branch;
- criar commit;
- push;
- eventualmente criar pull requests.

Operações que alteram estado remoto deverão estar protegidas por policy.

---

# 18. Web Tool

A ferramenta Web deverá permitir:

- pesquisar informações;
- abrir URLs;
- consultar documentação;
- extrair conteúdo relevante.

O acesso web deverá ser explicitamente acionado.

O modelo não deverá ter acesso irrestrito à internet por padrão.

---

# 19. Skills

Skills serão instruções e capacidades especializadas carregáveis pelo agente.

O sistema deverá permitir:

- descobrir Skills;
- carregar Skill;
- validar Skill;
- aplicar Skill;
- registrar uso.

O carregamento deverá possuir contexto e escopo.

---

# 20. MCP

MCP deverá ser implementado posteriormente.

O sistema deverá possuir:

- cliente MCP;
- descoberta de ferramentas;
- schemas;
- permissões;
- timeout;
- tratamento de erro;
- auditoria.

Ferramentas MCP deverão ser tratadas como ferramentas externas e potencialmente não confiáveis.

---

# 21. Memória

O sistema deverá diferenciar:

### Contexto da execução

Informações necessárias para a tarefa atual.

### Estado da sessão

Informações temporárias durante a sessão.

### Memória persistente

Informações explicitamente aprovadas para armazenamento.

### Conhecimento/documentos

Conteúdo externo recuperável.

Não armazenar tudo automaticamente.

---

# 22. Observabilidade

A observabilidade é requisito fundamental.

Toda execução significativa deverá possuir um `execution_id`.

Exemplo:

```text
execution_id = 01JXXXXXXXXXXXX
```

Todas as operações associadas à execução deverão utilizar esse identificador.

---

# 23. Objetivo da observabilidade

O sistema deverá responder:

- O que aconteceu?
- Quando aconteceu?
- Qual modelo foi usado?
- Quais ferramentas foram utilizadas?
- Quantas vezes o modelo foi chamado?
- Quanto tempo demorou?
- Quantos tokens foram processados?
- Quantas iterações ocorreram?
- Quantos erros ocorreram?
- Quanto CPU foi utilizado?
- Quanto RAM foi utilizado?
- Quanto GPU foi utilizado?
- Qual foi o custo computacional estimado?
- A tarefa terminou com sucesso?
- Houve intervenção humana?

---

# 24. Sistema de eventos

Eventos deverão possuir estrutura consistente.

Campos mínimos:

```text
event_id
execution_id
timestamp
event_type
status
metadata
```

Eventos iniciais:

```text
execution_started
execution_completed
execution_failed
execution_cancelled

model_started
model_completed
model_failed

tool_started
tool_completed
tool_failed

harness_iteration

validation_started
validation_completed

test_started
test_completed

git_operation

web_request

mcp_operation

skill_loaded

hardware_sample
```

---

# 25. Execution

Uma execução representa uma tarefa completa.

Exemplo:

```text
execution_id: abc123
task_type: coding
model: qwen2.5-coder:3b
status: completed
duration_ms: 84000
iterations: 2
tool_calls: 7
retries: 1
success: true
```

---

# 26. Métricas de modelo

Registrar, quando disponível:

- modelo;
- versão/tag;
- duração;
- prompt tokens;
- completion tokens;
- total tokens;
- tokens por segundo;
- status.

Nunca inventar informações que o runtime não forneceu.

Quando uma métrica não estiver disponível, armazenar `NULL`.

---

# 27. Métricas de execução

Cada execução deverá permitir calcular:

- duração total;
- tempo de inferência;
- tempo de ferramentas;
- quantidade de chamadas de modelo;
- quantidade de ferramentas;
- quantidade de retries;
- quantidade de iterações;
- quantidade de erros;
- status;
- intervenção humana.

---

# 28. Métricas de qualidade

O sistema deverá acompanhar:

- taxa de sucesso;
- taxa de falha;
- taxa de timeout;
- taxa de cancelamento;
- taxa de sucesso na primeira tentativa;
- número médio de iterações;
- número médio de retries;
- número de tarefas que exigiram intervenção;
- quantidade de validações aprovadas;
- quantidade de validações falhas.

---

# 29. Monitoramento de hardware

Durante execuções, o sistema deverá coletar, quando possível:

### CPU

- percentual de utilização;
- média;
- máximo.

### RAM

- RAM utilizada;
- percentual;
- pico.

### GPU

- percentual de utilização;
- memória utilizada;
- memória disponível;
- temperatura quando disponível;
- consumo quando disponível.

O sistema não deverá assumir que todas as métricas estarão disponíveis no Intel Iris Xe.

Campos não disponíveis deverão permanecer como `NULL`.

---

# 30. Sampling

A coleta deverá ser periódica.

Configuração exemplo:

```yaml
telemetry:
  hardware_sampling_interval_seconds: 2
```

A frequência deverá ser configurável.

O monitoramento não poderá consumir recursos excessivos.

---

# 31. Custo computacional

O sistema deverá calcular uma estimativa do custo de execução.

A estimativa poderá considerar:

- tempo de execução;
- CPU;
- GPU;
- potência configurada;
- energia;
- preço do kWh.

Fórmula:

```text
energia_kwh =
potencia_media_kw × duracao_horas
```

Depois:

```text
custo =
energia_kwh × preco_kwh
```

O resultado deverá ser identificado como estimativa.

Caso exista medição física mais precisa, ela poderá substituir a estimativa.

---

# 32. Banco de dados

O banco inicial será SQLite.

Motivos:

- simples;
- local;
- leve;
- sem servidor separado;
- adequado para uso individual;
- baixo consumo.

A aplicação deverá acessar o banco através de uma camada de persistência.

SQL não deverá ser espalhado pelas regras de negócio.

---

# 33. Entidades do banco

O banco deverá possuir, no mínimo:

```text
executions
model_runs
tool_runs
harness_iterations
validation_runs
hardware_samples
errors
git_operations
web_operations
mcp_operations
skills_usage
```

Entidades poderão ser adicionadas posteriormente quando houver necessidade real.

---

# 34. API

A API será implementada com FastAPI.

Endpoints mínimos:

```text
GET /api/health

GET /api/metrics/overview

GET /api/metrics/executions
GET /api/metrics/executions/{execution_id}

GET /api/metrics/models
GET /api/metrics/tools
GET /api/metrics/hardware
GET /api/metrics/costs
GET /api/metrics/errors
GET /api/metrics/harness
GET /api/metrics/timeseries
```

---

# 35. Dashboard

O dashboard será uma aplicação web local.

Ele deverá consumir a API.

O dashboard não deverá acessar SQLite diretamente.

Fluxo:

```text
Dashboard
    |
    v
FastAPI
    |
    v
Repository
    |
    v
SQLite
```

---

# 36. Dashboard — Overview

A página inicial deverá apresentar:

### KPIs

- total de execuções;
- execuções concluídas;
- execuções falhas;
- taxa de sucesso;
- duração média;
- tokens utilizados;
- chamadas de ferramentas;
- erros;
- custo computacional estimado.

### Gráficos

- execuções por período;
- duração ao longo do tempo;
- taxa de sucesso;
- uso de modelos;
- consumo de CPU;
- consumo de RAM;
- custo ao longo do tempo.

---

# 37. Dashboard — Performance

Deverá apresentar:

- média;
- mediana;
- P95;
- P99 quando houver dados suficientes;
- tokens/s;
- duração por modelo;
- duração por tarefa;
- duração das ferramentas;
- número de retries.

---

# 38. Dashboard — Modelos

Comparar:

- modelo;
- quantidade de execuções;
- taxa de sucesso;
- taxa de falha;
- latência;
- tokens/s;
- tokens utilizados;
- CPU;
- RAM;
- custo estimado.

O objetivo é descobrir qual modelo apresenta melhor relação entre:

```text
qualidade
+
velocidade
+
consumo
+
custo
```

---

# 39. Dashboard — Hardware

Apresentar:

- CPU média;
- CPU máxima;
- RAM média;
- RAM máxima;
- GPU média;
- GPU máxima;
- memória GPU;
- evolução temporal;
- consumo por execução.

---

# 40. Dashboard — Custos

Apresentar:

- custo total;
- custo diário;
- custo mensal;
- custo por execução;
- custo por modelo;
- custo por tipo de tarefa;
- energia estimada;
- tempo computacional.

Os valores devem deixar claro quando são estimativas.

---

# 41. Dashboard — Execuções

Criar tabela contendo:

- execution ID;
- data;
- tarefa;
- modelo;
- duração;
- status;
- iterações;
- chamadas de ferramentas;
- tokens;
- custo.

Permitir abrir uma execução.

---

# 42. Dashboard — Detalhes da execução

Mostrar:

```text
Resumo
Timeline
Chamadas do modelo
Chamadas de ferramentas
Iterações do Harness
Validações
Hardware
Erros
Custo
```

Timeline esperada:

```text
20:00:01 Execution started
20:00:02 Model started
20:00:07 Model completed
20:00:08 Filesystem read
20:00:10 Terminal command
20:00:15 Validation started
20:00:18 Validation completed
20:00:19 Execution completed
```

---

# 43. Dashboard — Harness

Mostrar:

- média de iterações;
- máximo de iterações;
- primeira tentativa;
- retries;
- loops;
- timeouts;
- correções;
- tempo de validação.

---

# 44. Dashboard — Erros

Mostrar:

- erros por categoria;
- erros por modelo;
- erros por ferramenta;
- erros por período;
- frequência;
- reincidência.

Categorias:

```text
model
tool
filesystem
terminal
git
github
web
mcp
validation
timeout
policy
system
```

---

# 45. Privacidade

Por padrão, não armazenar integralmente:

- prompts;
- respostas;
- arquivos;
- senhas;
- tokens;
- API keys;
- credenciais;
- conteúdo sensível.

O sistema deverá priorizar metadados.

Caso seja necessário armazenar conteúdo:

- deverá existir configuração explícita;
- aplicar redaction;
- nunca registrar secrets;
- documentar o comportamento.

---

# 46. Segurança

O sistema deverá:

- restringir filesystem ao workspace;
- impedir path traversal;
- validar comandos;
- aplicar timeouts;
- impedir operações destrutivas sem autorização;
- proteger credenciais;
- não colocar secrets no Git;
- não executar push silencioso quando policy exigir confirmação;
- registrar operações críticas.

---

# 47. Estratégia de testes

### Testes unitários

Cobrir:

- Agent;
- Harness;
- Policies;
- Tools;
- repositories;
- telemetry;
- métricas;
- cálculo de custo.

### Testes de integração

Cobrir:

- Ollama;
- SQLite;
- FastAPI;
- tools;
- telemetry.

### Testes E2E

Validar:

```text
solicitação
→ Agent
→ Harness
→ Tool
→ Validation
→ Telemetry
→ SQLite
→ API
→ Dashboard
```

---

# 48. Validação obrigatória

Antes de concluir uma tarefa:

```text
Ruff
↓
Mypy
↓
Pytest
↓
Integration tests
↓
Build/startup
↓
Security checks
↓
Git diff review
```

Qualquer falha relevante deverá ser corrigida antes da conclusão.

---

# 49. Git

Branch principal:

```text
main
```

Branches:

```text
feature/<nome>
fix/<nome>
refactor/<nome>
test/<nome>
docs/<nome>
chore/<nome>
```

Commits:

```text
feat:
fix:
refactor:
test:
docs:
chore:
build:
ci:
```

Commits deverão ser pequenos e semanticamente claros.

---

# 50. Exemplos de commits corretos

```text
feat: initialize assistant project
feat: add Ollama client
test: cover Ollama client
feat: add filesystem tool
feat: add terminal tool
feat: implement harness execution loop
feat: add execution telemetry
feat: persist execution metrics
test: cover telemetry repository
feat: add metrics API
feat: add dashboard overview
feat: add hardware metrics
feat: add computational cost metrics
```

Evitar:

```text
feat: create complete AI assistant
```

---

# 51. Performance

Performance deverá ser considerada desde o início.

Monitorar:

- tempo de inicialização;
- tempo de inferência;
- tempo de ferramentas;
- consumo de RAM;
- consumo de CPU;
- tamanho do banco;
- tamanho de logs;
- tamanho de contexto;
- número de processos.

---

# 52. Retenção de dados

A telemetria deverá possuir política de retenção configurável.

Exemplo:

```yaml
telemetry:
  retention_days: 90
```

O sistema poderá futuramente possuir:

- limpeza automática;
- agregação de métricas antigas;
- compactação;
- exportação.

---

# 53. Resiliência da observabilidade

A falha da telemetria não deverá necessariamente derrubar o agente.

Por padrão:

```text
Agent failure
≠
Telemetry failure
```

O sistema deverá continuar funcionando quando possível.

Entretanto, operações críticas poderão possuir policy que exija auditoria.

---

# 54. Ordem de implementação

A ordem recomendada é:

```text
1. Fundação
2. Configuração
3. Ollama
4. Agent
5. Filesystem
6. Terminal
7. Harness
8. Validation
9. Observability
10. SQLite
11. Hardware monitoring
12. Cost calculation
13. FastAPI
14. Dashboard
15. Git
16. GitHub
17. Web
18. Skills
19. MCP
20. Memory
```

---

# 55. Estrutura de diretórios

A estrutura inicial deverá ser:

```text
local-ai-assistant/
│
├── docs/
│   ├── PROJECT.md
│   ├── BACKLOG.md
│   └── architecture/
│
├── src/
│   └── assistant/
│       ├── __init__.py
│       │
│       ├── agent/
│       ├── harness/
│       ├── models/
│       ├── tools/
│       │   ├── filesystem/
│       │   ├── terminal/
│       │   ├── git/
│       │   ├── github/
│       │   └── web/
│       │
│       ├── skills/
│       ├── mcp/
│       ├── memory/
│       ├── policies/
│       │
│       ├── observability/
│       │   ├── events/
│       │   ├── metrics/
│       │   ├── telemetry/
│       │   └── repositories/
│       │
│       ├── database/
│       ├── api/
│       │   └── metrics/
│       │
│       └── config/
│
├── dashboard/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/
│
├── .github/
│   └── workflows/
│
├── pyproject.toml
├── README.md
├── .env.example
└── .gitignore
```

---

# 56. Definition of Done

Uma tarefa somente poderá ser considerada concluída quando:

1. código implementado;
2. critérios de aceitação atendidos;
3. testes relevantes criados;
4. testes executados;
5. Ruff executado;
6. Mypy executado;
7. integração validada quando aplicável;
8. segurança revisada;
9. documentação atualizada;
10. backlog atualizado;
11. Git diff revisado;
12. nenhuma credencial adicionada;
13. nenhuma funcionalidade quebrada;
14. nenhum TODO crítico criado;
15. commit semântico realizado.

---

# 57. Objetivo final

O sistema final deverá permitir que o usuário execute tarefas através de um agente local e acompanhe sua eficiência através de um painel de observabilidade.

O usuário deverá conseguir descobrir:

- quantas vezes utilizou a IA;
- quais tarefas executou;
- quais modelos utilizou;
- qual modelo é mais eficiente;
- quanto tempo as tarefas levam;
- quanto CPU consomem;
- quanto RAM consomem;
- quanto GPU consomem;
- quantos tokens utilizam;
- quantas ferramentas utilizam;
- quantos retries ocorrem;
- quantas tarefas falham;
- onde ocorrem as falhas;
- quanto custa computacionalmente;
- quanto evoluiu ao longo do tempo.

O dashboard deverá transformar o uso do agente em dados mensuráveis.

O projeto não deverá apenas executar IA.

Ele deverá permitir **medir, compreender, depurar e melhorar a própria IA**.