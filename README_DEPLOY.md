# 🚀 Guia de Deploy - LinkPulse

Guia completo para fazer deploy do LinkPulse em produção usando **Vercel** (frontend) e **Render** (backend).

---

## 📋 Pré-requisitos

- Conta no [Vercel](https://vercel.com) (gratuita)
- Conta no [Render](https://render.com) (gratuita)
- Repositório no GitHub (recomendado)
- Python 3.11+ instalado localmente (para testes)

---

## 🎯 Visão Geral do Deploy

- **Frontend (Next.js)**: Deploy na Vercel
- **Backend (FastAPI)**: Deploy no Render
- **Banco de Dados**: SQLite (arquivo local no Render)

---

## 🔧 Passo 1: Preparar o Backend no Render

### 1.1. Criar Novo Web Service no Render

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Selecione o repositório do LinkPulse

### 1.2. Configurar o Serviço

**Configurações básicas:**
- **Name**: `linkpulse-backend` (ou o nome que preferir)
- **Region**: Escolha a região mais próxima (ex: `Oregon (US West)`)
- **Branch**: `main` (ou sua branch principal)
- **Root Directory**: Deixe vazio (ou `backend` se quiser)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

**OU use o Procfile (recomendado):**
- Deixe **Build Command** e **Start Command** vazios
- O Render usará automaticamente o `Procfile` na raiz

### 1.3. Variáveis de Ambiente (Backend)

No Render, vá em **"Environment"** e adicione:

```
JWT_SECRET_KEY=sua-chave-secreta-aqui-minimo-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=4320
CORS_ORIGINS=https://seu-frontend.vercel.app
FRONTEND_URL=https://seu-frontend.vercel.app
```

**Importante:**
- `JWT_SECRET_KEY`: Gere uma chave segura com `openssl rand -hex 32`
- `CORS_ORIGINS`: URL do seu frontend na Vercel (será preenchida depois)
- `FRONTEND_URL`: URL do seu frontend na Vercel (será preenchida depois)

### 1.4. Deploy do Backend

1. Clique em **"Create Web Service"**
2. Aguarde o build e deploy (pode levar 5-10 minutos)
3. Anote a URL gerada (ex: `https://linkpulse-backend.onrender.com`)

**⚠️ Importante:**
- O primeiro deploy pode ser lento
- Serviços gratuitos do Render "dormem" após 15 minutos de inatividade
- O primeiro acesso após dormir pode levar 30-60 segundos

---

## 🎨 Passo 2: Preparar o Frontend na Vercel

### 2.1. Criar Novo Projeto na Vercel

1. Acesse [Vercel Dashboard](https://vercel.com/dashboard)
2. Clique em **"Add New..."** → **"Project"**
3. Importe seu repositório do GitHub
4. Selecione o repositório do LinkPulse

### 2.2. Configurar o Projeto

**Configurações:**
- **Framework Preset**: Next.js (detectado automaticamente)
- **Root Directory**: `frontend`
- **Build Command**: `npm run build` (padrão)
- **Output Directory**: `.next` (padrão)
- **Install Command**: `npm install` (padrão)

### 2.3. Variáveis de Ambiente (Frontend)

Na Vercel, vá em **"Environment Variables"** e adicione:

```
NEXT_PUBLIC_API_URL=https://seu-backend.onrender.com
```

**Importante:**
- Substitua `seu-backend.onrender.com` pela URL real do seu backend no Render
- Variáveis que começam com `NEXT_PUBLIC_` são expostas ao cliente

### 2.4. Deploy do Frontend

1. Clique em **"Deploy"**
2. Aguarde o build (geralmente 2-5 minutos)
3. Anote a URL gerada (ex: `https://linkpulse.vercel.app`)

---

## 🔄 Passo 3: Conectar Frontend e Backend

### 3.1. Atualizar CORS no Backend

Após o deploy do frontend, volte ao Render e atualize as variáveis de ambiente:

```
CORS_ORIGINS=https://seu-frontend.vercel.app
FRONTEND_URL=https://seu-frontend.vercel.app
```

Depois, faça um **redeploy** do backend no Render.

### 3.2. Verificar Conexão

1. Acesse a URL do frontend na Vercel
2. Tente fazer login
3. Se houver erro de CORS, verifique se as URLs estão corretas

---

## 🗄️ Passo 4: Banco de Dados (SQLite)

**⚠️ Importante sobre SQLite no Render:**

- O SQLite funciona, mas **dados são perdidos** quando o serviço é reiniciado
- Para produção real, considere migrar para PostgreSQL (Render oferece gratuito)
- Por enquanto, o SQLite é suficiente para testes e demonstração

**Localização do banco:**
- O banco será criado em `backend/data/whatsapp_links.db` no servidor Render
- Dados persistem enquanto o serviço estiver ativo

---

## 🔐 Passo 5: Criar Usuário Admin

Após o deploy, você precisará criar um usuário admin. Opções:

### Opção 1: Via API (Recomendado)

1. Faça registro normal pela interface
2. Acesse o banco de dados no Render (via SSH ou script)
3. Execute SQL para tornar o usuário admin:

```sql
UPDATE users SET is_admin = 1, approved = 1 WHERE email = 'seu@email.com';
```

### Opção 2: Script Python

Crie um script temporário no Render para criar admin:

```python
# backend/create_admin_deploy.py
from backend.db.users import create_user
create_user("admin@linkpulse.com", "senha_segura", "Admin", is_admin=True, approved=True)
```

---

## ✅ Checklist de Deploy

### Backend (Render)
- [ ] Repositório conectado
- [ ] Build Command configurado
- [ ] Start Command configurado (ou Procfile)
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado com sucesso
- [ ] URL do backend anotada

### Frontend (Vercel)
- [ ] Repositório conectado
- [ ] Root Directory: `frontend`
- [ ] Variável `NEXT_PUBLIC_API_URL` configurada
- [ ] Deploy realizado com sucesso
- [ ] URL do frontend anotada

### Integração
- [ ] CORS atualizado no backend com URL do frontend
- [ ] Backend redeployado após atualizar CORS
- [ ] Frontend consegue se conectar ao backend
- [ ] Login funcionando
- [ ] Usuário admin criado

---

## 🧪 Testes Pós-Deploy

1. **Teste de Login:**
   - Acesse a URL do frontend
   - Tente fazer login
   - Verifique se não há erros de CORS

2. **Teste de API:**
   - Acesse `https://seu-backend.onrender.com/docs`
   - Deve aparecer a documentação Swagger do FastAPI
   - Teste um endpoint simples (ex: `GET /`)

3. **Teste de Funcionalidades:**
   - Criar conta
   - Fazer login
   - Acessar dashboard
   - Adicionar página para monitorar
   - Executar scraper

---

## 🐛 Solução de Problemas

### Erro de CORS

**Sintoma:** `Access to fetch blocked by CORS policy`

**Solução:**
1. Verifique se `CORS_ORIGINS` e `FRONTEND_URL` estão corretos no Render
2. Certifique-se de que a URL do frontend está sem barra no final
3. Faça redeploy do backend após atualizar variáveis

### Backend não inicia

**Sintoma:** Deploy falha ou serviço não responde

**Solução:**
1. Verifique os logs no Render
2. Certifique-se de que `requirements.txt` está completo
3. Verifique se o `Procfile` está correto
4. Teste localmente: `cd backend && uvicorn main:app --port 8000`

### Frontend não encontra API

**Sintoma:** Erro 404 ou "Failed to fetch"

**Solução:**
1. Verifique se `NEXT_PUBLIC_API_URL` está configurada na Vercel
2. Certifique-se de que a URL do backend está correta (com `https://`)
3. Verifique se o backend está rodando (acesse `/docs`)

### Banco de dados vazio após reiniciar

**Sintoma:** Dados sumiram após reiniciar o serviço

**Explicação:** Isso é normal com SQLite no Render (serviços gratuitos). Para produção, migre para PostgreSQL.

---

## 📚 Links Úteis

- [Documentação Render](https://render.com/docs)
- [Documentação Vercel](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

---

## 🎉 Próximos Passos

Após o deploy bem-sucedido:

1. **Migrar para PostgreSQL** (opcional, mas recomendado)
2. **Configurar domínio customizado** (Vercel e Render oferecem)
3. **Configurar CI/CD** (deploy automático ao fazer push)
4. **Adicionar monitoramento** (logs, métricas)
5. **Configurar backup** do banco de dados

---

## 📝 Notas Importantes

- **Serviços gratuitos têm limitações:**
  - Render: Serviços "dormem" após 15 min de inatividade
  - Vercel: Limite de bandwidth e builds
  - SQLite: Dados podem ser perdidos em reinicializações

- **Para produção real:**
  - Use planos pagos ou considere outras plataformas
  - Migre para PostgreSQL
  - Configure backups automáticos
  - Use CDN para assets estáticos

---

**Boa sorte com o deploy! 🚀**

