"""
Rotas da API para gerenciamento de links coletados
Endpoints: /api/links, /api/stats
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from backend.auth.middleware import get_current_user
from backend.db.connection import list_links
from backend.models import LinkResponse
import os
from datetime import datetime

router = APIRouter(prefix="/api", tags=["links"])

# Configuração de paths (importa de main.py)
from backend.main import LAST_RUN_FILE

@router.get("/links", response_model=List[LinkResponse])
async def get_links(limit: int = 1000, current_user: dict = Depends(get_current_user)):
    """
    Retorna a lista de links coletados do usuário atual
    Parâmetro limit controla quantos links retornar (padrão: 1000)
    """
    try:
        user_id = current_user["id"]
        rows = list_links(limit, user_id=user_id)
        links = [
            LinkResponse(url=row[0], source=row[1], found_at=row[2])
            for row in rows
        ]
        return links
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar links: {str(e)}")


@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Retorna estatísticas do usuário atual"""
    try:
        user_id = current_user["id"]
        links = list_links(10000, user_id=user_id)
        from backend.db.pages import load_pages
        pages = load_pages(user_id)
        
        # Calcula estatísticas
        total_links = len(links)
        unique_links = len(set(link[0] for link in links))
        campaigns = len(set(link[1] for link in links if link[1]))
        total_pages = len(pages)
        
        # Lê última execução (por usuário)
        last_run = "Nunca executado"
        user_last_run_file = f"{LAST_RUN_FILE}.{user_id}"
        if os.path.exists(user_last_run_file):
            try:
                with open(user_last_run_file, "r", encoding="utf-8") as f:
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

