# 🚀 LinkPulse - Guia de Instalação e Uso

## 📋 Pré-requisitos

- **Python 3.11+** instalado
- **Node.js 18+** e **npm** instalados
- **Git** (opcional, para clonar o repositório)

## 🔧 Instalação

### 1. Backend (FastAPI)

```powershell
# Navegue até a pasta backend
cd backend

# Crie um ambiente virtual (se ainda não existir)
python -m venv venv

# Ative o ambiente virtual
.\venv\Scripts\Activate.ps1

# Instale as dependências
pip install -r ../requirements.txt
```

**Nota:** Se o arquivo `requirements.txt` não existir na raiz, você pode instalar manualmente:
```powershell
pip install fastapi uvicorn python-multipart requests beautifulsoup4
```

### 2. Frontend (Next.js)

```powershell
# Navegue até a pasta frontend
cd frontend

# Instale as dependências
npm install
```

## 🚀 Como Executar

### Opção 1: Scripts Automáticos (Recomendado)

#### Windows PowerShell:
```powershell
# Iniciar apenas o backend
.\start-backend.ps1

# Iniciar apenas o frontend
.\start-frontend.ps1

# Iniciar ambos simultaneamente
.\start-all.ps1
```

#### Windows CMD:
```cmd
# Iniciar apenas o backend
start-backend.bat

# Iniciar apenas o frontend
start-frontend.bat
```

### Opção 2: Manual

#### Backend:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend:
```powershell
cd frontend
npm run dev
```

## 🌐 Acessar a Aplicação

- **Backend API:** http://localhost:8000
- **Frontend Dashboard:** http://localhost:3000
- **Documentação da API:** http://localhost:8000/docs

## 📖 Como Usar

### 1. Adicionar Páginas para Monitoramento

1. Acesse o dashboard em http://localhost:3000
2. Na seção "Páginas Monitoradas", clique em "+ Adicionar Página"
3. Preencha:
   - **URL da Página:** Link da landing page que contém os grupos WhatsApp
   - **Nome da Campanha:** Nome identificador da campanha
4. Clique em "Adicionar"

### 2. Executar o Scraper

1. No dashboard, localize a seção "Controle do Scraper"
2. Clique em "🚀 Executar Scraper Agora"
3. Aguarde a execução (pode levar alguns minutos)
4. Os resultados aparecerão automaticamente na tabela de links

### 3. Configurar Notificações Telegram (Opcional)

1. Crie um bot no Telegram através do [@BotFather](https://t.me/botfather)
2. Obtenha o **Bot Token**
3. Obtenha o **Chat ID** (pode usar [@userinfobot](https://t.me/userinfobot))
4. No dashboard, vá até "Configuração do Telegram"
5. Preencha os campos e clique em "Salvar Configuração"
6. Teste com o botão "Testar Notificação"

### 4. Visualizar Links Coletados

- Todos os links coletados aparecem na tabela "Links Coletados"
- Você pode copiar links clicando no botão "Copiar"
- Os links são organizados por campanha e data de descoberta

## 🛠️ Estrutura do Projeto

```
whatsapp-coletor-links/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── data/                # Dados (CSV, logs, config)
│   └── venv/                # Ambiente virtual Python
├── frontend/
│   ├── app/                 # Páginas Next.js
│   ├── components/          # Componentes React
│   ├── lib/                 # Serviços e utilitários
│   └── node_modules/        # Dependências Node.js
├── src/                     # Código fonte do coletor
│   ├── collectors/          # Módulos de coleta
│   ├── processing/          # Processamento de links
│   └── storage/             # Banco de dados
├── start-backend.ps1        # Script para iniciar backend
├── start-frontend.ps1       # Script para iniciar frontend
└── start-all.ps1            # Script para iniciar ambos
```

## 🔍 Endpoints da API

### Links
- `GET /api/links` - Lista todos os links coletados
- `GET /api/stats` - Estatísticas gerais

### Páginas
- `GET /api/pages` - Lista páginas monitoradas
- `POST /api/pages` - Adiciona uma nova página
- `DELETE /api/pages?url=...` - Remove uma página

### Scraper
- `POST /api/scraper/run` - Executa o scraper
- `GET /api/scraper/last-run` - Última execução

### Telegram
- `GET /api/telegram/config` - Configuração atual
- `POST /api/telegram/save` - Salva configuração
- `POST /api/telegram/test` - Testa notificação

## 🐛 Solução de Problemas

### Backend não inicia
- Verifique se o ambiente virtual está ativado
- Verifique se todas as dependências estão instaladas
- Certifique-se de que a porta 8000 está livre

### Frontend não inicia
- Execute `npm install` novamente
- Verifique se a porta 3000 está livre
- Limpe o cache: `rm -rf .next` (Linux/Mac) ou `rmdir /s .next` (Windows)

### Erro de CORS
- Certifique-se de que o backend está rodando na porta 8000
- Verifique se o CORS está configurado corretamente no `main.py`

### Links não aparecem
- Verifique se há páginas cadastradas
- Execute o scraper manualmente
- Verifique os logs em `backend/data/logs.txt`

## 📝 Notas Importantes

- O backend precisa estar rodando para o frontend funcionar
- Os dados são salvos localmente em `backend/data/`
- O banco de dados SQLite é criado automaticamente
- As configurações do Telegram são salvas em `backend/data/config.json`

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs em `backend/data/logs.txt`
2. Verifique o console do navegador (F12)
3. Verifique a documentação da API em http://localhost:8000/docs

---

**Desenvolvido com ❤️ para automatizar a coleta de links WhatsApp**

