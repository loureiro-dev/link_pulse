"""
Link cleaning and normalization service
Handles WhatsApp link validation and normalization
"""

import re
from urllib.parse import urlparse, urljoin

def normalize_whatsapp_link(link: str) -> str:
    """
    Normalize and clean a WhatsApp link to canonical form
    
    Args:
        link: Raw link string
        
    Returns:
        Cleaned and normalized link
    """
    if not link:
        return link
    link = link.strip()
    # remove javascript: or window.location= prefixes
    link = re.sub(r"^javascript:|window\.location\.href\s*=\s*", "", link, flags=re.IGNORECASE)
    # extract actual http(s) link if text contains it
    m = re.search(r'(https?://[^\s\'\"]+)', link)
    if m:
        link = m.group(1)
    # remove URL fragments and trailing params that are not useful
    parsed = urlparse(link)
    clean = parsed._replace(fragment='').geturl()
    return clean

def is_group_link(link: str) -> bool:
    """
    Check if link is a WhatsApp group link
    
    Args:
        link: Link to check
        
    Returns:
        True if link is a WhatsApp group, False otherwise
    """
    link_l = (link or '').lower()
    if 'chat.whatsapp.com' in link_l:
        return True
    # api.whatsapp links that include 'text=' with words like 'grupo' are heuristics
    if 'api.whatsapp.com' in link_l and 'grupo' in link_l:
        return True
    return False

