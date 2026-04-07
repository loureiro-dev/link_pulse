"""
Módulo de descoberta via YouTube Data API v3.
Busca vídeos de lançamentos brasileiros com links de grupos WhatsApp
nas descrições.

Como obter a API Key:
  1. Acesse https://console.cloud.google.com/
  2. Crie um projeto → Ative a YouTube Data API v3
  3. Credenciais → Criar credencial → Chave de API
  4. Cole a chave nas Configurações do LinkPulse

Quota gratuita: 10.000 unidades/dia (≈ 100 buscas)
"""

import re
import requests
from typing import List, Dict, Optional

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

WHATSAPP_RE = re.compile(
    r'https?://chat\.whatsapp\.com/[A-Za-z0-9]+', re.IGNORECASE
)
URL_RE = re.compile(r'https?://[^\s\'"<>()\[\]]+', re.IGNORECASE)

SKIP_DOMAINS = ["youtube.com", "youtu.be", "google.com", "goo.gl", "bit.ly", "t.co"]

YT_DEFAULT_QUERIES = [
    "grupo whatsapp lançamento 2026",
    "entrar no grupo whatsapp curso lançamento",
    "grupo vip whatsapp lançamento digital",
    "link do grupo whatsapp lançamento",
    "comunidade whatsapp curso online lançamento",
    "grupo exclusivo whatsapp hotmart lançamento",
]


def _extract_urls(text: str) -> Dict[str, List[str]]:
    """Extrai links de WhatsApp e URLs de landing pages de um texto."""
    whatsapp = list(dict.fromkeys(WHATSAPP_RE.findall(text)))
    all_urls = URL_RE.findall(text)
    landing = list(dict.fromkeys(
        u.rstrip(".,;)")
        for u in all_urls
        if not any(skip in u for skip in SKIP_DOMAINS)
        and "whatsapp" not in u.lower()
    ))[:5]
    return {"whatsapp": whatsapp, "landing": landing}


def _search_videos(api_key: str, query: str, max_results: int) -> List[Dict]:
    """Faz uma busca no YouTube e retorna os itens encontrados."""
    params = {
        "key": api_key,
        "q": query,
        "type": "video",
        "part": "snippet",
        "maxResults": min(max_results, 50),
        "order": "date",
        "relevanceLanguage": "pt",
        "regionCode": "BR",
    }
    resp = requests.get(SEARCH_URL, params=params, timeout=12)

    if resp.status_code == 400:
        error = resp.json().get("error", {})
        raise RuntimeError(f"Erro na API do YouTube: {error.get('message', 'chave inválida')}")
    resp.raise_for_status()
    return resp.json().get("items", [])


def _get_full_descriptions(api_key: str, video_ids: List[str]) -> Dict[str, str]:
    """Busca descrições completas dos vídeos (a busca só retorna 100 chars)."""
    descriptions = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        params = {"key": api_key, "id": ",".join(batch), "part": "snippet"}
        try:
            resp = requests.get(VIDEOS_URL, params=params, timeout=12)
            resp.raise_for_status()
            for item in resp.json().get("items", []):
                descriptions[item["id"]] = item["snippet"].get("description", "")
        except Exception:
            continue
    return descriptions


def validate_api_key(api_key: str) -> Dict:
    """Valida se a chave da YouTube API está funcionando."""
    try:
        params = {"key": api_key, "q": "test", "type": "video", "part": "id", "maxResults": 1}
        resp = requests.get(SEARCH_URL, params=params, timeout=10)
        data = resp.json()
        if "error" in data:
            return {"valid": False, "message": data["error"].get("message", "Chave inválida")}
        return {"valid": True, "message": "Chave válida — YouTube API acessível"}
    except Exception as e:
        return {"valid": False, "message": str(e)}


def discover_from_youtube(
    api_key: str,
    queries: Optional[List[str]] = None,
    max_results_per_query: int = 10,
) -> List[Dict]:
    """
    Busca vídeos de lançamentos no YouTube e extrai links WhatsApp e landing pages.

    Returns:
        Lista de dicts com info do vídeo + links extraídos.
    """
    if not queries:
        queries = YT_DEFAULT_QUERIES

    seen_ids: set = set()
    results: List[Dict] = []

    for query in queries:
        try:
            items = _search_videos(api_key, query, max_results_per_query)
            for item in items:
                video_id = item["id"].get("videoId", "")
                if not video_id or video_id in seen_ids:
                    continue
                seen_ids.add(video_id)

                snippet = item["snippet"]
                results.append({
                    "video_id": video_id,
                    "title": snippet.get("title", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "description": snippet.get("description", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                    "video_url": f"https://www.youtube.com/watch?v={video_id}",
                    "query": query,
                    "whatsapp_links": [],
                    "landing_urls": [],
                })
        except RuntimeError:
            raise
        except Exception:
            continue

    if results:
        video_ids = [r["video_id"] for r in results]
        descriptions = _get_full_descriptions(api_key, video_ids)

        for r in results:
            full_desc = descriptions.get(r["video_id"], r["description"])
            r["description"] = full_desc[:400]
            extracted = _extract_urls(full_desc)
            r["whatsapp_links"] = extracted["whatsapp"]
            r["landing_urls"] = extracted["landing"]

    return results
