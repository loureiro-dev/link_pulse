# 🚀 Deploy do Backend no Render - Passo a Passo

## 1. Criar Conta no Render

1. Acesse: https://render.com
2. Clique em **"Get Started for Free"**
3. Faça login com **GitHub** (mesma conta do seu repositório)

## 2. Criar Novo Web Service

1. No dashboard, clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório GitHub:
   - Se for a primeira vez, autorize o Render a acessar seus repositórios
   - Selecione o repositório: `link_pulse` (ou o nome do seu repo)

## 3. Configurar o Serviço

Preencha os campos:

**Name:**
```
linkpulse-backend
```

**Region:**
```
Oregon (US West) - ou mais próximo de você
```

**Branch:**
```
main
```

**Root Directory:**
```
(Deixe vazio - o Render vai usar a raiz do projeto)
```

**Runtime:**
```
Python 3
```

**Build Command:**
```
pip install -r backend/requirements.txt
```

**Start Command:**
```
cd backend && gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

## 4. Configurar Variáveis de Ambiente

Na seção **"Environment Variables"**, adicione:

**Variável 1:**
- Key: `CORS_ORIGINS`
- Value: `https://seu-projeto.vercel.app` (substitua pela URL do seu frontend no Vercel)

**Variável 2:**
- Key: `FRONTEND_URL`
- Value: `https://seu-projeto.vercel.app` (mesma URL do frontend)

**Variável 3 (Opcional - para Telegram):**
- Key: `TELEGRAM_BOT_TOKEN`
- Value: (seu token do Telegram, se tiver)

**Variável 4 (Opcional - para Telegram):**
- Key: `TELEGRAM_CHAT_ID`
- Value: (seu chat ID do Telegram, se tiver)

## 5. Plano e Deploy

1. **Plan:** Selecione **"Free"** (gratuito)
2. Clique em **"Create Web Service"**
3. Aguarde o build (5-10 minutos na primeira vez)

## 6. Obter a URL do Backend

Após o deploy:
1. Você verá uma URL como: `https://linkpulse-backend.onrender.com`
2. **Copie essa URL** - você vai precisar dela!

## 7. Atualizar Frontend no Vercel

1. Vá no Vercel → Seu projeto → **Settings** → **Environment Variables**
2. Edite ou adicione:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://linkpulse-backend.onrender.com` (URL do seu backend no Render)
3. Salve
4. Vá em **Deployments** → Clique nos 3 pontinhos do último deploy → **Redeploy**

## 8. Testar

1. Acesse seu frontend no Vercel
2. Deve funcionar normalmente agora!
3. O backend pode demorar alguns segundos para "acordar" se estiver inativo (plano free)

## ⚠️ Notas Importantes

- **Plano Free do Render:** O serviço "dorme" após 15 minutos de inatividade, mas acorda automaticamente quando recebe uma requisição (pode levar 30-60 segundos)
- **Primeiro acesso:** Pode demorar mais porque o Render está iniciando o serviço
- **Banco de dados:** O SQLite será criado automaticamente no servidor do Render
- **Logs:** Você pode ver os logs em tempo real no dashboard do Render

## ✅ Pronto!

Agora seu projeto está 100% online, sem precisar da sua máquina! 🎉

