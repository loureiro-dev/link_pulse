# 📖 Instruções de Uso - LinkPulse

Guia completo de uso do sistema LinkPulse para monitoramento e coleta de links WhatsApp.

---

## 📋 Índice

1. [Primeiros Passos](#primeiros-passos)
2. [Instalação](#instalação)
3. [Iniciar o Sistema](#iniciar-o-sistema)
4. [Primeiro Acesso](#primeiro-acesso)
5. [Usando o Sistema](#usando-o-sistema)
6. [Configurar Telegram (Opcional)](#configurar-telegram-opcional)
7. [Solução de Problemas](#solução-de-problemas)
8. [Dicas e Boas Práticas](#dicas-e-boas-práticas)

---

## 🚀 Primeiros Passos

### Requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.11+** ([Download aqui](https://www.python.org/downloads/))
- **Node.js 18+** e npm ([Download aqui](https://nodejs.org/))
- **Git** (opcional, para clonar o repositório)

---

## 📦 Instalação

### 1. Baixar o Projeto

Se você já tem o projeto baixado, pule para a próxima etapa.

Se não, clone ou baixe o repositório do GitHub.

### 2. Configurar Backend

Abra o terminal/PowerShell e navegue até a pasta do projeto:

```bash
cd caminho/para/whatsapp-coletor-links
```

#### 2.1. Criar Ambiente Virtual (Recomendado)

**Windows:**
```bash
cd backend
python -m venv venv
```

#### 2.2. Ativar Ambiente Virtual

**Windows (CMD):**
```bash
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

Se você receber um erro de política de execução no PowerShell, execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2.3. Instalar Dependências do Backend

```bash
pip install -r requirements.txt
```

Isso instalará todas as bibliotecas necessárias:
- FastAPI
- Uvicorn
- BeautifulSoup4
- Requests
- Python-JOSE (para JWT)
- Passlib (para hash de senhas)
- E outras...

### 3. Configurar Frontend

Abra **outro terminal** (deixe o backend em execução no primeiro) e navegue para a pasta frontend:

```bash
cd frontend
```

#### 3.1. Instalar Dependências do Frontend

```bash
npm install
```

Isso instalará todas as dependências do Next.js e React.

---

## 🎮 Iniciar o Sistema

### Opção 1: Usando Scripts Automáticos (Recomendado)

**Windows - Usando arquivos .bat:**

1. **Backend:** Clique duas vezes em `start-backend.bat`
2. **Frontend:** Clique duas vezes em `start-frontend.bat`

**Windows - Usando PowerShell:**

1. Abra PowerShell na raiz do projeto
2. Execute: `.\start-backend.ps1` (em um terminal)
3. Execute: `.\start-frontend.ps1` (em outro terminal)

### Opção 2: Manual

#### Iniciar Backend

```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará rodando em: `http://localhost:8000`

#### Iniciar Frontend

```bash
cd frontend
npm run dev
```

O frontend estará rodando em: `http://localhost:3000`

---

## 🔐 Primeiro Acesso

### 1. Acessar o Sistema

Abra seu navegador e acesse: `http://localhost:3000`

### 2. Criar Conta

Você será redirecionado para a página de login. Como ainda não tem conta:

1. Clique em **"Criar conta nova"** ou acesse: `http://localhost:3000/register`
2. Preencha os dados:
   - **Nome** (opcional)
   - **Email** (obrigatório)
   - **Senha** (obrigatório, mínimo 6 caracteres)
3. Clique em **"Criar conta"**

### 3. Login Automático

Após criar a conta, você será automaticamente logado e redirecionado para o dashboard.

---

## 💼 Usando o Sistema

### Dashboard Principal

O dashboard mostra:
- **Estatísticas gerais**: Total de links, links únicos, campanhas, páginas monitoradas
- **Gráficos**: Evolução de links ao longo do tempo
- **Tabela de links**: Links coletados recentemente

### Adicionar Páginas para Monitorar

1. Vá para a página **"Gerenciar Páginas"** (no menu lateral)
2. Clique em **"Adicionar Página"**
3. Preencha:
   - **URL da página**: Ex: `https://exemplo.com/captura`
   - **Nome da campanha**: Ex: `Campanha Black Friday`
4. Clique em **"Adicionar"**

**Dica:** Você pode adicionar quantas páginas quiser para monitorar simultaneamente.

### Executar Coleta de Links

1. Vá para a página **"Scraper"** (no menu lateral)
2. Clique no botão **"Executar Coleta"**
3. Aguarde o processo finalizar (pode levar alguns minutos dependendo do número de páginas)
4. Os resultados aparecerão em tempo real:
   - Quantas páginas foram verificadas
   - Quantos links foram encontrados
   - Lista dos links encontrados

### Visualizar Links Coletados

1. Vá para o **"Dashboard"**
2. Role até a seção **"Links Coletados Recentes"**
3. Você verá uma tabela com:
   - **URL do link**
   - **Fonte/Campanha** (de qual página veio)
   - **Data de descoberta**

**Dica:** Use os filtros para buscar links específicos por campanha ou data.

---

## 📱 Configurar Telegram (Opcional)

Para receber notificações no Telegram quando novos links forem encontrados:

### 1. Criar Bot no Telegram

1. Abra o Telegram e procure por **@BotFather**
2. Envie o comando: `/newbot`
3. Siga as instruções e crie um nome para seu bot
4. **Guarde o token** que o BotFather fornecer (ex: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Obter Chat ID

1. Procure seu bot no Telegram (o nome que você criou)
2. Envie qualquer mensagem para ele
3. Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
   - Substitua `<SEU_TOKEN>` pelo token do seu bot
4. Procure por `"chat":{"id":` no resultado
5. **Copie o número** que aparece após `"id":` (ex: `123456789`)

### 3. Configurar no Sistema

1. Vá para a página **"Configuração Telegram"** (no menu lateral)
2. Cole o **Bot Token** e o **Chat ID**
3. Clique em **"Salvar Configuração"**
4. Teste enviando uma mensagem de teste (clique em **"Enviar Teste"**)

### 4. Pronto!

Agora, sempre que novos links forem encontrados, você receberá uma notificação no Telegram automaticamente.

---

## 🔧 Solução de Problemas

### Backend não inicia

**Problema:** Erro ao iniciar o backend

**Soluções:**
1. Verifique se o ambiente virtual está ativado: `venv\Scripts\activate`
2. Verifique se todas as dependências estão instaladas: `pip install -r requirements.txt`
3. Verifique se a porta 8000 está livre (feche outros programas usando essa porta)
4. Tente usar outra porta: `uvicorn main:app --port 8001`

### Frontend não inicia

**Problema:** Erro ao iniciar o frontend

**Soluções:**
1. Verifique se o Node.js está instalado: `node --version`
2. Delete a pasta `node_modules` e reinstale: 
   ```bash
   rm -rf node_modules
   npm install
   ```
3. Verifique se a porta 3000 está livre

### Erro de conexão entre frontend e backend

**Problema:** Frontend não consegue conectar ao backend

**Soluções:**
1. Verifique se o backend está rodando: Acesse `http://localhost:8000` no navegador
2. Verifique se ambos estão nas portas corretas:
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:3000`
3. Verifique o console do navegador (F12) para ver erros específicos

### Erro de autenticação

**Problema:** Não consigo fazer login ou sou redirecionado

**Soluções:**
1. Limpe os cookies do navegador para o site `localhost:3000`
2. Tente criar uma nova conta
3. Verifique se o backend está rodando corretamente

### Páginas não são coletadas

**Problema:** O scraper não encontra links

**Soluções:**
1. Verifique se a URL está correta e acessível
2. Algumas páginas podem ter proteção contra scraping
3. Verifique os logs em `backend/data/logs.txt`
4. Tente com outra página de teste

### Telegram não envia mensagens

**Problema:** Notificações não chegam no Telegram

**Soluções:**
1. Verifique se o Bot Token está correto
2. Verifique se o Chat ID está correto
3. Certifique-se de ter enviado uma mensagem para o bot antes de pegar o Chat ID
4. Teste a configuração usando o botão "Enviar Teste"

---

## 💡 Dicas e Boas Práticas

### Organização de Campanhas

- Use nomes descritivos para suas campanhas (ex: "Black Friday 2024", "Lançamento Produto X")
- Agrupe páginas relacionadas com o mesmo nome de campanha para facilitar análise

### Frequência de Coleta

- Execute coletas periodicamente (ex: 1x por dia ou 1x por semana)
- Muitas coletas podem sobrecarregar as páginas monitoradas
- Use o histórico para ver quando novos links foram encontrados

### Segurança

- **Nunca compartilhe** seu token JWT ou senha
- Use senhas fortes para sua conta
- Em produção, altere o `JWT_SECRET_KEY` no arquivo `.env`

### Performance

- O sistema armazena apenas links únicos (evita duplicatas)
- Links antigos são mantidos no banco para histórico
- Use filtros para visualizar apenas dados recentes

### Backup

- Faça backup periódico da pasta `backend/data/`
- Isso preserva:
  - Banco de dados (`whatsapp_links.db`)
  - Páginas cadastradas (`pages.csv`)
  - Configurações (`config.json`)
  - Logs (`logs.txt`)

---

## 📞 Suporte

Se você encontrar problemas que não estão listados aqui:

1. Verifique os logs em `backend/data/logs.txt`
2. Verifique o console do navegador (F12 → Console)
3. Verifique o terminal onde o backend está rodando
4. Abra uma issue no repositório do GitHub

---

## 🎓 Próximos Passos

Depois de dominar o básico:

- Explore a **API REST** em `http://localhost:8000/docs`
- Personalize o dashboard conforme suas necessidades
- Configure notificações automáticas
- Exporte dados para análise externa

---

**✨ Boa sorte com seu monitoramento! ✨**


