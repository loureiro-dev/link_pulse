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
# AJUSTE DO ROOT CORRETO
# ============================

# Caminho da pasta backend/
BACKEND_ROOT = os.path.dirname(__file__)

# Caminho da raiz do projeto (volta 1 nível)
ROOT = os.path.abspath(os.path.join(BACKEND_ROOT, ".."))

# Caminho da pasta src/
SRC_ROOT = os.path.join(ROOT, "src")

# Adiciona caminhos ao sys.path
# Inclui backend/ para permitir imports de backend.*
for p in [BACKEND_ROOT, ROOT, SRC_ROOT]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ============================
# IMPORTS DOS MÓDULOS DO PROJETO
# ============================

# Import database functions from new location
from backend.db.connection import save_links, list_links, init_db
# Import services from new location
from backend.services.collectors.requests_collector import collect_from_page
from backend.services.processing.cleaning import normalize_whatsapp_link, is_group_link

# ============================
# CONFIGURAÇÃO DE PATHS
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

# Inicializa o banco de dados
init_db()

# Importa router de autenticação
from backend.auth.routes import router as auth_router
# Importa middleware de autenticação para proteger rotas
from backend.auth.middleware import get_current_user

# Flag para controlar proteção de rotas (para migração gradual)
# Agora que o frontend está pronto, podemos proteger as rotas
PROTECTED_ROUTES = True  # Frontend já está implementado

# ============================================================================
# Modelos Pydantic para validação de dados
# ============================================================================

class LinkResponse(BaseModel):
    """Modelo de resposta para um link coletado"""
    url: str
    source: str
    found_at: str

class PageRequest(BaseModel):
    """Modelo de requisição para criar/atualizar uma página"""
    url: str
    name: str

class PageResponse(BaseModel):
    """Modelo de resposta para uma página cadastrada"""
    url: str
    name: str

class TelegramConfig(BaseModel):
    """Modelo para configuração do Telegram"""
    bot_token: str
    chat_id: str

class ScraperResponse(BaseModel):
    """Modelo de resposta da execução do scraper"""
    success: bool
    total_checked: int
    links_found: int
    links: List[dict]
    message: str

# ============================================================================
# Funções auxiliares
# ============================================================================

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
# Endpoints da API
# ============================================================================

# Inclui router de autenticação
app.include_router(auth_router)

@app.get("/")
async def root():
    """Endpoint raiz - informações da API"""
    return {
        "name": "LinkPulse API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/links", response_model=List[LinkResponse])
async def get_links(limit: int = 1000, current_user: dict = Depends(get_current_user)):
    """
    Retorna a lista de links coletados
    Parâmetro limit controla quantos links retornar (padrão: 1000)
    """
    try:
        rows = list_links(limit)
        links = [
            LinkResponse(url=row[0], source=row[1], found_at=row[2])
            for row in rows
        ]
        return links
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar links: {str(e)}")

@app.get("/api/pages", response_model=List[PageResponse])
async def get_pages(current_user: dict = Depends(get_current_user)):
    """Retorna todas as páginas cadastradas para monitoramento"""
    try:
        pages = load_pages()
        return [PageResponse(**page) for page in pages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar páginas: {str(e)}")

@app.post("/api/pages", response_model=PageResponse)
async def create_page(page: PageRequest, current_user: dict = Depends(get_current_user)):
    """Adiciona uma nova página para monitoramento"""
    try:
        pages = load_pages()
        
        # Verifica se a URL já existe
        if any(p.get("url") == page.url for p in pages):
            raise HTTPException(status_code=400, detail="URL já cadastrada")
        
        # Adiciona a nova página
        new_page = {"url": page.url, "name": page.name}
        pages.append(new_page)
        save_pages(pages)
        
        write_log(f"Página adicionada: {page.name} ({page.url})")
        return PageResponse(**new_page)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar página: {str(e)}")

@app.delete("/api/pages")
async def delete_page(url: str, current_user: dict = Depends(get_current_user)):
    """Remove uma página do monitoramento"""
    try:
        pages = load_pages()
        original_count = len(pages)
        pages = [p for p in pages if p.get("url") != url]
        
        if len(pages) == original_count:
            raise HTTPException(status_code=404, detail="Página não encontrada")
        
        save_pages(pages)
        write_log(f"Página excluída: {url}")
        return {"success": True, "message": "Página excluída com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir página: {str(e)}")

@app.post("/api/scraper/run", response_model=ScraperResponse)
async def run_scraper(current_user: dict = Depends(get_current_user)):
    """
    Executa o scraper em todas as páginas cadastradas
    Retorna os links encontrados e estatísticas da execução
    """
    try:
        write_log("Iniciando coleta de links...")
        pages = load_pages()
        
        if not pages:
            return ScraperResponse(
                success=False,
                total_checked=0,
                links_found=0,
                links=[],
                message="Nenhuma página cadastrada"
            )
        
        all_found = []
        total_checked = 0
        
        for page in pages:
            url = str(page.get("url", "")).strip()
            name = str(page.get("name", "")).strip()
            
            if not url:
                continue
            
            total_checked += 1
            write_log(f"Verificando página: {name} ({url})")
            
            try:
                links, has_form, is_thanks = collect_from_page(url)
            except Exception as e:
                write_log(f"Erro ao coletar {url}: {e}")
                links = []
            
            # Processa e normaliza os links
            cleaned = []
            for l in links:
                c = normalize_whatsapp_link(l)
                if is_group_link(c):
                    cleaned.append(c)
            
            # Remove duplicatas
            cleaned = list(dict.fromkeys(cleaned))
            
            if cleaned:
                # Salva no banco de dados
                save_links(cleaned, source=name)
                
                # Prepara resposta e envia notificações
                for link in cleaned:
                    all_found.append({
                        "url": link,
                        "source": name,
                        "found_at": datetime.utcnow().isoformat()
                    })
                    send_telegram_message(link, name)
        
        # Registra última execução
        msg = f"Coleta finalizada. Páginas verificadas: {total_checked}, links encontrados: {len(all_found)}"
        with open(LAST_RUN_FILE, "w", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()} - {msg}")
        
        write_log(msg)
        
        return ScraperResponse(
            success=True,
            total_checked=total_checked,
            links_found=len(all_found),
            links=all_found,
            message=msg
        )
    except Exception as e:
        write_log(f"Erro na coleta: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao executar scraper: {str(e)}")

@app.get("/api/scraper/last-run")
async def get_last_run(current_user: dict = Depends(get_current_user)):
    """Retorna informações da última execução do scraper"""
    try:
        if not os.path.exists(LAST_RUN_FILE):
            return {"last_run": "Nunca executado"}
        
        with open(LAST_RUN_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            return {"last_run": content}
    except Exception as e:
        return {"last_run": f"Erro ao ler: {str(e)}"}

@app.get("/api/telegram/config")
async def get_telegram_config(current_user: dict = Depends(get_current_user)):
    """Retorna a configuração atual do Telegram"""
    config = load_config()
    telegram_config = config.get("telegram", {})
    return {
        "bot_token": telegram_config.get("bot_token", ""),
        "chat_id": telegram_config.get("chat_id", ""),
        "configured": bool(telegram_config.get("bot_token") and telegram_config.get("chat_id"))
    }

@app.post("/api/telegram/save")
async def save_telegram_config(config: TelegramConfig, current_user: dict = Depends(get_current_user)):
    """Salva a configuração do Telegram"""
    try:
        current_config = load_config()
        current_config["telegram"] = {
            "bot_token": config.bot_token.strip(),
            "chat_id": config.chat_id.strip()
        }
        
        if save_config(current_config):
            write_log("Configuração Telegram atualizada")
            return {"success": True, "message": "Configuração salva com sucesso"}
        else:
            raise HTTPException(status_code=500, detail="Erro ao salvar configuração")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar: {str(e)}")

@app.post("/api/telegram/test")
async def test_telegram(current_user: dict = Depends(get_current_user)):
    """Envia uma mensagem de teste para o Telegram"""
    import requests
    
    config = load_config()
    token = config.get("telegram", {}).get("bot_token", "").strip()
    chat_id = config.get("telegram", {}).get("chat_id", "").strip()
    
    if not token or not chat_id:
        raise HTTPException(status_code=400, detail="Telegram não configurado")
    
    msg = (
        "*TESTE DE NOTIFICAÇÃO*\n\n"
        f"Se você recebeu esta mensagem, o Telegram está configurado corretamente!\n\n"
        f"*Data/Hora:* {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "*Sistema operacional!*"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        write_log("Teste de Telegram enviado com sucesso")
        return {"success": True, "message": "Mensagem de teste enviada com sucesso!"}
    except Exception as e:
        write_log(f"Erro no teste de Telegram: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar teste: {str(e)}")

@app.get("/api/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Retorna estatísticas gerais do sistema"""
    try:
        links = list_links(10000)
        pages = load_pages()
        
        # Calcula estatísticas
        total_links = len(links)
        unique_links = len(set(link[0] for link in links))
        campaigns = len(set(link[1] for link in links if link[1]))
        total_pages = len(pages)
        
        # Lê última execução
        last_run = "Nunca executado"
        if os.path.exists(LAST_RUN_FILE):
            try:
                with open(LAST_RUN_FILE, "r", encoding="utf-8") as f:
                    last_run = f.read()
            except:
                pass
        
        return {
            "total_links": total_links,
            "unique_links": unique_links,
            "campaigns": campaigns,
            "total_pages": total_pages,
            "last_run": last_run
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

