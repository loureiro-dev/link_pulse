"""
Backend FastAPI para LinkPulse
API REST que integra com o sistema de coleta de links existente
"""

import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

load_dotenv()

# ============================
# CONFIGURAÇÃO DE CAMINHOS DO PROJETO
# ============================

# Caminho da pasta backend/ (onde está este arquivo)
BACKEND_ROOT = os.path.dirname(__file__)

# Caminho da raiz do projeto (volta 1 nível)
ROOT = os.path.abspath(os.path.join(BACKEND_ROOT, ".."))

# Caminho da pasta src/ (código legado, mantido para compatibilidade)
SRC_ROOT = os.path.join(ROOT, "src")

# Adiciona caminhos ao sys.path para permitir imports
# Se o script está sendo rodado de dentro da pasta backend/, 
# precisamos adicionar o diretório pai ao path.
PARENT_DIR = os.path.dirname(BACKEND_ROOT)

for p in [PARENT_DIR, BACKEND_ROOT, ROOT, SRC_ROOT]:
    if p and p not in sys.path:
        sys.path.insert(0, p)

# ============================
# IMPORTS DOS MÓDULOS DO PROJETO
# ============================

# Importa funções de banco de dados do novo local
from backend.db.connection import save_links, list_links, init_db
# Importa serviços do novo local (coleta, processamento)
from backend.services.collectors.requests_collector import collect_from_page
from backend.services.processing.cleaning import normalize_whatsapp_link, is_group_link

# ============================
# CONFIGURAÇÃO DE ARQUIVOS E PATHS
# ============================

DATA_DIR = os.path.join(ROOT, "backend", "data")  
os.makedirs(DATA_DIR, exist_ok=True)

PAGES_FILE = os.path.join(DATA_DIR, "pages.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
LAST_RUN_FILE = os.path.join(DATA_DIR, "last_run.txt")
LOGS_FILE = os.path.join(DATA_DIR, "logs.txt")

# ============================================================================
# FUNÇÕES AUXILIARES (DEFINIDAS ANTES DO SCHEDULER)
# ============================================================================

def load_config():
    """Carrega a configuração do Telegram do arquivo JSON"""
    if not os.path.exists(CONFIG_FILE):
        return {"telegram": {"bot_token": "", "chat_id": ""}}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"telegram": {"bot_token": "", "chat_id": ""}}

def save_config(config: dict):
    """Salva a configuração no arquivo JSON"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar config: {e}")
        return False

def write_log(message: str):
    """Escreve uma mensagem no arquivo de logs"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOGS_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

def send_telegram_message(link: str, source: str, link_type: str = "group", is_relaunch: bool = False):
    """Envia notificação para o Telegram usando o serviço especializado"""
    from backend.services.notifications.telegram import send_message
    return send_message(link, source, link_type, is_relaunch)

# ============================================================================
# AGENDADOR DE TAREFAS (SCHEDULER)
# ============================================================================

def run_automated_scrapers():
    """
    Tarefa executada pelo scheduler para coletar links de todas as páginas 
    de todos os usuários.
    """
    write_log("🕒 [Scheduler] Iniciando coleta automática de rotina...")
    
    from backend.db.users import list_all_users
    from backend.db.pages import load_pages
    from backend.api.scraper import run_scraper_logic
    
    try:
        # Pega todos os usuários aprovados
        users = list_all_users(include_pending=False)
        total_pages = 0
        total_links = 0
        
        for user in users:
            user_id = user["id"]
            pages = load_pages(user_id)
            for page in pages:
                total_pages += 1
                try:
                    # Executa a lógica de coleta para a página
                    # O run_scraper_logic já salva no banco e envia pro Telegram
                    result = run_scraper_logic(page["url"], page["name"], user_id)
                    total_links += result.get("links_found", 0)
                except Exception as e:
                    write_log(f"❌ [Scheduler] Erro na página {page['name']}: {e}")
                    
        write_log(f"✅ [Scheduler] Finalizado: {total_pages} página(s) processada(s), {total_links} links novos.")
        
    except Exception as e:
        write_log(f"🚨 [Scheduler] Erro crítico no ciclo automático: {e}")

# Inicializa o agendador
scheduler = BackgroundScheduler()
# Define o fuso horário de Brasília
br_timezone = pytz.timezone('America/Sao_Paulo')

# Agenda as coletas (08h, 14h, 20h)
scheduler.add_job(
    run_automated_scrapers,
    CronTrigger(hour='8,14,20', minute='0', timezone=br_timezone),
    id='automated_collect',
    replace_existing=True
)

# Inicia o scheduler
scheduler.start()
write_log("🚀 [Scheduler] Agendador iniciado (Jobs: 08:00, 14:00, 20:00 BRT)")

# Inicializa o FastAPI
app = FastAPI(
    title="LinkPulse API",
    description="API para monitoramento e coleta de links de grupos WhatsApp",
    version="1.0.0"
)

# Configura CORS para permitir requisições do frontend
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
extra_origins = ["https://link-pulse-tau.vercel.app"]
for origin in extra_origins:
    if origin not in cors_origins:
        cors_origins.append(origin)

if cors_origins == ["*"] and os.getenv("FRONTEND_URL"):
    cors_origins = [os.getenv("FRONTEND_URL")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o banco de dados (cria tabelas se não existirem)
init_db()

# Importa router de autenticação (login, registro)
from backend.auth.routes import router as auth_router
# Importa middleware de autenticação para proteger rotas
from backend.auth.middleware import get_current_user

# Importa modelos de arquivo separado
from backend.models import (
    LinkResponse,
    PageRequest,
    PageResponse,
    TelegramConfig,
    ScraperResponse
)

# ============================================================================
# ENDPOINTS DA API
# ============================================================================

# Inclui routers de autenticação e API
app.include_router(auth_router)

# Importa routers de API organizados
from backend.api.links import router as links_router
from backend.api.pages import router as pages_router
from backend.api.scraper import router as scraper_router
from backend.api.settings import router as settings_router, router_telegram, router_youtube, router_ai
from backend.api.discovery import router as discovery_router
from backend.api.logs import router as logs_router
from backend.api.admin import router as admin_router
from backend.api.profile import router as profile_router

# Inclui routers de API
app.include_router(links_router)
app.include_router(pages_router)
app.include_router(scraper_router)
app.include_router(settings_router)
app.include_router(router_telegram)
app.include_router(router_youtube)
app.include_router(router_ai)
app.include_router(discovery_router)
app.include_router(logs_router)
app.include_router(admin_router)
app.include_router(profile_router)

@app.get("/")
async def root():
    """Endpoint raiz - informações da API"""
    return {
        "name": "LinkPulse API",
        "version": "1.0.0",
        "status": "running",
        "authentication": "enabled"
    }

# ─── WEBHOOK DO BOT TELEGRAM ──────────────────────────────────────────────────
from fastapi import Request as FastAPIRequest

@app.post("/api/telegram/bot-webhook")
async def telegram_bot_webhook(req: FastAPIRequest):
    import re
    try:
        body = await req.json()
    except Exception:
        return {"ok": True}

    message = body.get("message") or body.get("channel_post") or {}
    text = message.get("text", "").strip()
    chat_id = message.get("chat", {}).get("id")
    from_user = message.get("from", {}).get("first_name", "você")

    if not text:
        return {"ok": True}

    urls = re.findall(r"https?://[^\s]+", text)
    if not urls:
        return {"ok": True}

    try:
        from backend.services.discovery.quick_collect import collect_url_now
        config = load_config()
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() or config.get("telegram", {}).get("bot_token", "").strip()

        total_links = 0
        for url in urls:
            result = collect_url_now(
                url=url,
                user_id=1,
                source_name=f"Bot Telegram — {from_user}",
                add_to_pages=True,
                send_telegram=False,
            )
            total_links += result.get("links_found", 0)

        if token and chat_id:
            if total_links > 0:
                reply = f"✅ *{total_links} grupo(s) WhatsApp* encontrado(s) e salvos!\n\nURL(s) adicionadas ao monitoramento."
            else:
                reply = f"🔍 URL recebida e adicionada ao monitoramento.\nNenhum grupo encontrado por enquanto."

            import requests as _req
            _req.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"},
                timeout=8,
            )
    except Exception as e:
        write_log(f"Erro no webhook Telegram: {e}")

    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
