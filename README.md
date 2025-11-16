# LinkPulse

Sistema de monitoramento e coleta automatizada de links de grupos WhatsApp em páginas de captura.

## Sobre

Projeto desenvolvido para automatizar a descoberta de links de grupos WhatsApp escondidos em páginas de lançamento. Muitos produtores digitais escondem esses links em HTML complexo, scripts JavaScript, iframes ou campos invisíveis. Este sistema resolve isso automatizando todo o processo.

## Stack

**Backend:**
- FastAPI
- Python 3.11+
- SQLite
- BeautifulSoup4 + Selenium

**Frontend:**
- Next.js 14
- TypeScript
- Tailwind CSS
- Recharts

## Estrutura

```
├── backend/          # API FastAPI
├── frontend/         # Next.js app
└── src/             # Módulos de coleta
```

## Setup Local

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Deploy

### Frontend (Vercel - Gratuito)

1. Conecte seu repositório no [Vercel](https://vercel.com)
2. Configure a variável de ambiente:
   - `NEXT_PUBLIC_API_URL` = URL do seu backend
3. Deploy automático a cada push

### Backend (Render/Railway - Gratuito)

**Render:**
1. Crie uma conta no [Render](https://render.com)
2. New → Web Service
3. Conecte o repositório
4. Configurações:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - Environment: Python 3
5. Adicione variável: `CORS_ORIGINS` = URL do frontend Vercel

**Railway:**
1. Crie conta no [Railway](https://railway.app)
2. New Project → Deploy from GitHub
3. Selecione o repositório
4. Configure o start command no `Procfile`

Após o deploy, ambos os serviços ficam online 24/7 sem precisar da sua máquina.

## Funcionalidades

- Coleta automatizada de links WhatsApp
- Dashboard com gráficos e estatísticas
- Gerenciamento de páginas monitoradas
- Notificações via Telegram
- Normalização e validação de links

## API

Documentação interativa disponível em `/docs` quando o backend estiver rodando.

Principais endpoints:
- `GET /api/links` - Lista links coletados
- `GET /api/stats` - Estatísticas
- `POST /api/pages` - Adiciona página
- `POST /api/scraper/run` - Executa coleta

## Notas

Este é um projeto de portfólio desenvolvido para demonstrar habilidades em web scraping, desenvolvimento full-stack e engenharia de dados.
