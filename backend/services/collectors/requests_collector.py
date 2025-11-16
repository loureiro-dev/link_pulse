"""
Requests-based collector for scraping WhatsApp links from pages
Uses requests library with BeautifulSoup for HTML parsing
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from typing import List, Tuple

USER_AGENT = "Mozilla/5.0 (compatible; LinkMonitor/1.0)"

def fetch_html(url: str, timeout: int = 15) -> Tuple[str, str]:
    """Fetch HTML from URL and return (final_url, html)"""
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.url, resp.text

def extract_whatsapp_links_from_html(html: str) -> List[str]:
    """Extract WhatsApp links from HTML content"""
    soup = BeautifulSoup(html, 'html.parser')
    links = set()

    # anchor tags
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if 'whatsapp' in href.lower():
            links.add(href)

    # onclicks / scripts
    for tag in soup.find_all(onclick=True):
        onclick = tag['onclick']
        matches = re.findall(r'(https?://[^\s\'\"]+)', onclick)
        for m in matches:
            if 'whatsapp' in m.lower():
                links.add(m)

    for script in soup.find_all('script'):
        s = script.string or ""
        matches = re.findall(r'(https?://[^\s\'\"]*whatsapp[^\s\'\"]*)', s, re.IGNORECASE)
        for m in matches:
            links.add(m)

    return list(links)

def collect_from_page(url: str) -> Tuple[List[str], bool, bool]:
    """
    Collect WhatsApp links from a page
    
    Args:
        url: URL to scrape
        
    Returns:
        Tuple of (links, has_form, is_thank_you)
    """
    try:
        final, html = fetch_html(url)
    except Exception:
        return [], False, False

    soup = BeautifulSoup(html, 'html.parser')

    # simple heuristics
    has_form = bool(soup.find('form'))
    is_thanks = any(kw in final.lower() for kw in ['obrigado', 'thank', 'success', 'confirmacao'])

    links = extract_whatsapp_links_from_html(html)
    return links, has_form, is_thanks

