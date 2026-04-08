"""
Operações de banco de dados para links — Supabase PostgreSQL.
Substitui a implementação SQLite anterior.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Tuple, Optional
from backend.db.supabase_client import get_client


def init_db():
    """
    Verifica conexão com Supabase e cria usuário admin padrão se necessário.
    As tabelas já devem existir (criadas via SQL Editor no Supabase).
    """
    try:
        from backend.db.users import _ensure_admin_exists
        _ensure_admin_exists()
    except Exception as e:
        print(f"\n[AVISO] Não foi possível inicializar o banco de dados (admin): {e}")
        print("Isso geralmente ocorre se as variáveis do Supabase não estiverem configuradas.\n")


def save_links(links: List[str], source: str = "unknown", user_id: int = 1) -> None:
    """
    Salva links coletados no Supabase com lógica de IA (Relançamento / Comunidade).
    Ignora duplicatas (mesmo url + user_id).
    """
    client = get_client()
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    # Lógica de Relançamento: verifica se já existem links para esta fonte há mais de 3 dias
    is_relaunch = False
    try:
        three_days_ago = (now - timedelta(days=3)).isoformat()
        old_links = client.table("links") \
            .select("id") \
            .eq("source", source) \
            .lt("found_at", three_days_ago) \
            .limit(1) \
            .execute()
        
        if old_links.data:
            is_relaunch = True
    except Exception as e:
        print(f"Erro ao verificar relançamento: {e}")

    for link in links:
        try:
            # Identificação de Tipo (Comunidade vs Grupo)
            link_type = 'group'
            if '/community/' in link.lower():
                link_type = 'community'

            client.table("links").insert({
                "url": link,
                "source": source,
                "found_at": now_iso,
                "user_id": user_id,
                "link_type": link_type,
                "is_relaunch": is_relaunch,
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


def delete_link(url: str, user_id: int) -> bool:
    """Deleta um link específico do usuário no Supabase."""
    client = get_client()
    try:
        res = client.table("links").delete().eq("user_id", user_id).eq("url", url).execute()
        return len(res.data) > 0 if res.data else False
    except Exception:
        return False


def delete_all_links(user_id: int) -> bool:
    """Deleta todos os links coletados de um usuário."""
    client = get_client()
    try:
        res = client.table("links").delete().eq("user_id", user_id).execute()
        return True
    except Exception:
        return False
