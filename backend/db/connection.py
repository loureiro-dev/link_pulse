"""
Operações de banco de dados para links — Supabase PostgreSQL.
Substitui a implementação SQLite anterior.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Tuple, Optional
from backend.db.supabase_client import get_client


import json
import os

# Caminho para fallback local
LOCAL_LINKS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "links.json")

def _load_local_links() -> List[dict]:
    if not os.path.exists(LOCAL_LINKS_FILE):
        return []
    try:
        with open(LOCAL_LINKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_local_links(links: List[dict]) -> None:
    os.makedirs(os.path.dirname(LOCAL_LINKS_FILE), exist_ok=True)
    try:
        # Mantém apenas os últimos 500 links no modo local para não sobrecarregar
        to_save = links[-500:]
        with open(LOCAL_LINKS_FILE, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=4, ensure_ascii=True)
    except Exception:
        pass

def init_db():
    """
    Verifica conexão com Supabase e cria usuário admin padrão se necessário.
    """
    client = get_client()
    if client:
        try:
            from backend.db.users import _ensure_admin_exists
            _ensure_admin_exists()
        except Exception as e:
            print(f"\n[AVISO] Erro ao inicializar admin no Supabase: {e}")
    else:
        print("💡 [DB] Sistema operando em MODO LOCAL (SQLite desativado, usando JSON).")


def save_links(links: List[str], source: str = "unknown", user_id: int = 1) -> None:
    """
    Salva links coletados. Fallback para JSON se Supabase offline.
    """
    client = get_client()
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    if client is None:
        local_links = _load_local_links()
        for link in links:
            if not any(l["url"] == link for l in local_links):
                local_links.append({
                    "url": link,
                    "source": source,
                    "found_at": now_iso,
                    "link_type": 'community' if '/community/' in link.lower() else 'group',
                    "is_relaunch": False
                })
        _save_local_links(local_links)
        return

    # Lógica Supabase
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
    except Exception:
        pass

    for link in links:
        try:
            link_type = 'community' if '/community/' in link.lower() else 'group'
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
    Lista links. Fallback para JSON se Supabase offline.
    """
    client = get_client()
    if client is None:
        local_links = _load_local_links()
        # Inverte e limita
        results = local_links[::-1][:limit]
        return [(l["url"], l["source"], l["found_at"]) for l in results]

    try:
        query = client.table("links").select("url, source, found_at")
        if user_id is not None:
            query = query.eq("user_id", user_id)
        result = query.order("id", desc=True).limit(limit).execute()
        return [(row["url"], row["source"], row["found_at"]) for row in result.data]
    except Exception:
        # Fallback local em caso de erro na query
        local_links = _load_local_links()
        results = local_links[::-1][:limit]
        return [(l["url"], l["source"], l["found_at"]) for l in results]


def delete_link(url: str, user_id: int) -> bool:
    """Deleta um link."""
    client = get_client()
    if client is None:
        links = _load_local_links()
        new_links = [l for l in links if l["url"] != url]
        if len(new_links) < len(links):
            _save_local_links(new_links)
            return True
        return False

    try:
        res = client.table("links").delete().eq("user_id", user_id).eq("url", url).execute()
        return bool(res.data)
    except Exception:
        return False


def delete_all_links(user_id: int) -> bool:
    """Deleta todos os links."""
    client = get_client()
    if client is None:
        _save_local_links([])
        return True

    try:
        client.table("links").delete().eq("user_id", user_id).execute()
        return True
    except Exception:
        return False
