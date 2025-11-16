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

O frontend está configurado para deploy no Vercel. O backend pode ser hospedado em qualquer serviço que suporte Python (Render, Railway, etc.).

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
