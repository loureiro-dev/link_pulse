"""
Coleta imediata de uma URL submetida manualmente.

Fluxo:
  1. URL recebida (via UI ou bot Telegram)
  2. Adicionada às páginas monitoradas do usuário
  3. Scraped imediatamente em busca de grupos WhatsApp
  4. Links salvos no banco + notificação Telegram enviada
  5. Resultado retornado ao chamador
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional
from backend.services.collectors.requests_collector import collect_from_page
from backend.services.processing.cleaning import normalize_whatsapp_link, is_group_link
from backend.db.pages import add_page
from backend.db.connection import save_links


def collect_url_now(
    url: str,
    user_id: int,
    source_name: Optional[str] = None,
    add_to_pages: bool = True,
    send_telegram: bool = True,
) -> Dict:
    """
    Adiciona uma URL ao monitoramento e a coleta imediatamente.

    Args:
        url:           URL a ser coletada
        user_id:       ID do usuário dono da coleta
        source_name:   Nome/label da origem (ex: 'Via Telegram')
        add_to_pages:  Se True, adiciona às páginas monitoradas
        send_telegram: Se True, envia notificação para o Telegram do usuário

    Returns:
        Dict com resultado: links encontrados, status, mensagem
    """
    name = source_name or _extract_name(url)
    page_added = False

    if add_to_pages:
        page_added = add_page(url, name, user_id)

    try:
        links_raw, has_form, is_thanks = collect_from_page(url)
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "name": name,
            "page_added": page_added,
            "links_found": 0,
            "links": [],
            "message": f"Erro ao acessar a página: {str(e)}",
        }

    cleaned: List[str] = []
    for raw in links_raw:
        normalized = normalize_whatsapp_link(raw)
        if is_group_link(normalized) and normalized not in cleaned:
            cleaned.append(normalized)

    if cleaned:
        save_links(cleaned, source=name, user_id=user_id)

        if send_telegram:
            try:
                from backend.main import send_telegram_message
                for link in cleaned:
                    send_telegram_message(link, name)
            except Exception:
                pass

    return {
        "success": True,
        "url": url,
        "name": name,
        "page_added": page_added,
        "links_found": len(cleaned),
        "links": cleaned,
        "has_form": has_form,
        "is_thank_you_page": is_thanks,
        "message": (
            f"{len(cleaned)} grupo(s) WhatsApp encontrado(s) em '{name}'"
            if cleaned else
            f"Nenhum grupo WhatsApp encontrado em '{name}'"
        ),
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def _extract_name(url: str) -> str:
    """Extrai um nome legível a partir de uma URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        path = parsed.path.strip("/").split("/")[0] if parsed.path.strip("/") else ""
        return f"{domain}/{path}" if path else domain
    except Exception:
        return url[:60]
