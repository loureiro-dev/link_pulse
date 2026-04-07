"""
Operações de banco de dados para links — Supabase PostgreSQL.
Substitui a implementação SQLite anterior.
"""

from datetime import datetime, timezone
from typing import List, Tuple, Optional
from backend.db.supabase_client import get_client


def init_db():
    """
    Verifica conexão com Supabase e cria usuário admin padrão se necessário.
    As tabelas já devem existir (criadas via SQL Editor no Supabase).
    """
    from backend.db.users import _ensure_admin_exists
    _ensure_admin_exists()


def save_links(links: List[str], source: str = "unknown", user_id: int = 1) -> None:
    """
    Salva links coletados no Supabase.
    Ignora duplicatas (mesmo url + user_id).
    """
    client = get_client()
    now = datetime.now(timezone.utc).isoformat()

    for link in links:
        try:
            client.table("links").insert({
                "url": link,
                "source": source,
                "found_at": now,
                "user_id": user_id,
            }).execute()
        except Exception:
            continue


def list_links(limit: int = 100, user_id: Optional[int] = None) -> List[Tuple[str, str, str]]:
    """
    Lista links do banco de dados.

    Returns:
        Lista de tuplas (url, source, found_at)
    """
    client = get_client()

    query = client.table("links").select("url, source, found_at")

    if user_id is not None:
        query = query.eq("user_id", user_id)

    result = query.order("id", desc=True).limit(limit).execute()

    return [(row["url"], row["source"], row["found_at"]) for row in result.data]
