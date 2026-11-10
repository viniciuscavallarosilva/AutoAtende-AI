# AutoAtende AI

**Protótipo de atendimento com inteligência artificial e agendamento de avaliações presenciais**

O **AutoAtende AI** é um protótipo de agente de atendimento para uma oficina mecânica fictícia. Ele recebe mensagens pelo **WhatsApp** e pelo **Telegram**, conduz conversas com apoio da API da OpenAI e utiliza regras de negócio e um banco de dados PostgreSQL para consultar e registrar agendamentos.

> **Status:** protótipo funcional, disponibilizado para demonstração técnica e aprendizado. Não é um produto pronto para operação comercial sem testes adicionais, monitoramento e melhorias de segurança.

**Idiomas:** Português | [English](https://github.com/viniciuscavallarosilva/AutoAtende-AI/blob/master/README_EN.md) **

## Funcionalidades

- Atendimento conversacional por WhatsApp e Telegram.
- Identificação e persistência de clientes e conversas.
- Continuidade de contexto entre mensagens de uma conversa.
- Consulta de disponibilidade e agendamento de avaliações presenciais.
- Reagendamento e consulta do agendamento atual, conforme as regras implementadas.
- Persistência de mensagens e agendamentos em PostgreSQL.
- Endpoint HTTP para testes e integração com outros sistemas.
- Execução em nuvem no Railway.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Backend | Python, FastAPI |
| Agente | API da OpenAI |
| Persistência | PostgreSQL, SQLAlchemy |
| WhatsApp | Meta WhatsApp Cloud API e webhooks |
| Telegram | Telegram Bot API, `python-telegram-bot` |
| Hospedagem | Railway |

## Arquitetura simplificada

```text
WhatsApp Cloud API ── webhook ──┐
                                │
Telegram Bot API ─── polling ───┼── FastAPI / lógica de atendimento
                                │                │
REST API ───────────────────────┘                ├── API da OpenAI
                                                 └── PostgreSQL
```

Os canais compartilham a lógica de atendimento e o banco de dados. O serviço HTTP e o polling do Telegram podem ser executados no mesmo processo, conforme a configuração do ambiente.

## Estrutura principal

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Inicialização do FastAPI, endpoints e ciclo de vida da aplicação |
| `webhook.py` | Recepção de eventos do WhatsApp |
| `telegram_bot.py` | Integração com o Telegram |
| `atendimento.py` | Fluxo compartilhado de atendimento e persistência |
| `agent.py` | Comunicação com o modelo e operações do agente |
| `database.py` | Conexão e sessões do banco |
| `models.py` | Modelos de dados SQLAlchemy |
| `schemas.py` | Contratos de entrada e saída da API |

> A estrutura acima corresponde aos módulos discutidos durante o desenvolvimento. Confira os nomes no repositório antes da publicação.

## Executar localmente

### Pré-requisitos

- Python compatível com as dependências do projeto.
- PostgreSQL acessível localmente ou por uma URL de conexão.
- Chave da API da OpenAI.
- Credenciais da Meta e/ou do Telegram para habilitar os respectivos canais.

### Instalação

```bash
git clone <URL_DO_REPOSITORIO>
cd <PASTA_DO_REPOSITORIO>
python -m venv .venv
```

No Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Copie o arquivo `.env.example` para `.env` e preencha as configurações necessárias. **Nunca publique o `.env` com credenciais reais.**

```bash
uvicorn main:app --reload
```

A documentação interativa da API estará disponível em `http://localhost:8000/docs`, caso o servidor seja iniciado na porta padrão.

**Importante:** o procedimento de criação das tabelas deve ser documentado de acordo com o mecanismo realmente utilizado pelo projeto (por exemplo, inicialização automática, script ou migrações). Não execute o atendimento antes de preparar o banco.

## Configuração das integrações

### OpenAI e PostgreSQL

Configure uma chave de API válida e a URL de conexão do banco. O modelo utilizado e os nomes exatos das variáveis devem corresponder aos lidos pelo código.

### WhatsApp (Meta Cloud API)

1. Crie ou selecione um aplicativo no [Meta for Developers](https://developers.facebook.com/).
2. Configure o produto WhatsApp e obtenha as credenciais necessárias.
3. Disponibilize o backend em um endereço HTTPS público.
4. Cadastre a URL do webhook e o token de verificação no painel da Meta.
5. Inscreva o aplicativo nos eventos de mensagens relevantes.
6. Verifique as permissões e restrições do número e da conta de WhatsApp Business.

A integração com a Meta exige configuração externa ao código e pode variar conforme o ambiente de teste ou produção. Não compartilhe tokens, segredos do aplicativo ou dados de clientes.

### Telegram

1. Crie um bot com o [BotFather](https://t.me/BotFather).
2. Configure o token do bot no ambiente.
3. Habilite o polling somente no processo que deve consumir as mensagens.
4. Evite executar simultaneamente duas instâncias de polling com o mesmo token, pois isso pode gerar conflitos.

## Deploy no Railway

O protótipo utiliza um serviço para a API e as integrações, além de um banco PostgreSQL. O comando de inicialização utilizado no ambiente de deploy é:

```bash
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
```

Configure as variáveis de ambiente no serviço, conecte o PostgreSQL e utilize o domínio HTTPS gerado pelo Railway para o webhook do WhatsApp. Em produção, mantenha apenas uma instância de polling do Telegram por bot.

## Limitações conhecidas e melhorias planejadas

- Tratar mensagens de áudio recebidas e, futuramente, transcrevê-las.
- Garantir idempotência no processamento de eventos do WhatsApp.
- Ampliar a consulta do histórico de agendamentos, incluindo cancelamentos.
- Melhorar a edição dos dados de um agendamento.
- Bloquear feriados nacionais, estaduais e municipais na agenda.
- Aprimorar tratamento de erros, observabilidade e segurança.
- Evoluir a identificação de clientes entre diferentes canais.

## Segurança e uso responsável

Este repositório não deve conter credenciais, arquivos `.env`, dados pessoais de clientes nem dumps reais do banco. Antes de disponibilizá-lo publicamente, revise também o histórico de commits e revogue qualquer credencial que tenha sido exposta.

## Licença e Uso do Código

Este repositório é disponibilizado publicamente para fins de demonstração técnica, consulta e estudo.

O código permanece protegido por direitos autorais. Não é concedida, neste momento, uma licença para redistribuição, modificação ou utilização em outros projetos.

Caso tenha interesse em utilizar alguma parte da implementação, entre em contato para solicitar autorização.

## Sobre o projeto

Projeto demonstrativo de integração entre agentes de IA, canais de mensageria, APIs, regras de negócio e persistência de dados. O objetivo é apresentar uma implementação funcional de ponta a ponta e documentar sua evolução técnica.
