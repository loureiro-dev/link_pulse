"""
API de Descoberta Automática de Páginas de Lançamento.

Módulos disponíveis:
  - DuckDuckGo  → /api/discovery/duckduckgo
  - YouTube     → /api/discovery/youtube
  - Telegram    → /api/discovery/telegram

Cada módulo é independente e pode ser usado separadamente.
"""

import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from backend.auth.middleware import get_current_user
from backend.db.pages import add_page
from backend.db.settings import get_setting, save_setting

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


# ─── GESTÃO DE KEYWORDS CUSTOMIZADAS ─────────────────────────────────────────

VALID_MODULES = {"ddg", "youtube", "facebook"}


def _load_custom_queries(user_id: int, module: str) -> List[str]:
    raw = get_setting(user_id, f"custom_queries_{module}")
    if not raw:
        return []
    try:
        return json.loads(raw)
    except Exception:
        return []


def _save_custom_queries(user_id: int, module: str, queries: List[str]) -> None:
    save_setting(user_id, f"custom_queries_{module}", json.dumps(queries, ensure_ascii=False))


class CustomQueriesRequest(BaseModel):
    module: str          # "ddg" | "youtube" | "facebook"
    queries: List[str]   # lista completa (substitui)


@router.get("/custom-queries")
async def get_custom_queries(
    module: str,
    current_user: dict = Depends(get_current_user),
):
    if module not in VALID_MODULES:
        raise HTTPException(status_code=400, detail=f"Módulo inválido. Use: {VALID_MODULES}")
    user_id = current_user["id"]
    return {"module": module, "queries": _load_custom_queries(user_id, module)}


@router.post("/custom-queries")
async def save_custom_queries(
    request: CustomQueriesRequest,
    current_user: dict = Depends(get_current_user),
):
    if request.module not in VALID_MODULES:
        raise HTTPException(status_code=400, detail=f"Módulo inválido. Use: {VALID_MODULES}")
    user_id = current_user["id"]
    cleaned = [q.strip() for q in request.queries if q.strip()]
    _save_custom_queries(user_id, request.module, cleaned)
    return {"success": True, "module": request.module, "total": len(cleaned)}


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
    only_with_whatsapp: bool = False
    auto_add: bool = False
    use_ai: bool = False  # classifica cada resultado com IA


class DiscoveredPage(BaseModel):
    url: str
    name: str
    has_whatsapp: Optional[bool] = None
    has_form: Optional[bool] = None
    url_score: int = 0
    landing_score: int = 0
    total_score: int = 0
    signals: List[str] = []
    whatsapp_links: List[str] = []
    verified: bool = False
    added: bool = False
    query: Optional[str] = None
    # Campos de IA (preenchidos quando use_ai=True)
    ai_status: Optional[str] = None        # "approved" | "rejected" | "review"
    ai_confidence: Optional[float] = None
    ai_niche: Optional[str] = None
    ai_reasoning: Optional[str] = None


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

    # Mescla: queries do request → customizadas do banco → padrão
    queries = request.queries or []
    queries += _load_custom_queries(user_id, "ddg")
    if not queries:
        queries = None  # usa DEFAULT_QUERIES do módulo

    try:
        pages = discover_pages(
            queries=queries,
            max_results_per_query=request.max_results_per_query,
            verify=request.verify,
            only_with_whatsapp=request.only_with_whatsapp,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na descoberta: {str(e)}")

    # Classificação IA (opcional)
    ai_cfg = None
    if request.use_ai:
        from backend.api.settings import _get_ai_config
        from backend.services.ai.classifier import classify_batch
        ai_cfg = _get_ai_config(user_id)
        if ai_cfg.get("api_key") and ai_cfg.get("enabled"):
            pages = classify_batch(
                pages,
                api_key=ai_cfg["api_key"],
                provider=ai_cfg.get("provider", "gemini"),
                min_confidence=ai_cfg.get("min_confidence", 0.65),
            )

    pages_added = 0
    result_pages = []

    for page in pages:
        ai = page.get("ai", {})
        ai_status = page.get("ai_status")

        # Com IA ativa: auto_add só aprova os "approved"
        added = False
        if request.auto_add:
            if not request.use_ai or ai_status == "approved":
                added = add_page(page["url"], page["name"], user_id)
                if added:
                    pages_added += 1

        result_pages.append(DiscoveredPage(
            url=page["url"],
            name=page["name"],
            has_whatsapp=page.get("has_whatsapp"),
            has_form=page.get("has_form"),
            url_score=page.get("url_score", 0),
            landing_score=page.get("landing_score", 0),
            total_score=page.get("total_score", 0),
            signals=page.get("signals", []),
            whatsapp_links=page.get("whatsapp_links", []),
            verified=page.get("verified", False),
            added=added,
            query=page.get("query"),
            ai_status=ai_status,
            ai_confidence=ai.get("confidence"),
            ai_niche=ai.get("niche"),
            ai_reasoning=ai.get("reasoning"),
        ))

    msg = f"DuckDuckGo: {len(pages)} páginas de captura encontradas"
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
    filter_tutorials: bool = True
    only_with_links: bool = False
    use_ai: bool = False   # classifica landing_urls de cada vídeo com IA


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
    # Campos de IA por landing URL (preenchidos quando use_ai=True)
    ai_status: Optional[str] = None        # "approved" | "rejected" | "review"
    ai_confidence: Optional[float] = None
    ai_niche: Optional[str] = None
    ai_reasoning: Optional[str] = None


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
    from backend.db.settings import get_youtube_api_key

    user_id = current_user["id"]
    api_key = get_youtube_api_key(user_id).strip()

    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Chave da YouTube API não configurada. Acesse Configurações.",
        )

    # Mescla: queries do request → customizadas do banco → padrão
    queries = list(request.queries or [])
    queries += _load_custom_queries(user_id, "youtube")
    if not queries:
        queries = None  # usa YT_DEFAULT_QUERIES do módulo

    try:
        videos = discover_from_youtube(
            api_key=api_key,
            queries=queries,
            max_results_per_query=request.max_results_per_query,
            filter_tutorials=request.filter_tutorials,
            only_with_links=request.only_with_links,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")

    # Classificação IA nas landing URLs de cada vídeo (opcional)
    if request.use_ai:
        from backend.api.settings import _get_ai_config
        from backend.services.ai.classifier import classify_page as ai_classify
        ai_cfg = _get_ai_config(user_id)
        if ai_cfg.get("api_key") and ai_cfg.get("enabled"):
            for v in videos:
                if v["landing_urls"]:
                    # Classifica a primeira landing URL do vídeo
                    url_to_classify = v["landing_urls"][0]
                    ai_result = ai_classify(
                        url=url_to_classify,
                        title=v["title"],
                        api_key=ai_cfg["api_key"],
                        provider=ai_cfg.get("provider", "gemini"),
                        user_id=user_id,
                    )
                    v["ai_status"]     = "approved" if (ai_result.get("is_capture_page") and ai_result.get("confidence", 0) >= ai_cfg.get("min_confidence", 0.65)) else (
                                         "rejected" if (ai_result.get("is_capture_page") is False and ai_result.get("confidence", 0) >= ai_cfg.get("min_confidence", 0.65)) else "review")
                    v["ai_confidence"] = ai_result.get("confidence")
                    v["ai_niche"]      = ai_result.get("niche")
                    v["ai_reasoning"]  = ai_result.get("reasoning")

    pages_added = 0
    results = []

    for v in videos:
        added_urls = []
        ai_status = v.get("ai_status")

        if request.auto_add_with_url and v["landing_urls"]:
            url = v["landing_urls"][0]
            # Com IA: só adiciona se aprovado ou sem IA ativa
            if not request.use_ai or ai_status == "approved":
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
            ai_status=ai_status,
            ai_confidence=v.get("ai_confidence"),
            ai_niche=v.get("ai_niche"),
            ai_reasoning=v.get("ai_reasoning"),
        ))

    msg = f"YouTube: {len(videos)} vídeos encontrados"
    with_links = sum(1 for r in results if r.whatsapp_links or r.landing_urls)
    if with_links:
        msg += f" | {with_links} com links úteis"
    if request.use_ai:
        approved = sum(1 for r in results if r.ai_status == "approved")
        msg += f" | IA: {approved} aprovados"

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


# ─── MÓDULO: FACEBOOK AD LIBRARY (SELENIUM + IA) ─────────────────────────────

class FacebookLibraryRequest(BaseModel):
    queries: List[str]
    scroll_times: int = 3
    max_ads_per_query: int = 20
    use_ai: bool = True
    auto_add: bool = False


class FacebookLibraryPage(BaseModel):
    url: str
    name: str
    url_score: int = 0
    source_query: str = ""
    ai_status: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_niche: Optional[str] = None
    ai_reasoning: Optional[str] = None
    added: bool = False


class FacebookLibraryResponse(BaseModel):
    success: bool
    pages_found: int
    pages_added: int
    approved: int
    review: int
    rejected: int
    pages: List[FacebookLibraryPage]
    message: str


@router.post("/facebook-library", response_model=FacebookLibraryResponse)
async def run_facebook_library_discovery(
    request: FacebookLibraryRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Scraping automático da Biblioteca de Anúncios do Facebook.
    Usa Selenium + IA para encontrar e filtrar landing pages de lançamentos.
    """
    from backend.services.discovery.facebook_discovery import discover_from_facebook_library
    from backend.api.settings import _get_ai_config

    user_id = current_user["id"]

    ai_key = ""
    ai_provider = "gemini"
    ai_min_conf = 0.65

    if request.use_ai:
        ai_cfg = _get_ai_config(user_id)
        if ai_cfg.get("enabled") and ai_cfg.get("api_key"):
            ai_key = ai_cfg["api_key"]
            ai_provider = ai_cfg.get("provider", "gemini")
            ai_min_conf = ai_cfg.get("min_confidence", 0.65)

    try:
        pages = discover_from_facebook_library(
            queries=request.queries,
            scroll_times=request.scroll_times,
            max_ads_per_query=request.max_ads_per_query,
            ai_api_key=ai_key,
            ai_provider=ai_provider,
            ai_min_confidence=ai_min_conf,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no scraping: {str(e)}")

    pages_added = 0
    result_pages = []
    counts = {"approved": 0, "review": 0, "rejected": 0}

    for page in pages:
        status = page.get("ai_status") or "review"
        if status in counts:
            counts[status] += 1

        added = False
        if request.auto_add and status == "approved":
            added = add_page(page["url"], page["name"], user_id)
            if added:
                pages_added += 1

        result_pages.append(FacebookLibraryPage(
            url=page["url"],
            name=page["name"],
            url_score=page.get("url_score", 0),
            source_query=page.get("source_query", ""),
            ai_status=status,
            ai_confidence=page.get("ai_confidence"),
            ai_niche=page.get("ai_niche"),
            ai_reasoning=page.get("ai_reasoning"),
            added=added,
        ))

    msg = (f"Facebook Library: {len(pages)} páginas encontradas"
           f" | ✓ {counts['approved']} aprovadas · ? {counts['review']} revisar · ✗ {counts['rejected']} rejeitadas")

    return FacebookLibraryResponse(
        success=True,
        pages_found=len(pages),
        pages_added=pages_added,
        approved=counts["approved"],
        review=counts["review"],
        rejected=counts["rejected"],
        pages=result_pages,
        message=msg,
    )
