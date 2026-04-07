"""
API de Descoberta Automática de Páginas de Lançamento.

Módulos disponíveis:
  - DuckDuckGo  → /api/discovery/duckduckgo
  - YouTube     → /api/discovery/youtube
  - Telegram    → /api/discovery/telegram

Cada módulo é independente e pode ser usado separadamente.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from backend.auth.middleware import get_current_user
from backend.db.pages import add_page

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


# ─── MODELOS COMPARTILHADOS ───────────────────────────────────────────────────

class AddPageRequest(BaseModel):
    url: str
    name: str


@router.post("/add")
async def add_discovered_page(
    request: AddPageRequest,
    current_user: dict = Depends(get_current_user),
):
    """Adiciona uma página descoberta ao monitoramento do usuário."""
    user_id = current_user["id"]
    added = add_page(request.url, request.name, user_id)
    if added:
        return {"success": True, "message": "Página adicionada ao monitoramento"}
    return {"success": False, "message": "Página já existe no monitoramento"}


# ─── MÓDULO: DUCKDUCKGO ───────────────────────────────────────────────────────

class DuckDuckGoRequest(BaseModel):
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


class DuckDuckGoResponse(BaseModel):
    success: bool
    pages_found: int
    pages_added: int
    pages: List[DiscoveredPage]
    message: str


@router.get("/duckduckgo/queries")
async def get_ddg_queries(current_user: dict = Depends(get_current_user)):
    """Retorna as queries padrão do DuckDuckGo."""
    from backend.services.discovery.page_discovery import DEFAULT_QUERIES
    return {"queries": DEFAULT_QUERIES}


@router.post("/duckduckgo", response_model=DuckDuckGoResponse)
async def run_duckduckgo_discovery(
    request: DuckDuckGoRequest,
    current_user: dict = Depends(get_current_user),
):
    """Descobre páginas de lançamento via DuckDuckGo (sem API key)."""
    from backend.services.discovery.page_discovery import discover_pages

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
    result_pages = []

    for page in pages:
        added = False
        if request.auto_add:
            added = add_page(page["url"], page["name"], user_id)
            if added:
                pages_added += 1

        result_pages.append(DiscoveredPage(
            url=page["url"],
            name=page["name"],
            has_whatsapp=page.get("has_whatsapp"),
            verified=page.get("verified", False),
            added=added,
            query=page.get("query"),
        ))

    msg = f"DuckDuckGo: {len(pages)} páginas com WhatsApp encontradas"
    if request.auto_add:
        msg += f" | {pages_added} adicionadas"

    return DuckDuckGoResponse(
        success=True,
        pages_found=len(pages),
        pages_added=pages_added,
        pages=result_pages,
        message=msg,
    )


# ─── MÓDULO: YOUTUBE ─────────────────────────────────────────────────────────

class YoutubeRequest(BaseModel):
    queries: Optional[List[str]] = None
    max_results_per_query: int = 10
    auto_add_with_url: bool = False


class YoutubeVideoResult(BaseModel):
    video_id: str
    title: str
    channel: str
    published_at: str
    description: str
    thumbnail: str
    video_url: str
    query: str
    whatsapp_links: List[str]
    landing_urls: List[str]
    added_urls: List[str] = []


class YoutubeResponse(BaseModel):
    success: bool
    videos_found: int
    pages_added: int
    results: List[YoutubeVideoResult]
    message: str


@router.get("/youtube/queries")
async def get_youtube_queries(current_user: dict = Depends(get_current_user)):
    """Retorna as queries padrão do YouTube."""
    from backend.services.discovery.youtube_discovery import YT_DEFAULT_QUERIES
    return {"queries": YT_DEFAULT_QUERIES}


@router.post("/youtube", response_model=YoutubeResponse)
async def run_youtube_discovery(
    request: YoutubeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Descobre vídeos de lançamento no YouTube e extrai links WhatsApp."""
    from backend.services.discovery.youtube_discovery import discover_from_youtube
    from backend.main import load_config

    user_id = current_user["id"]
    config = load_config()
    api_key = config.get("youtube", {}).get("api_key", "").strip()

    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Chave da YouTube API não configurada. Acesse Configurações.",
        )

    try:
        videos = discover_from_youtube(
            api_key=api_key,
            queries=request.queries,
            max_results_per_query=request.max_results_per_query,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")

    pages_added = 0
    results = []

    for v in videos:
        added_urls = []
        if request.auto_add_with_url and v["landing_urls"]:
            url = v["landing_urls"][0]
            if add_page(url, v["title"][:100], user_id):
                added_urls.append(url)
                pages_added += 1

        results.append(YoutubeVideoResult(
            video_id=v["video_id"],
            title=v["title"],
            channel=v["channel"],
            published_at=v["published_at"],
            description=v["description"],
            thumbnail=v["thumbnail"],
            video_url=v["video_url"],
            query=v["query"],
            whatsapp_links=v["whatsapp_links"],
            landing_urls=v["landing_urls"],
            added_urls=added_urls,
        ))

    msg = f"YouTube: {len(videos)} vídeos encontrados"
    with_links = sum(1 for r in results if r.whatsapp_links or r.landing_urls)
    if with_links:
        msg += f" | {with_links} com links úteis"

    return YoutubeResponse(
        success=True,
        videos_found=len(videos),
        pages_added=pages_added,
        results=results,
        message=msg,
    )


# ─── MÓDULO: COLETA RÁPIDA (VIA UI OU BOT TELEGRAM) ─────────────────────────

class QuickCollectRequest(BaseModel):
    urls: List[str]
    source_name: Optional[str] = "Envio Manual"
    add_to_pages: bool = True


class QuickCollectResult(BaseModel):
    url: str
    name: str
    page_added: bool
    links_found: int
    links: List[str]
    success: bool
    message: str


class QuickCollectResponse(BaseModel):
    success: bool
    urls_processed: int
    total_links_found: int
    results: List[QuickCollectResult]
    message: str


@router.post("/quick", response_model=QuickCollectResponse)
async def quick_collect(
    request: QuickCollectRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Coleta imediata de uma ou mais URLs submetidas pelo usuário.
    Adiciona às páginas monitoradas e scrapa em busca de grupos WhatsApp.
    Ideal para URLs recebidas via Telegram ou outras fontes.
    """
    from backend.services.discovery.quick_collect import collect_url_now

    if not request.urls:
        raise HTTPException(status_code=400, detail="Informe pelo menos uma URL.")

    user_id = current_user["id"]
    results = []
    total_links = 0

    for url in request.urls:
        url = url.strip()
        if not url.startswith("http"):
            url = "https://" + url

        result = collect_url_now(
            url=url,
            user_id=user_id,
            source_name=request.source_name,
            add_to_pages=request.add_to_pages,
            send_telegram=True,
        )

        total_links += result.get("links_found", 0)
        results.append(QuickCollectResult(
            url=result["url"],
            name=result["name"],
            page_added=result.get("page_added", False),
            links_found=result.get("links_found", 0),
            links=result.get("links", []),
            success=result["success"],
            message=result["message"],
        ))

    msg = f"{len(request.urls)} URL(s) processada(s) — {total_links} grupo(s) WhatsApp encontrado(s)"

    return QuickCollectResponse(
        success=True,
        urls_processed=len(request.urls),
        total_links_found=total_links,
        results=results,
        message=msg,
    )
