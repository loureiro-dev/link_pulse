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
# Inclui backend/ para permitir imports de backend.*
for p in [BACKEND_ROOT, ROOT, SRC_ROOT]:
    if p not in sys.path:
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

# Inicializa o FastAPI
app = FastAPI(
    title="LinkPulse API",
    description="API para monitoramento e coleta de links de grupos WhatsApp",
    version="1.0.0"
)

# Configura CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens para desenvolvimento
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

# Flag para controlar proteção de rotas (para migração gradual)
# Agora que o frontend está pronto, podemos proteger as rotas
PROTECTED_ROUTES = True  # Frontend já está implementado

# ============================================================================
# MODELOS PYDANTIC PARA VALIDAÇÃO DE DADOS
# ============================================================================
# Modelos movidos para backend/models.py para evitar importações circulares
# Importa modelos de arquivo separado
from backend.models import (
    LinkResponse,
    PageRequest,
    PageResponse,
    TelegramConfig,
    ScraperResponse
)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================
# Funções utilitárias para gerenciamento de páginas, configuração e logs

def load_pages():
    """Carrega as páginas cadastradas do arquivo CSV"""
    import csv
    if not os.path.exists(PAGES_FILE):
        return []
    try:
        pages = []
        with open(PAGES_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pages.append(row)
        return pages
    except Exception:
        return []

def save_pages(pages: List[dict]):
    """Salva as páginas no arquivo CSV"""
    import csv
    if not pages:
        # Se não há páginas, cria arquivo vazio com cabeçalho
        with open(PAGES_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'name'])
            writer.writeheader()
        return
    
    with open(PAGES_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'name'])
        writer.writeheader()
        writer.writerows(pages)

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

def send_telegram_message(link: str, source: str):
    """Envia notificação para o Telegram"""
    import requests
    
    config = load_config()
    token = config.get("telegram", {}).get("bot_token", "").strip()
    chat_id = config.get("telegram", {}).get("chat_id", "").strip()
    
    if not token or not chat_id:
        write_log("Telegram não configurado - pulando envio")
        return False
    
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    msg = (
        "*NOVO GRUPO ENCONTRADO!*\n\n"
        f"*Campanha:* `{source}`\n"
        f"*Link do Grupo:*\n`{link}`\n"
        f"*Data/Hora:* {timestamp}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "*Monitoramento ativo*"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        write_log(f"Telegram enviado: {link} (campanha: {source})")
        return True
    except Exception as e:
        write_log(f"Erro ao enviar Telegram: {e}")
        return False

# ============================================================================
# ENDPOINTS DA API
# ============================================================================

# Inclui routers de autenticação e API (rotas organizadas por módulos)
app.include_router(auth_router)

# Importa routers de API organizados
from backend.api.links import router as links_router
from backend.api.pages import router as pages_router
from backend.api.scraper import router as scraper_router
from backend.api.settings import router as settings_router
from backend.api.admin import router as admin_router
from backend.api.profile import router as profile_router

# Inclui routers de API (todas as rotas /api/* são protegidas com JWT)
app.include_router(links_router)
app.include_router(pages_router)
app.include_router(scraper_router)
app.include_router(settings_router)
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

# Rotas removidas - agora estão organizadas em módulos separados:
# - backend/api/links.py: GET /api/links, GET /api/stats
# - backend/api/pages.py: GET/POST/DELETE /api/pages
# - backend/api/scraper.py: POST /api/scraper/run, GET /api/scraper/last-run
# - backend/api/settings.py: GET/POST /api/telegram/config, POST /api/telegram/test

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

