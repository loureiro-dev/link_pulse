"""
Rotas da API para gerenciamento de páginas monitoradas
Endpoints: /api/pages (GET, POST, DELETE)
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from backend.auth.middleware import get_current_user
from backend.main import (
    PageRequest, 
    PageResponse, 
    load_pages, 
    save_pages, 
    write_log
)

router = APIRouter(prefix="/api", tags=["pages"])


@router.get("/pages", response_model=List[PageResponse])
async def get_pages(current_user: dict = Depends(get_current_user)):
    """Retorna todas as páginas cadastradas para monitoramento"""
    try:
        pages = load_pages()
        return [PageResponse(**page) for page in pages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar páginas: {str(e)}")


@router.post("/pages", response_model=PageResponse)
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


@router.delete("/pages")
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

