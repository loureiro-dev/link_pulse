# 🚀 LinkPulse - Sistema de Monitoramento de Links WhatsApp

> **Projeto SaaS profissional para coleta automatizada e monitoramento de links de grupos WhatsApp**

LinkPulse é uma aplicação web moderna desenvolvida como projeto de portfólio, criada para automatizar o processo de monitoramento e coleta de links de grupos WhatsApp em páginas de captura. O sistema oferece autenticação segura, dashboard interativo e integração com Telegram para notificações.

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Endpoints da API](#endpoints-da-api)
- [Funcionalidades](#funcionalidades)
- [Segurança](#segurança)
- [Próximos Passos](#próximos-passos)

---

## 🎯 Sobre o Projeto

Este projeto foi desenvolvido como parte de um portfólio pessoal focado em **Data Science** e **Engenharia de Dados**. O objetivo principal é demonstrar habilidades em:

- **Web Scraping**: Extração de dados de páginas web (Requests + BeautifulSoup + Selenium)
- **Desenvolvimento Backend**: API REST com FastAPI e autenticação JWT
- **Desenvolvimento Frontend**: Interface moderna com Next.js 14 e Tailwind CSS
- **Engenharia de Dados**: Pipeline de coleta, processamento e armazenamento
- **Banco de Dados**: SQLite para armazenamento simples e eficiente

### O Problema que Resolve

Muitos produtores digitais escondem links de grupos WhatsApp em:
- HTML complexo ou quebrado
- Scripts JavaScript
- iframes
- Campos invisíveis
- Redirecionamentos

O LinkPulse automatiza esse processo, coletando, normalizando e armazenando esses links automaticamente.

---

## 🛠 Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework moderno e rápido para APIs REST
- **Python 3.11+** - Linguagem principal
- **SQLite** - Banco de dados leve e simples
- **JWT** - Autenticação segura com tokens
- **BeautifulSoup4** - Parser HTML
- **Selenium** - Web scraping de páginas JavaScript (opcional)
- **Requests** - Cliente HTTP

### Frontend
- **Next.js 14** - Framework React com App Router
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização moderna e responsiva
- **Recharts** - Gráficos e visualizações
- **js-cookie** - Gerenciamento de cookies para autenticação

### DevOps
- **Uvicorn** - Servidor ASGI para FastAPI
- **Docker** (opcional) - Containerização

---

## 📁 Estrutura do Projeto

```
linkpulse/
│
├── backend/                 # Backend FastAPI
│   ├── api/                # Rotas da API organizadas por recurso
│   ├── auth/               # Módulo de autenticação JWT
│   │   ├── models.py       # Modelos Pydantic
│   │   ├── jwt.py          # Geração e validação de tokens
│   │   ├── middleware.py   # Middleware de proteção
│   │   └── routes.py       # Rotas de login/registro
│   ├── db/                 # Módulo de banco de dados
│   │   ├── connection.py   # Conexão SQLite
│   │   ├── users.py        # Operações de usuários
│   │   └── migrations/     # Migrações futuras
│   ├── services/           # Lógica de negócio
│   │   ├── collectors/     # Coleta de links
│   │   │   ├── requests_collector.py
│   │   │   └── selenium_collector.py
│   │   ├── processing/     # Processamento de links
│   │   │   └── cleaning.py
│   │   └── notifications/  # Notificações
│   │       └── telegram.py
│   ├── storage/            # Armazenamento de arquivos
│   ├── data/               # Dados locais (logs, CSV, DB)
│   ├── main.py             # Aplicação FastAPI principal
│   └── requirements.txt    # Dependências Python
│
├── frontend/               # Frontend Next.js
│   ├── app/                # App Router do Next.js
│   │   ├── login/          # Página de login
│   │   ├── register/       # Página de registro
│   │   ├── dashboard/      # Dashboard principal
│   │   ├── pages-manager/  # Gerenciamento de páginas
│   │   ├── scraper/        # Controle do scraper
│   │   └── telegram/       # Configuração Telegram
│   ├── components/         # Componentes React reutilizáveis
│   ├── lib/                # Utilitários
│   │   ├── api.ts          # Cliente API
│   │   └── auth.ts         # Funções de autenticação
│   ├── middleware.ts       # Middleware de proteção de rotas
│   └── package.json        # Dependências Node.js
│
├── src/                    # Código legado (mantido para compatibilidade)
│   ├── collectors/
│   ├── processing/
│   ├── storage/
│   └── notifications/
│
├── dashboard/              # Dashboard Streamlit legado (opcional)
│
├── start-backend.bat       # Script Windows para iniciar backend
├── start-frontend.bat      # Script Windows para iniciar frontend
├── start-backend.ps1       # Script PowerShell para backend
├── start-frontend.ps1      # Script PowerShell para frontend
└── README.md               # Este arquivo
```

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.11+**
- **Node.js 18+** e npm
- **Git** (para clonar o repositório)

### Passo a Passo

#### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/whatsapp-coletor-links.git
cd whatsapp-coletor-links
```

#### 2. Configurar Backend

```bash
# Navegue para o diretório backend
cd backend

# Crie um ambiente virtual (Windows)
python -m venv venv

# Ative o ambiente virtual (Windows)
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

#### 3. Configurar Frontend

```bash
# Volte para a raiz do projeto
cd ..

# Navegue para o diretório frontend
cd frontend

# Instale as dependências
npm install
```

#### 4. Configurar Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto para configurações:

```env
# JWT Secret (gerar uma chave segura em produção)
JWT_SECRET_KEY=your-secret-key-minimum-32-characters

# Telegram (opcional)
TELEGRAM_BOT_TOKEN=seu_token_do_bot
TELEGRAM_CHAT_ID=seu_chat_id

# API URL (opcional, padrão: http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🎮 Como Usar

### Iniciar o Backend

**Windows (PowerShell):**
```powershell
.\start-backend.ps1
```

**Windows (CMD):**
```cmd
start-backend.bat
```

**Manual:**
```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: `http://localhost:8000`

### Iniciar o Frontend

**Windows (PowerShell):**
```powershell
.\start-frontend.ps1
```

**Windows (CMD):**
```cmd
start-frontend.bat
```

**Manual:**
```bash
cd frontend
npm run dev
```

O frontend estará disponível em: `http://localhost:3000`

### Primeiro Acesso

1. Acesse `http://localhost:3000`
2. Você será redirecionado para `/login`
3. Clique em "Criar conta" para registrar um novo usuário
4. Após o registro, você será automaticamente logado
5. Acesse o dashboard para começar a usar o sistema

---

## 📡 Endpoints da API

### Autenticação (Públicas)

- `POST /auth/register` - Registro de novo usuário
  ```json
  {
    "email": "usuario@example.com",
    "password": "senha123",
    "name": "Nome do Usuário" // opcional
  }
  ```

- `POST /auth/login` - Login de usuário
  ```json
  {
    "email": "usuario@example.com",
    "password": "senha123"
  }
  ```

- `GET /auth/me` - Obter usuário atual (requer token)

### API de Links (Protegidas - requerem autenticação)

- `GET /api/links?limit=1000` - Listar links coletados
- `GET /api/stats` - Estatísticas gerais do sistema

### API de Páginas (Protegidas)

- `GET /api/pages` - Listar páginas monitoradas
- `POST /api/pages` - Adicionar nova página
  ```json
  {
    "url": "https://example.com/page",
    "name": "Nome da Campanha"
  }
  ```
- `DELETE /api/pages?url=...` - Remover página

### API do Scraper (Protegidas)

- `POST /api/scraper/run` - Executar coleta de links
- `GET /api/scraper/last-run` - Última execução do scraper

### API do Telegram (Protegidas)

- `GET /api/telegram/config` - Obter configuração atual
- `POST /api/telegram/save` - Salvar configuração
- `POST /api/telegram/test` - Enviar mensagem de teste

**Nota**: Todas as rotas `/api/*` requerem token JWT no header:
```
Authorization: Bearer <seu_token_jwt>
```

---

## ⚙️ Funcionalidades

### ✅ Implementadas

- **Autenticação JWT**: Login e registro seguro
- **Dashboard Interativo**: Visualização de links e estatísticas
- **Gerenciamento de Páginas**: Adicionar, editar e remover páginas monitoradas
- **Coleta Automatizada**: Executar scraper via interface web
- **Normalização de Links**: Limpeza e validação de links WhatsApp
- **Armazenamento SQLite**: Banco de dados local eficiente
- **Notificações Telegram**: Alertas quando novos links são encontrados
- **Rotas Protegidas**: Middleware de autenticação no frontend e backend

### 🔄 Em Desenvolvimento

- Multi-tenancy (isolamento de dados por usuário)
- Agendamento automático de coletas (cron jobs)
- Exportação de dados (CSV, JSON)
- Dashboard avançado com mais gráficos
- Coleta distribuída
- Suporte a mais tipos de notificações

---

## 🔒 Segurança

- **JWT Tokens**: Autenticação segura com expiração (7 dias)
- **Hashing de Senhas**: bcrypt para armazenamento seguro
- **Middleware de Proteção**: Rotas protegidas automaticamente
- **CORS Configurado**: Permite apenas origens confiáveis em produção
- **Validação de Dados**: Pydantic para validação de entrada

**⚠️ Importante para Produção:**

1. Altere o `JWT_SECRET_KEY` no arquivo `.env`
2. Configure CORS adequadamente
3. Use HTTPS em produção
4. Implemente rate limiting
5. Configure logs e monitoramento

---

## 📊 Fluxo de Dados

```
Página Web → Scraper → Normalização → Validação → 
Banco de Dados → Dashboard → Notificações (Telegram)
```

1. **Coleta**: Scraper acessa páginas cadastradas
2. **Extração**: Links WhatsApp são extraídos do HTML
3. **Processamento**: Links são normalizados e validados
4. **Armazenamento**: Links únicos são salvos no SQLite
5. **Visualização**: Dashboard exibe links coletados
6. **Notificação**: Novos links disparam alertas no Telegram

---

## 🐳 Docker (Opcional)

Em breve: Docker Compose para facilitar o deploy.

---

## 🧪 Testes

Para testar o sistema:

1. Registre um usuário
2. Faça login
3. Adicione uma página para monitorar
4. Execute o scraper
5. Visualize os links coletados no dashboard

---

## 📝 Próximos Passos

### Curto Prazo
- [ ] Adicionar testes automatizados (pytest)
- [ ] Implementar refresh token
- [ ] Melhorar tratamento de erros
- [ ] Adicionar validação de email

### Médio Prazo
- [ ] Multi-tenancy completo
- [ ] Agendamento de coletas (cron)
- [ ] API de logs estruturada
- [ ] Documentação Swagger melhorada

### Longo Prazo
- [ ] Deploy em produção (Vercel + Render)
- [ ] Integração com mais serviços de notificação
- [ ] Machine Learning para detectar padrões
- [ ] Dashboard analytics avançado

---

## 👨‍💻 Autor

Desenvolvido como projeto de portfólio para demonstrar habilidades em:
- Engenharia de Dados
- Desenvolvimento Full-Stack
- Web Scraping
- API Design

---

## 📄 Licença

Este projeto é de código aberto e está disponível para fins educacionais e de portfólio.

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

## 📞 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!**
