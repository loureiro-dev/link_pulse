"""
Rotas da API para descoberta automática de páginas de lançamento.
Endpoints: /api/discovery/run, /api/discovery/add, /api/discovery/queries
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from backend.auth.middleware import get_current_user
from backend.db.pages import add_page
from backend.services.discovery.page_discovery import (
    discover_pages,
    DEFAULT_QUERIES,
)

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


class DiscoveryRequest(BaseModel):
    queries: Optional[List[str]] = None
    max_results_per_query: int = 5
    verify: bool = True
    only_with_whatsapp: bool = True
    auto_add: bool = False


class DiscoveredPage(BaseModel):
    url: str
    name: str
    has_whatsapp: Optional[bool] = None
    verified: bool = False
    added: bool = False
    query: Optional[str] = None


class DiscoveryResponse(BaseModel):
    success: bool
    pages_found: int
    pages_added: int
    pages: List[DiscoveredPage]
    message: str


class AddPageRequest(BaseModel):
    url: str
    name: str


@router.get("/queries")
async def get_default_queries(current_user: dict = Depends(get_current_user)):
    """Retorna as queries padrão de descoberta"""
    return {"queries": DEFAULT_QUERIES}


@router.post("/run", response_model=DiscoveryResponse)
async def run_discovery(
    request: DiscoveryRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Executa a descoberta automática de páginas de lançamento via DuckDuckGo.
    Se auto_add=True, adiciona as páginas encontradas diretamente ao monitoramento.
    """
    user_id = current_user["id"]

    try:
        pages = discover_pages(
            queries=request.queries,
            max_results_per_query=request.max_results_per_query,
            verify=request.verify,
            only_with_whatsapp=request.only_with_whatsapp,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na descoberta: {str(e)}")

    pages_added = 0
    result_pages: List[DiscoveredPage] = []

    for page in pages:
        added = False
        if request.auto_add:
            added = add_page(page["url"], page["name"], user_id)
            if added:
                pages_added += 1

        result_pages.append(
            DiscoveredPage(
                url=page["url"],
                name=page["name"],
                has_whatsapp=page.get("has_whatsapp"),
                verified=page.get("verified", False),
                added=added,
                query=page.get("query"),
            )
        )

    msg = f"Descoberta concluída. Páginas com WhatsApp encontradas: {len(pages)}"
    if request.auto_add:
        msg += f" | Adicionadas ao monitoramento: {pages_added}"

    return DiscoveryResponse(
        success=True,
        pages_found=len(pages),
        pages_added=pages_added,
        pages=result_pages,
        message=msg,
    )


@router.post("/add")
async def add_discovered_page(
    request: AddPageRequest,
    current_user: dict = Depends(get_current_user),
):
    """Adiciona uma página descoberta ao monitoramento do usuário"""
    user_id = current_user["id"]
    added = add_page(request.url, request.name, user_id)

    if added:
        return {"success": True, "message": "Página adicionada ao monitoramento"}
    return {"success": False, "message": "Página já existe no monitoramento"}
