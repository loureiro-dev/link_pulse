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
from backend.services.discovery.facebook_ads_discovery import (
    search_active_ads,
    FB_SEARCH_QUERIES,
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



# ─── FACEBOOK AD LIBRARY DISCOVERY ───────────────────────────────────────────

class FacebookDiscoveryRequest(BaseModel):
    search_terms: Optional[List[str]] = None
    limit_per_query: int = 20
    auto_add_with_url: bool = False


class FacebookAdResult(BaseModel):
    ad_id: str
    page_name: str
    name: str
    landing_urls: List[str]
    whatsapp_direct: List[str]
    snapshot_url: str
    ad_text: str
    search_term: str
    start_date: str
    added_urls: List[str] = []


class FacebookDiscoveryResponse(BaseModel):
    success: bool
    ads_found: int
    pages_added: int
    results: List[FacebookAdResult]
    message: str


@router.post("/facebook", response_model=FacebookDiscoveryResponse)
async def run_facebook_discovery(
    request: FacebookDiscoveryRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Busca anúncios ATIVOS no Facebook Ad Library relacionados a lançamentos
    com grupos WhatsApp. Requer token configurado em /api/facebook/save.
    """
    from backend.main import load_config

    user_id = current_user["id"]
    config = load_config()
    token = config.get("facebook", {}).get("access_token", "").strip()

    if not token:
        raise HTTPException(
            status_code=400,
            detail="Token do Facebook não configurado. Acesse as configurações e adicione seu token.",
        )

    try:
        ads = search_active_ads(
            access_token=token,
            search_terms=request.search_terms,
            limit_per_query=request.limit_per_query,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")

    pages_added = 0
    results: List[FacebookAdResult] = []

    for ad in ads:
        added_urls: List[str] = []

        if request.auto_add_with_url and ad["landing_urls"]:
            url = ad["landing_urls"][0]
            name = ad["name"] or ad["page_name"] or url
            if add_page(url, name, user_id):
                added_urls.append(url)
                pages_added += 1

        results.append(
            FacebookAdResult(
                ad_id=ad["ad_id"],
                page_name=ad["page_name"],
                name=ad["name"],
                landing_urls=ad["landing_urls"],
                whatsapp_direct=ad["whatsapp_direct"],
                snapshot_url=ad["snapshot_url"],
                ad_text=ad["ad_text"],
                search_term=ad["search_term"],
                start_date=ad["start_date"],
                added_urls=added_urls,
            )
        )

    msg = f"Facebook Ads: {len(ads)} anúncios ativos encontrados"
    if request.auto_add_with_url:
        msg += f" | {pages_added} páginas adicionadas"

    return FacebookDiscoveryResponse(
        success=True,
        ads_found=len(ads),
        pages_added=pages_added,
        results=results,
        message=msg,
    )


@router.get("/facebook/queries")
async def get_facebook_queries(current_user: dict = Depends(get_current_user)):
    """Retorna os termos de busca padrão para o Facebook"""
    return {"queries": FB_SEARCH_QUERIES}


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
