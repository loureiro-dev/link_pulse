"""
Rotas da API para gerenciamento de páginas monitoradas
Endpoints: /api/pages (GET, POST, DELETE)
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from backend.auth.middleware import get_current_user
from backend.models import PageRequest, PageResponse
from backend.db.pages import load_pages, save_pages, add_page, delete_page
from backend.main import write_log

router = APIRouter(prefix="/api", tags=["pages"])


@router.get("/pages", response_model=List[PageResponse])
async def get_pages(current_user: dict = Depends(get_current_user)):
    """Retorna todas as páginas cadastradas para monitoramento do usuário atual"""
    try:
        user_id = current_user["id"]
        pages = load_pages(user_id)
        return [PageResponse(**page) for page in pages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar páginas: {str(e)}")


@router.post("/pages", response_model=PageResponse)
async def create_page(page: PageRequest, current_user: dict = Depends(get_current_user)):
    """Adiciona uma nova página para monitoramento do usuário atual"""
    try:
        user_id = current_user["id"]
        
        # Tenta adicionar a página
        if not add_page(page.url, page.name, user_id):
            raise HTTPException(status_code=400, detail="URL já cadastrada")
        
        write_log(f"Página adicionada: {page.name} ({page.url}) - User: {user_id}")
        return PageResponse(url=page.url, name=page.name)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar página: {str(e)}")


@router.delete("/pages")
async def delete_page_route(url: str, current_user: dict = Depends(get_current_user)):
    """Remove uma página do monitoramento do usuário atual"""
    try:
        user_id = current_user["id"]
        
        if not delete_page(url, user_id):
            raise HTTPException(status_code=404, detail="Página não encontrada")
        
        write_log(f"Página excluída: {url} - User: {user_id}")
        return {"success": True, "message": "Página excluída com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir página: {str(e)}")

