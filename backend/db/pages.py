"""
Operações de páginas — Supabase PostgreSQL.
Substitui a implementação SQLite anterior.
"""

from typing import List
from backend.db.supabase_client import get_client


def init_pages_table():
    """Compatibilidade: no Supabase a tabela é criada via SQL Editor."""
    pass


def load_pages(user_id: int) -> List[dict]:
    """Carrega as páginas de um usuário."""
    client = get_client()
    result = client.table("pages").select("url, name").eq("user_id", user_id).order("id").execute()
    return [{"url": row["url"], "name": row["name"]} for row in result.data]


def save_pages(pages: List[dict], user_id: int) -> None:
    """
    Substitui todas as páginas do usuário.
    Remove as existentes e insere as novas.
    """
    client = get_client()
    client.table("pages").delete().eq("user_id", user_id).execute()

    for page in pages:
        try:
            client.table("pages").insert({
                "url": page.get("url", ""),
                "name": page.get("name", ""),
                "user_id": user_id,
            }).execute()
        except Exception:
            continue


def add_page(url: str, name: str, user_id: int) -> bool:
    """
    Adiciona uma página para o usuário.

    Returns:
        True se adicionada, False se já existia.
    """
    client = get_client()
    try:
        client.table("pages").insert({
            "url": url,
            "name": name,
            "user_id": user_id,
        }).execute()
        return True
    except Exception:
        return False


def delete_page(url: str, user_id: int) -> bool:
    """Remove uma página do usuário."""
    client = get_client()
    try:
        result = client.table("pages").delete().eq("url", url).eq("user_id", user_id).execute()
        return bool(result.data)
    except Exception:
        return False
