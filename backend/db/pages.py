"""
Operações de páginas — Supabase PostgreSQL.
Substitui a implementação SQLite anterior.
"""

from typing import List
from backend.db.supabase_client import get_client


import json
import os

# Caminho para fallback local
LOCAL_PAGES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "pages.json")

def _load_local_pages() -> List[dict]:
    if not os.path.exists(LOCAL_PAGES_FILE):
        return []
    try:
        with open(LOCAL_PAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_local_pages(pages: List[dict]) -> None:
    os.makedirs(os.path.dirname(LOCAL_PAGES_FILE), exist_ok=True)
    try:
        with open(LOCAL_PAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(pages, f, indent=4, ensure_ascii=True)
    except Exception:
        pass

def init_pages_table():
    """Compatibilidade: no Supabase a tabela é criada via SQL Editor."""
    pass


def load_pages(user_id: int) -> List[dict]:
    """Carrega as páginas de um usuário."""
    client = get_client()
    if client is None:
        return _load_local_pages()
        
    try:
        result = client.table("pages").select("url, name").eq("user_id", user_id).order("id").execute()
        return [{"url": row["url"], "name": row["name"]} for row in result.data]
    except Exception:
        return _load_local_pages()


def add_page(url: str, name: str, user_id: int) -> bool:
    """Adiciona uma página para o usuário."""
    client = get_client()
    if client is None:
        pages = _load_local_pages()
        if any(p["url"] == url for p in pages):
            return False
        pages.append({"url": url, "name": name})
        _save_local_pages(pages)
        return True

    try:
        client.table("pages").insert({
            "url": url,
            "name": name,
            "user_id": user_id,
        }).execute()
        return True
    except Exception:
        # Fallback local em caso de erro no Supabase
        pages = _load_local_pages()
        if not any(p["url"] == url for p in pages):
            pages.append({"url": url, "name": name})
            _save_local_pages(pages)
        return False


def delete_page(url: str, user_id: int) -> bool:
    """Remove uma página do usuário."""
    client = get_client()
    if client is None:
        pages = _load_local_pages()
        new_pages = [p for p in pages if p["url"] != url]
        if len(new_pages) < len(pages):
            _save_local_pages(new_pages)
            return True
        return False

    try:
        result = client.table("pages").delete().eq("url", url).eq("user_id", user_id).execute()
        return bool(result.data)
    except Exception:
        return False
