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

# Adiciona caminhos ao sys.path para permitir imports flexíveis
# Isso resolve o problema de 'cd backend' no Render
for p in [BACKEND_ROOT, ROOT]:
    if p and p not in sys.path:
        sys.path.insert(0, p)

# ============================
# CONFIGURAÇÃO DE ARQUIVOS E PATHS
# ============================

DATA_DIR = os.path.join(BACKEND_ROOT, "data")  
os.makedirs(DATA_DIR, exist_ok=True)

PAGES_FILE = os.path.join(DATA_DIR, "pages.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
LAST_RUN_FILE = os.path.join(DATA_DIR, "last_run.txt")
LOGS_FILE = os.path.join(DATA_DIR, "logs.txt")

# ============================================================================
# FUNÇÕES AUXILIARES
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
    try:
        # Import flexível para evitar erros de caminho
        try:
            from backend.services.notifications.telegram import send_message
        except ImportError:
            from services.notifications.telegram import send_message
        return send_message(link, source, link_type, is_relaunch)
    except Exception as e:
        write_log(f"Erro ao enviar Telegram: {e}")
        return False

# ============================================================================
# AGENDADOR DE TAREFAS (SCHEDULER)
# ============================================================================

def run_automated_scrapers():
    """Tarefa executada pelo scheduler para coletar links"""
    write_log("🕒 [Scheduler] Iniciando coleta automática de rotina...")
    
    try:
        # Tenta disparar a coleta automática via API interna ou DB
        try:
            from backend.db.users import list_all_users
            from backend.db.pages import load_pages
            from backend.api.scraper import run_scraper_logic
        except ImportError:
            from db.users import list_all_users
            from db.pages import load_pages
            from api.scraper import run_scraper_logic
            
        users = list_all_users(include_pending=False)
        for user in users:
            pages = load_pages(user["id"])
            for page in pages:
                try:
                    run_scraper_logic(page["url"], page["name"], user["id"])
                except Exception:
                    continue
        write_log("✅ [Scheduler] Coleta automática concluída.")
    except Exception as e:
        write_log(f"🚨 [Scheduler] Erro: {e}")

# Inicializa o agendador
try:
    scheduler = BackgroundScheduler()
    br_timezone = pytz.timezone('America/Sao_Paulo')
    scheduler.add_job(
        run_automated_scrapers,
        CronTrigger(hour='8,14,20', minute='0', timezone=br_timezone),
        id='automated_collect',
        replace_existing=True
    )
    scheduler.start()
    write_log("🚀 [Scheduler] Agendador iniciado (08:00, 14:00, 20:00 BRT)")
except Exception as e:
    print(f"Erro ao iniciar agendador: {e}")
    write_log(f"Erro ao iniciar agendador: {e}")

# ============================
# INICIALIZAÇÃO FASTAPI
# ============================

app = FastAPI(title="LinkPulse API", version="1.0.0")

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Banco de dados
try:
    try:
        from backend.db.connection import init_db
    except ImportError:
        from db.connection import init_db
    init_db()
except Exception as e:
    print(f"Erro ao iniciar DB: {e}")

# ============================
# ROTAS / API
# ============================

# ============================
# ROTAS / API
# ============================

@app.get("/")
async def root():
    return {
        "status": "online", 
        "service": "LinkPulse API",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/debug-routes")
async def debug_routes():
    """Retorna todas as rotas registradas no sistema para diagnóstico."""
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods) if hasattr(route, "methods") else []
            })
    return {"total": len(routes), "routes": routes}

# Wrapper de importação robusta
def include_pulse_routers(app_instance):
    write_log("🔧 [API] Iniciando carregamento dos roteadores...")
    
    # Lista de roteadores a importar e incluir com seus respectivos prefixos
    # Formato: (nome_module, router_attr_name, prefix)
    routers_to_include = [
        ('auth.routes', 'router', '/auth'),
        ('api.links', 'router', '/api'),
        ('api.pages', 'router', '/api'),
        ('api.scraper', 'router', '/api'),
        ('api.settings', 'router', '/api'),
        ('api.settings', 'router_telegram', '/api/telegram'),
        ('api.settings', 'router_youtube', '/api/youtube'),
        ('api.settings', 'router_ai', '/api/ai'),
        ('api.discovery', 'router', '/api/discovery'),
        ('api.logs', 'router', '/api'),
        ('api.admin', 'router', '/api'),
        ('api.profile', 'router', '/api'),
    ]

    for module_name, attr_name, prefix in routers_to_include:
        try:
            # Tenta importar com prefixo backend. (contexto local)
            full_module_name = f"backend.{module_name}"
            try:
                module = __import__(full_module_name, fromlist=[attr_name])
            except ImportError:
                # Tenta importar direto (contexto render)
                module = __import__(module_name, fromlist=[attr_name])
            
            router = getattr(module, attr_name)
            app_instance.include_router(router, prefix=prefix)
            write_log(f"✅ [API] Router '{module_name}.{attr_name}' montado em '{prefix}'")
            
        except Exception as e:
            msg = f"❌ [API] ERRO ao carregar roteador {module_name}.{attr_name}: {e}"
            print(msg)
            write_log(msg)

include_pulse_routers(app)

# Webhook Telegram (Simplificado para evitar crashes)
@app.post("/api/telegram/bot-webhook")
async def telegram_bot_webhook(data: dict):
    # Lógica mínima para evitar erros de importação no webhook
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
