"""
Módulo de descoberta automática de páginas de lançamento.
Usa DuckDuckGo (gratuito, sem API key) para encontrar páginas
de lançamentos brasileiros que potencialmente contêm links de grupos WhatsApp.
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple

# Termos de busca pré-configurados focados em lançamentos brasileiros
DEFAULT_QUERIES = [
    '"grupo whatsapp" lançamento hotmart',
    '"entrar no grupo" whatsapp lançamento',
    '"grupo vip" whatsapp curso lançamento',
    '"acesse o grupo" whatsapp lançamento',
    '"comunidade whatsapp" lançamento curso',
    'site:hotmart.com "grupo whatsapp"',
    'site:kiwify.com.br "grupo whatsapp"',
    '"grupo exclusivo" whatsapp curso online',
    '"link do grupo" whatsapp lançamento',
]

# Plataformas conhecidas de produtos digitais brasileiros
LAUNCH_PLATFORMS = [
    'hotmart.com',
    'kiwify.com.br',
    'eduzz.com',
    'monetizze.com.br',
    'braip.com',
    'pepper.com.br',
    'payt.com.br',
]

WHATSAPP_PATTERN = re.compile(
    r'chat\.whatsapp\.com/[A-Za-z0-9]+|wa\.me/[0-9]+|whatsapp\.com/invite',
    re.IGNORECASE
)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def _has_whatsapp_signal_in_html(html: str) -> bool:
    """Verifica se o HTML contém padrões de link de grupo WhatsApp."""
    return bool(WHATSAPP_PATTERN.search(html))


def quick_verify_page(url: str, timeout: int = 12) -> Tuple[bool, str]:
    """
    Faz uma requisição rápida para verificar se a página contém
    links de grupos WhatsApp.

    Returns:
        (has_whatsapp, page_title)
    """
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        html = resp.text

        soup = BeautifulSoup(html, 'html.parser')
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()[:100]
        if not title:
            title = url

        has_wa = _has_whatsapp_signal_in_html(html)
        return has_wa, title
    except Exception:
        return False, url


def discover_pages(
    queries: Optional[List[str]] = None,
    max_results_per_query: int = 5,
    verify: bool = True,
    only_with_whatsapp: bool = True,
) -> List[Dict]:
    """
    Descobre páginas de lançamento usando buscas no DuckDuckGo.

    Args:
        queries: Lista de termos de busca. Se None, usa DEFAULT_QUERIES.
        max_results_per_query: Máximo de resultados por query.
        verify: Se True, acessa cada página para confirmar presença de WhatsApp.
        only_with_whatsapp: Se True, retorna apenas páginas com links WhatsApp confirmados.

    Returns:
        Lista de dicts: {url, name, has_whatsapp, verified}
    """
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            raise RuntimeError(
                "Biblioteca 'ddgs' não instalada. "
                "Execute: pip install ddgs"
            )

    if queries is None:
        queries = DEFAULT_QUERIES

    found: Dict[str, dict] = {}

    with DDGS() as ddgs:
        for query in queries:
            try:
                results = list(ddgs.text(query, max_results=max_results_per_query))
                for r in results:
                    url = r.get('href', '').strip()
                    title = r.get('title', url)[:100]

                    if not url or url in found:
                        continue

                    found[url] = {
                        'url': url,
                        'name': title,
                        'has_whatsapp': None,
                        'verified': False,
                        'query': query,
                    }
            except Exception:
                continue

    pages = list(found.values())

    if verify:
        for page in pages:
            has_wa, title = quick_verify_page(page['url'])
            page['has_whatsapp'] = has_wa
            page['verified'] = True
            if title and title != page['url']:
                page['name'] = title

    if only_with_whatsapp:
        pages = [p for p in pages if p.get('has_whatsapp') is True]

    return pages
