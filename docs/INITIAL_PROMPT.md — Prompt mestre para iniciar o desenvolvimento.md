# Prompt Mestre para Desenvolvimento

Você será responsável pelo desenvolvimento deste projeto de Assistente de IA Local.

Leia integralmente os seguintes documentos antes de modificar qualquer código:

```text
docs/PROJECT.md
docs/BACKLOG.md
```

Esses documentos definem a arquitetura, os requisitos, o backlog, as regras de segurança, os critérios de qualidade e a estratégia de desenvolvimento.

Não trate esses arquivos como documentação opcional.

Eles são a especificação oficial do projeto.

---

# 1. Objetivo do projeto

Estamos desenvolvendo um assistente pessoal de Inteligência Artificial executado localmente.

O sistema deverá utilizar Ollama para executar modelos locais e deverá evoluir progressivamente para um agente capaz de:

- compreender tarefas;
- planejar;
- executar ferramentas;
- trabalhar com arquivos;
- executar comandos;
- executar testes;
- corrigir problemas;
- validar alterações;
- trabalhar com Git;
- trabalhar com GitHub;
- consultar a Web;
- utilizar Skills;
- utilizar MCP;
- utilizar memória controlada;
- operar através de um Harness;
- registrar suas próprias execuções;
- medir desempenho;
- medir consumo de hardware;
- estimar custo computacional;
- fornecer essas informações em uma API;
- apresentar essas informações em um dashboard web.

---

# 2. Restrição fundamental

A inferência deverá ser 100% local.

Utilize Ollama.

Não introduza dependências obrigatórias de APIs pagas de LLM.

Os modelos devem ser configuráveis.

Modelos iniciais esperados:

```text
Qwen3 4B
Qwen2.5-Coder 3B
```

Modelos menores poderão ser utilizados para tarefas simples.

Não codifique esses modelos diretamente no Agent.

---

# 3. Hardware

Considere como ambiente de referência:

```text
Intel Core i7-1255U
16 GB RAM
Intel Iris Xe
aproximadamente 512 GB SSD
Windows
WSL2
Ollama
```

O projeto deve economizar recursos.

Não introduza:

- serviços pesados sem necessidade;
- containers desnecessários;
- bancos externos para o MVP;
- processos permanentes desnecessários;
- modelos grandes;
- bibliotecas grandes sem justificativa.

Performance deve ser considerada desde o início.

---

# 4. Regra absoluta: não implemente tudo de uma vez

Você não deve tentar desenvolver o projeto inteiro em uma única execução.

Trabalhe uma tarefa por vez.

O processo obrigatório é:

```text
INSPECT
↓
UNDERSTAND
↓
PLAN
↓
IMPLEMENT
↓
TEST
↓
VALIDATE
↓
REVIEW
↓
COMMIT
↓
UPDATE BACKLOG
```

Depois disso, pare.

Não avance várias Epics sem necessidade.

---

# 5. Primeira ação

Antes de escrever código:

1. verifique o sistema operacional;
2. verifique Python;
3. verifique Git;
4. verifique Ollama;
5. verifique modelos instalados;
6. verifique ambiente virtual;
7. verifique estrutura do projeto;
8. verifique estado do Git;
9. verifique branches;
10. leia `docs/PROJECT.md`;
11. leia `docs/BACKLOG.md`.

Não presuma que ferramentas estão instaladas.

Verifique.

---

# 6. Seleção da primeira tarefa

Depois da inspeção:

1. procure a primeira tarefa P0 pendente;
2. verifique se suas dependências estão concluídas;
3. se as dependências não estiverem concluídas, escolha a primeira dependência pendente;
4. implemente somente essa tarefa;
5. execute os testes;
6. execute validações;
7. atualize o backlog;
8. faça um commit semântico pequeno.

---

# 7. Arquitetura

Respeite:

- Separation of Concerns;
- SOLID;
- Dependency Inversion;
- KISS;
- DRY;
- composição sobre herança;
- baixo acoplamento;
- alta coesão;
- interfaces;
- Dependency Injection quando apropriado.

Não crie abstrações desnecessárias.

Não introduza Design Patterns apenas para parecer sofisticado.

Use padrões somente quando resolverem um problema concreto.

---

# 8. Agent

O Agent deverá ser responsável por raciocínio e coordenação.

Não coloque dentro do Agent:

- código de filesystem;
- código de terminal;
- SQL;
- código de Git;
- código de GitHub;
- código de hardware;
- cálculo de custos.

Essas funcionalidades deverão existir em componentes próprios.

---

# 9. Harness

O Harness é obrigatório.

O fluxo deverá ser:

```text
PLAN
↓
ACT
↓
OBSERVE
↓
VERIFY
↓
FIX
↓
ACT
↓
VERIFY
↓
COMPLETE
```

O Harness deverá controlar:

- número de iterações;
- timeout;
- retries;
- loops;
- ferramentas;
- validações;
- erros;
- telemetria.

Nunca permitir loops infinitos.

---

# 10. Critério de sucesso

Nunca aceite:

```text
"o modelo disse que terminou"
```

como evidência suficiente.

Exija evidências objetivas.

Para uma alteração de software, sempre que aplicável:

```text
Ruff
Mypy
Pytest
Build
```

devem ser executados.

Se alguma validação falhar:

```text
FIX
↓
TEST
↓
VALIDATE
```

Não ignore falhas.

---

# 11. Tools

As ferramentas deverão ser abstraídas.

Ferramentas previstas:

```text
Filesystem
Terminal
Git
GitHub
Web
Skills
MCP
```

Cada Tool deverá:

- possuir interface;
- validar entrada;
- executar operação;
- retornar resultado estruturado;
- tratar erro;
- possuir timeout quando apropriado;
- gerar telemetria;
- respeitar policies.

---

# 12. Segurança

Nunca:

- execute comandos destrutivos sem autorização;
- permita acesso fora do workspace;
- permita path traversal;
- coloque secrets no código;
- coloque secrets no Git;
- registre tokens em logs;
- exponha credenciais;
- faça push remoto sem respeitar policy;
- ignore validações;
- falsifique resultados de ferramentas.

---

# 13. Observabilidade

A observabilidade é parte essencial da arquitetura.

Não trate como funcionalidade cosmética.

Cada execução deverá possuir:

```text
execution_id
```

Todas as ações deverão ser associadas à execução.

---

# 14. Eventos

Utilize eventos estruturados.

Eventos previstos:

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

# 15. Métricas

Registrar quando disponíveis:

### Modelo

- nome;
- versão;
- duração;
- prompt tokens;
- completion tokens;
- total tokens;
- tokens/s.

### Execução

- duração;
- status;
- modelo;
- task type;
- ferramentas;
- retries;
- iterações;
- erros;
- intervenção humana.

### Ferramentas

- quantidade;
- duração;
- sucesso;
- falhas.

### Harness

- iterações;
- retries;
- loops;
- timeout;
- primeira tentativa.

---

# 16. Regra contra métricas inventadas

Nunca invente métricas.

Se o Ollama ou o sistema operacional não fornecer determinado valor:

```text
NULL
```

deve ser utilizado.

Nunca transformar uma aproximação em dado exato.

---

# 17. Hardware telemetry

Coletar, quando disponível:

```text
CPU %
RAM %
RAM usada
GPU %
GPU memory
GPU temperature
power
```

O sampling deverá ser configurável.

Valor inicial recomendado:

```text
2 segundos
```

Mas deve ser configurável.

Não colete a cada milissegundo.

---

# 18. Custo computacional

O sistema deverá estimar o custo de utilização local.

Utilize parâmetros configuráveis.

Exemplo:

```text
preço do kWh
potência estimada
tempo de execução
```

Fórmula:

```text
energia = potência × tempo
```

e:

```text
custo = energia × preço
```

O dashboard deverá informar claramente que se trata de estimativa quando não existir medição elétrica física.

---

# 19. Banco de dados

O banco inicial será SQLite.

Não utilize PostgreSQL no MVP sem necessidade concreta.

Crie uma camada Repository.

Não espalhe SQL pelo código.

Tabelas principais:

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

---

# 20. API

Utilize FastAPI.

Endpoints previstos:

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

A API deverá consumir repositories/services.

Não colocar SQL diretamente nos endpoints.

---

# 21. Dashboard

O dashboard deverá consumir a API.

Nunca acessar o SQLite diretamente.

Arquitetura:

```text
Dashboard
↓
FastAPI
↓
Service
↓
Repository
↓
SQLite
```

---

# 22. Dashboard obrigatório

Criar as seguintes áreas:

## Overview

Mostrar:

- execuções;
- sucesso;
- falha;
- duração;
- tokens;
- ferramentas;
- erros;
- custo.

## Performance

Mostrar:

- latência;
- duração;
- média;
- mediana;
- P95;
- tokens/s.

## Models

Comparar modelos.

## Hardware

Mostrar:

- CPU;
- RAM;
- GPU;
- picos;
- médias.

## Costs

Mostrar:

- custo;
- energia;
- custo por execução;
- custo por modelo;
- custo por tarefa.

## Executions

Mostrar histórico.

## Execution Detail

Mostrar timeline completa.

## Harness

Mostrar:

- iterações;
- retries;
- loops;
- timeouts;
- primeira tentativa.

## Errors

Mostrar:

- categoria;
- frequência;
- modelo;
- ferramenta;
- período.

---

# 23. Dashboard como ferramenta de engenharia

Não construa apenas gráficos bonitos.

O dashboard deve ajudar a tomar decisões.

Deve permitir responder:

```text
Qual modelo é mais rápido?

Qual modelo é mais eficiente?

Qual modelo consome menos RAM?

Qual modelo consome menos CPU?

Qual modelo tem maior taxa de sucesso?

Qual tarefa demora mais?

Qual ferramenta mais falha?

Quanto tempo é gasto em retries?

Quanto tempo é gasto em validação?

Qual tarefa consome mais recursos?

Quanto custa cada execução?

O sistema está melhorando?
```

---

# 24. Testes

Utilize:

```text
pytest
Ruff
mypy
```

Crie:

```text
tests/unit
tests/integration
tests/e2e
```

Não escrever testes apenas para aumentar cobertura.

Os testes devem validar comportamento real.

---

# 25. Testes de integração

Quando apropriado, testar:

```text
Agent
→ Ollama
→ Harness
→ Tool
→ Validation
→ Telemetry
→ SQLite
```

---

# 26. Teste E2E do sistema de observabilidade

Deverá existir eventualmente um teste equivalente a:

```text
1. iniciar execução;
2. executar tarefa;
3. utilizar ferramenta;
4. executar modelo;
5. executar validação;
6. finalizar execução;
7. verificar execution_id;
8. verificar eventos;
9. verificar SQLite;
10. consultar API;
11. verificar dados retornados.
```

---

# 27. Git

Sempre trabalhe com branch apropriada.

Exemplos:

```text
feature/ollama-client
feature/filesystem-tool
feature/harness
feature/telemetry
feature/metrics-api
feature/dashboard
fix/terminal-timeout
test/telemetry
refactor/repository-layer
```

---

# 28. Commits

Utilize Conventional Commits.

Tipos:

```text
feat
fix
refactor
test
docs
chore
build
ci
```

Exemplos:

```text
feat: add Ollama model adapter
test: cover Ollama adapter
feat: add execution telemetry
test: cover execution repository
feat: add metrics API
feat: add dashboard overview
```

Nunca crie commits genéricos como:

```text
update
changes
stuff
final
final2
fixes
```

---

# 29. Tamanho dos commits

Commits deverão ser pequenos.

Uma alteração lógica deve resultar em um commit.

Evite misturar:

```text
telemetry
+
dashboard
+
GitHub
+
MCP
```

em uma única alteração.

---

# 30. Pull/Push

Durante o desenvolvimento local:

- commit pode ser realizado após validação;
- push deverá seguir a policy definida;
- operações remotas não devem ser executadas silenciosamente quando exigirem confirmação.

---

# 31. Performance

Sempre considere:

```text
RAM
CPU
latência
armazenamento
processos
dependências
```

Antes de adicionar uma biblioteca pesada, avalie se a funcionalidade pode ser implementada com uma dependência menor ou com a biblioteca padrão.

---

# 32. Dependências

Não adicione uma dependência sem necessidade.

Para cada nova dependência, considere:

1. ela é realmente necessária?
2. existe solução na biblioteca padrão?
3. ela aumenta significativamente o consumo?
4. ela possui manutenção adequada?
5. ela possui impacto de segurança?
6. ela é compatível com o Python utilizado?

---

# 33. Banco

Não armazenar conteúdo sensível desnecessariamente.

Preferir:

```text
metadata
```

a:

```text
full prompt
full response
full file contents
```

O objetivo é observabilidade, não armazenamento indiscriminado de dados.

---

# 34. Erros

Todo erro deverá possuir tratamento adequado.

Não utilizar:

```python
except Exception:
    pass
```

sem justificativa explícita.

Não esconder erros.

Não utilizar fallback silencioso que mascara problema real.

---

# 35. Logs

Logs deverão ser estruturados quando apropriado.

Utilizar:

```text
timestamp
level
execution_id
component
event
message
```

Não incluir secrets.

---

# 36. Alterações arquiteturais

Se durante o desenvolvimento você descobrir que a arquitetura precisa mudar:

1. interrompa a implementação da tarefa;
2. explique o problema;
3. apresente a alteração necessária;
4. verifique impacto;
5. atualize `PROJECT.md` se necessário;
6. atualize `BACKLOG.md`;
7. somente depois implemente.

Não altere silenciosamente uma decisão arquitetural importante.

---

# 37. Não faça overengineering

Não implemente antecipadamente:

- sistemas distribuídos;
- Kubernetes;
- microservices;
- PostgreSQL;
- Redis;
- filas externas;
- observabilidade externa;
- infraestrutura cloud;
- modelos enormes.

Este projeto é inicialmente pessoal, local e executado em hardware limitado.

Prefira simplicidade.

---

# 38. Não simplifique demais

Ao mesmo tempo, não transforme tudo em um único arquivo.

Separar responsabilidades.

O objetivo é:

```text
simples
+
modular
+
testável
+
extensível
```

---

# 39. Ordem de desenvolvimento

Siga esta ordem:

```text
FASE 1
Fundação
↓
FASE 2
Ollama
↓
FASE 3
Agent
↓
FASE 4
Filesystem
↓
FASE 5
Terminal
↓
FASE 6
Harness
↓
FASE 7
Validation
↓
FASE 8
Observability
↓
FASE 9
SQLite
↓
FASE 10
Hardware
↓
FASE 11
Computational Cost
↓
FASE 12
FastAPI
↓
FASE 13
Dashboard
↓
FASE 14
Git
↓
FASE 15
GitHub
↓
FASE 16
Web
↓
FASE 17
Skills
↓
FASE 18
MCP
↓
FASE 19
Memory
```

---

# 40. Primeira execução obrigatória

Agora execute somente estas etapas:

## Etapa 1

Inspecione o ambiente.

## Etapa 2

Inspecione o repositório.

## Etapa 3

Leia completamente:

```text
docs/PROJECT.md
docs/BACKLOG.md
```

## Etapa 4

Verifique:

```text
Python
Git
Ollama
modelos Ollama
ambiente virtual
```

## Etapa 5

Verifique o estado atual do Git.

## Etapa 6

Identifique a primeira tarefa P0 pendente.

## Etapa 7

Verifique dependências.

## Etapa 8

Crie branch apropriada.

## Etapa 9

Implemente somente essa tarefa.

## Etapa 10

Crie testes.

## Etapa 11

Execute:

```text
pytest
ruff
mypy
```

quando esses componentes já estiverem configurados.

Não tente executar uma ferramenta que ainda não foi configurada sem antes configurá-la de acordo com a tarefa.

## Etapa 12

Revise o código.

## Etapa 13

Revise o Git diff.

## Etapa 14

Atualize o `BACKLOG.md`.

## Etapa 15

Faça um commit pequeno e semântico.

## Etapa 16

Informe o resultado.

---

# 41. Formato obrigatório do relatório após cada tarefa

Ao concluir uma tarefa, responda:

```text
Tarefa:
[identificador e nome completos]

Status:
Concluída / Bloqueada / Parcial

Objetivo:
[descrever o objetivo da tarefa]

Implementação:
[descrever exatamente o que foi implementado]

Arquivos criados:
[lista completa]

Arquivos modificados:
[lista completa]

Testes criados:
[lista completa]

Testes executados:
[comandos executados]

Resultado dos testes:
[resultado]

Validações executadas:
[lint, type-check, integração, build etc.]

Resultado das validações:
[resultado]

Problemas encontrados:
[descrever ou informar que nenhum foi encontrado]

Decisões técnicas:
[descrever decisões relevantes]

Segurança:
[descrever verificações]

Performance:
[descrever impacto]

Documentação atualizada:
[lista]

Backlog atualizado:
[sim/não]

Branch:
[nome]

Commit:
[hash e mensagem]

Próxima tarefa:
[identificador e nome completos]
```

Não utilize respostas vagas.

---

# 42. Regra de parada

Depois de concluir uma tarefa:

- não implemente automaticamente a próxima tarefa grande;
- não avance várias fases;
- não crie funcionalidades futuras;
- não faça refatorações não relacionadas;
- não adicione dependências por conveniência.

Finalize o ciclo e informe o resultado.

---

# 43. Critério de qualidade

Código deverá ser:

- legível;
- tipado;
- testável;
- modular;
- seguro;
- documentado quando necessário;
- simples;
- eficiente.

Evite:

- funções gigantes;
- classes gigantes;
- variáveis genéricas;
- lógica duplicada;
- dependências globais;
- estado global desnecessário;
- tratamento silencioso de erros;
- código morto;
- TODOs sem justificativa.

---

# 44. Regra para mudanças necessárias

Se uma tarefa revelar que outra funcionalidade precisa ser criada antes:

Não implemente silenciosamente uma grande funcionalidade adicional.

Faça:

```text
identificar dependência
→ registrar necessidade
→ verificar backlog
→ implementar dependência mínima
→ testar
→ retornar à tarefa original
```

---

# 45. Regra para problemas

Quando algo falhar:

```text
REPRODUZIR
↓
DIAGNOSTICAR
↓
IDENTIFICAR CAUSA
↓
CORRIGIR
↓
TESTAR
↓
VALIDAR
```

Não use workarounds sem compreender a causa.

---

# 46. Regra para o dashboard

O dashboard somente deverá ser desenvolvido depois que houver dados reais provenientes da telemetria.

Não criar gráficos com dados falsos apenas para demonstrar a interface.

Durante desenvolvimento, dados mockados poderão ser utilizados exclusivamente em testes automatizados e deverão ser claramente separados dos dados reais.

---

# 47. Regra para métricas

Nenhuma métrica deverá ser fabricada.

Se não houver dado:

```text
null
```

Se houver estimativa:

```text
estimated: true
```

Se houver medição real:

```text
estimated: false
```

Sempre que possível, o banco deverá distinguir medição de estimativa.

---

# 48. Regra para custos

O custo computacional deverá ser tratado como métrica de engenharia.

O objetivo não é apenas calcular dinheiro.

Também deverá ser possível analisar:

```text
tempo
energia
hardware
modelo
tarefa
resultado
```

Assim será possível comparar:

```text
modelo A:
mais rápido
mas consome mais RAM

modelo B:
mais lento
mas consome menos recursos

modelo C:
mais eficiente para tarefas simples
```

---

# 49. Resultado esperado

Ao final do projeto, o sistema deverá ser capaz de executar:

```text
Usuário
↓
solicitação
↓
Agent
↓
planejamento
↓
Harness
↓
Tools
↓
Ollama
↓
validação
↓
correções
↓
conclusão
```

Enquanto paralelamente:

```text
execução
↓
eventos
↓
telemetria
↓
SQLite
↓
FastAPI
↓
Dashboard
```

O usuário deverá conseguir visualizar e analisar o comportamento completo do agente.

---

# 50. Princípio final

Não construa apenas uma IA que responde.

Construa um sistema que consiga demonstrar:

```text
o que fez
como fez
por que fez
quanto demorou
quanto consumiu
quanto custou
onde falhou
como se recuperou
qual modelo utilizou
qual ferramenta utilizou
quantas tentativas realizou
se a tarefa realmente foi validada
```

O agente deverá ser **útil, seguro, observável, mensurável, eficiente e evolutivo**.

Comece pela inspeção do ambiente.

Não escreva código antes de entender o estado atual do projeto.

Depois disso, execute somente a primeira tarefa pendente do backlog.