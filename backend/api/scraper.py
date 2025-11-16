"""
Rotas da API para execução do scraper
Endpoints: /api/scraper/run, /api/scraper/last-run
"""

from fastapi import APIRouter, HTTPException, Depends
from backend.auth.middleware import get_current_user
from backend.main import (
    ScraperResponse, 
    load_pages, 
    write_log, 
    LAST_RUN_FILE,
    collect_from_page,
    normalize_whatsapp_link,
    is_group_link,
    save_links,
    send_telegram_message
)
from datetime import datetime
import os

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


@router.post("/run", response_model=ScraperResponse)
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


@router.get("/last-run")
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

