# Local AI Assistant 🧠🚀

Um assistente de Inteligência Artificial **100% local, autônomo e focado em privacidade**. 

Projetado para operar em sua máquina Windows utilizando **Ollama**, o Local AI Assistant tem a capacidade de atuar ativamente no seu Workspace, executar comandos, acessar web, manipular repositórios Git/GitHub e consumir servidores MCP (Model Context Protocol). Tudo com uma camada robusta de telemetria e segurança, mantendo seus dados protegidos localmente.

---

## 🚀 Funcionalidades Principais

- **100% Local**: Funciona offline alimentado por modelos rodando na sua própria máquina (via Ollama).
- **Harness Autônomo**: Loop interno (`PLAN`, `ACT`, `OBSERVE`, `VERIFY`) capaz de pensar, agir, validar a própria ação e corrigir erros autonomamente.
- **Memória de Longo Prazo**: Sistema de sessão temporária (para contexto rápido) e persistência de memórias com regras e políticas restritas.
- **Ferramentas Integradas (Tools)**:
  - **Sistema Operacional:** Acesso de leitura e escrita ao File System, limitados ao seu Workspace.
  - **Git & GitHub:** Pode criar branchs, commitar, puxar relatórios de Issues e PRs e empurrar código de volta ao repositório.
  - **Web & Pesquisa:** Busca na web, acesso à documentação de bibliotecas externas e leitura de sites.
- **Model Context Protocol (MCP)**: Integração via JSON-RPC 2.0 sobre `stdio` para plugar ferramentas adicionais, validado por políticas de Allow/Blocklists.
- **Segurança Rigorosa**: Bloqueio de comandos destrutivos (como `rm -rf`), boundary de diretório para evitar "path traversals" e detecção/ofuscamento automático de API Keys e Senhas (Secrets Masking).
- **Extensibilidade (Skills)**: Capacidade de receber instruções e scripts dinâmicos de como realizar tarefas.

---

## 📦 Instalação

### Pré-requisitos
- Python 3.12+ (O projeto utiliza `uv` ou `pip` para gerenciamento)
- [Ollama](https://ollama.com) instalado na máquina para servir os modelos.

### Passo a passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/DanielDPereira/local-ai-assistant.git
   cd local-ai-assistant
   ```

2. **Crie e ative o ambiente virtual**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -e .[dev]
   ```

4. **Baixe os modelos recomendados no Ollama**
   ```bash
   ollama pull qwen3:4b
   ollama pull qwen2.5-coder:3b
   ollama pull qwen3:1.7b
   ```

---

## 💻 Como Rodar

O assistente expõe seus serviços via uma API FastAPI que também entrega uma Dashboard gráfica leve.

### Subindo o Servidor / Dashboard

Na raiz do projeto, com o seu ambiente ativado, execute:

```bash
uvicorn src.assistant.api.main:app --reload
```

Acesse no seu navegador:
👉 **http://localhost:8000** (Dashboard e Chat interativo)
👉 **http://localhost:8000/docs** (Swagger/Documentação da API)

### Testando a Inteligência Local (CLI)

Se quiser disparar testes end-to-end simulando as capacidades core do Agente:
```bash
.venv\Scripts\pytest tests\integration\test_e2e.py -v -s
```

---

## 🛠️ Casos de Uso (Use Cases)

A arquitetura autônoma permite que você passe tarefas abstratas que o Agente destrinchará em múltiplos passos lógicos:

### 1. Refatoração de Código e Versionamento Automático
*"Analise o arquivo `api.py`. Quero que extraia as rotas para um módulo de `routers/`. Faça a refatoração, garanta que nada quebrou, crie uma branch `refatoracao-rotas` e faça um commit de suas mudanças."*
> **Como ele atua:** Usará `File I/O Tools` para ler e alterar o arquivo localmente no workspace. Em seguida usará `Git Tools` (status, branch, commit) de forma autônoma para criar o histórico seguro da alteração.

### 2. Pesquisa Externa, Extração e Escrita
*"Pesquise na web a sintaxe de uso do novo pydantic v2. Crie um script de exemplo testando BaseModel no meu repositório e chame-o de `teste_pydantic.py`."*
> **Como ele atua:** Usará as `Web Tools` e `Docs Lookup` para baixar o contexto e aprender sobre o pacote, para então usar `File Write Tool` e escrever o arquivo executável na raiz do projeto.

### 3. Recuperação de Memória e Ações Contínuas
*"Lembra do nosso padrão arquitetural de usar injeção de dependência? Baseado nele, escreva um novo serviço de cache persistente."*
> **Como ele atua:** O Agente vai varrer a `PersistentMemory` e a `SessionState` para resgatar o contexto do que vocês definiram como padrão arquitetural e usará esse contexto imediatamente no output de código.

---

## 🛡️ Telemetria e Segurança
- Logs de segurança são mantidos de forma auditável.
- Quaisquer comandos enviados ao sistema ou via ferramentas MCP são avaliados pelo módulo de segurança `DestructiveOperationPolicy`.
- Caso tente visualizar um arquivo, os bounds bloqueiam fugas do diretório principal.

---

## 📖 Documentação Adicional
- **[Backlog do Projeto (Concluído)](docs/BACKLOG.md)**
- **[Guia Mestre de Design (Initial Prompt)](docs/INITIAL_PROMPT.md)**
- **[Manuais de Testes de Qualidade](docs/TESTING.md)**