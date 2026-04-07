"""
Módulo de descoberta via Facebook Ad Library API.
API oficial e gratuita do Meta para buscar anúncios ativos.

Como obter o token:
  1. Acesse https://developers.facebook.com/tools/explorer/
  2. Selecione "User Token" e adicione a permissão 'ads_read'
  3. Clique em "Generate Access Token"
  4. Cole o token nas configurações do LinkPulse

Documentação: https://developers.facebook.com/docs/marketing-api/reference/ads_archive
"""

import re
import requests
from typing import List, Dict, Optional

GRAPH_API_VERSION = "v21.0"
ADS_ARCHIVE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/ads_archive"

# Termos de busca focados em lançamentos brasileiros com WhatsApp
FB_SEARCH_QUERIES = [
    "grupo whatsapp lançamento",
    "entrar no grupo whatsapp",
    "grupo vip whatsapp",
    "grupo exclusivo whatsapp",
    "comunidade whatsapp curso",
    "link do grupo whatsapp",
]

# Regex para extrair URLs do texto dos anúncios
URL_RE = re.compile(r'https?://[^\s\'"<>(),]+', re.IGNORECASE)
WHATSAPP_RE = re.compile(
    r'(https?://)?(chat\.whatsapp\.com/[A-Za-z0-9]+|wa\.me/[0-9]+)',
    re.IGNORECASE
)

AD_FIELDS = ",".join([
    "id",
    "page_name",
    "page_id",
    "ad_creative_bodies",
    "ad_creative_link_captions",
    "ad_creative_link_titles",
    "ad_snapshot_url",
    "ad_delivery_start_time",
])


def _extract_urls_from_text(texts: List[str]) -> List[str]:
    """Extrai URLs encontradas no texto dos anúncios."""
    urls = []
    for text in (texts or []):
        matches = URL_RE.findall(text)
        for m in matches:
            m = m.rstrip(".,;)")
            if "facebook.com" not in m and "instagram.com" not in m:
                urls.append(m)
    return list(dict.fromkeys(urls))


def _extract_whatsapp_from_text(texts: List[str]) -> List[str]:
    """Extrai links diretos de WhatsApp do texto do anúncio."""
    links = []
    for text in (texts or []):
        for m in WHATSAPP_RE.finditer(text):
            full = m.group(0)
            if not full.startswith("http"):
                full = "https://" + full
            links.append(full)
    return list(dict.fromkeys(links))


def _reconstruct_url_from_caption(caption: str) -> Optional[str]:
    """
    Tenta reconstruir uma URL a partir da caption do anúncio.
    Captions como 'hotmart.com/curso-x' são convertidas em 'https://hotmart.com/curso-x'.
    """
    if not caption:
        return None
    caption = caption.strip()
    if caption.startswith("http"):
        return caption
    if "." in caption and " " not in caption:
        return "https://" + caption
    return None


def search_active_ads(
    access_token: str,
    search_terms: Optional[List[str]] = None,
    limit_per_query: int = 20,
) -> List[Dict]:
    """
    Busca anúncios ATIVOS no Brasil via Facebook Ad Library API.

    Returns:
        Lista de dicts com informações de cada anúncio encontrado.
    """
    if not search_terms:
        search_terms = FB_SEARCH_QUERIES

    seen_ids: set = set()
    results: List[Dict] = []

    for term in search_terms:
        params = {
            "access_token": access_token,
            "ad_type": "ALL",
            "ad_reached_countries": "BR",
            "ad_active_status": "ACTIVE",
            "search_terms": term,
            "fields": AD_FIELDS,
            "limit": limit_per_query,
        }

        try:
            resp = requests.get(ADS_ARCHIVE_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.HTTPError as e:
            error_body = {}
            try:
                error_body = e.response.json()
            except Exception:
                pass
            error_msg = error_body.get("error", {}).get("message", str(e))
            raise RuntimeError(f"Erro na API do Facebook: {error_msg}")
        except Exception as e:
            raise RuntimeError(f"Erro ao conectar ao Facebook: {str(e)}")

        for ad in data.get("data", []):
            ad_id = ad.get("id")
            if ad_id in seen_ids:
                continue
            seen_ids.add(ad_id)

            bodies = ad.get("ad_creative_bodies") or []
            captions = ad.get("ad_creative_link_captions") or []
            titles = ad.get("ad_creative_link_titles") or []

            landing_urls = _extract_urls_from_text(bodies)
            whatsapp_in_ad = _extract_whatsapp_from_text(bodies)

            # Tenta reconstruir URL a partir da caption
            if not landing_urls:
                for cap in captions:
                    url = _reconstruct_url_from_caption(cap)
                    if url:
                        landing_urls.append(url)

            ad_name = (
                " | ".join(titles[:1])
                or " | ".join(captions[:1])
                or ad.get("page_name", f"Anúncio {ad_id}")
            )[:100]

            results.append({
                "ad_id": ad_id,
                "page_name": ad.get("page_name", ""),
                "page_id": ad.get("page_id", ""),
                "name": ad_name,
                "landing_urls": landing_urls,
                "whatsapp_direct": whatsapp_in_ad,
                "snapshot_url": ad.get("ad_snapshot_url", ""),
                "ad_text": bodies[:1][0][:200] if bodies else "",
                "search_term": term,
                "start_date": ad.get("ad_delivery_start_time", ""),
            })

    return results


def validate_token(access_token: str) -> Dict:
    """
    Valida se o token tem acesso à Ad Library API.
    Faz uma busca mínima como teste.
    """
    try:
        params = {
            "access_token": access_token,
            "ad_type": "ALL",
            "ad_reached_countries": "BR",
            "ad_active_status": "ACTIVE",
            "search_terms": "whatsapp",
            "fields": "id",
            "limit": 1,
        }
        resp = requests.get(ADS_ARCHIVE_URL, params=params, timeout=10)
        data = resp.json()

        if "error" in data:
            return {
                "valid": False,
                "message": data["error"].get("message", "Token inválido"),
            }

        return {"valid": True, "message": "Token válido — Ad Library acessível"}
    except Exception as e:
        return {"valid": False, "message": str(e)}
