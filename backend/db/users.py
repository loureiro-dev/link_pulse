"""
Operações de usuários — Supabase PostgreSQL.
Substitui a implementação SQLite anterior.
"""

from typing import Optional, Tuple
from backend.db.supabase_client import get_client
from backend.auth.jwt import get_password_hash, verify_password


def _ensure_admin_exists() -> None:
    """Cria usuário admin padrão se não existir nenhum usuário."""
    client = get_client()
    result = client.table("users").select("id").limit(1).execute()

    if not result.data:
        admin_password = get_password_hash("admin123")
        client.table("users").insert({
            "email": "admin@linkpulse.com",
            "hashed_password": admin_password,
            "name": "Administrador",
            "is_admin": True,
            "approved": True,
        }).execute()


def init_users_table():
    """Compatibilidade: verifica conexão e garante admin padrão."""
    _ensure_admin_exists()


def create_user(
    email: str,
    password: str,
    name: Optional[str] = None,
    is_admin: bool = False,
    approved: bool = False,
) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Cria um novo usuário.

    Returns:
        (success, user_id, error_message)
    """
    client = get_client()

    existing = client.table("users").select("id").eq("email", email.lower()).execute()
    if existing.data:
        return False, None, "Email already registered"

    try:
        hashed_password = get_password_hash(password)
        result = client.table("users").insert({
            "email": email.lower(),
            "hashed_password": hashed_password,
            "name": name,
            "is_admin": is_admin,
            "approved": approved,
        }).execute()

        user_id = result.data[0]["id"] if result.data else None
        return True, user_id, None
    except Exception as e:
        return False, None, f"Error creating user: {str(e)}"


def get_user_by_email(email: str) -> Optional[dict]:
    """Busca usuário pelo email."""
    client = get_client()
    result = client.table("users").select(
        "id, email, hashed_password, name, is_admin, approved"
    ).eq("email", email.lower()).execute()

    if result.data:
        row = result.data[0]
        return {
            "id": row["id"],
            "email": row["email"],
            "hashed_password": row["hashed_password"],
            "name": row.get("name"),
            "is_admin": bool(row.get("is_admin", False)),
            "approved": bool(row.get("approved", False)),
        }
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Busca usuário pelo ID."""
    client = get_client()
    result = client.table("users").select(
        "id, email, name, is_admin, approved"
    ).eq("id", user_id).execute()

    if result.data:
        row = result.data[0]
        return {
            "id": row["id"],
            "email": row["email"],
            "name": row.get("name"),
            "is_admin": bool(row.get("is_admin", False)),
            "approved": bool(row.get("approved", False)),
        }
    return None


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Autentica usuário com email e senha."""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "is_admin": user.get("is_admin", False),
        "approved": user.get("approved", False),
    }


def list_all_users(include_pending: bool = True) -> list:
    """Lista todos os usuários."""
    client = get_client()

    query = client.table("users").select(
        "id, email, name, is_admin, approved, created_at"
    ).order("created_at", desc=True)

    if not include_pending:
        query = query.eq("approved", True)

    result = query.execute()

    return [
        {
            "id": row["id"],
            "email": row["email"],
            "name": row.get("name"),
            "is_admin": bool(row.get("is_admin", False)),
            "approved": bool(row.get("approved", False)),
            "created_at": row.get("created_at"),
        }
        for row in result.data
    ]


def approve_user(user_id: int) -> bool:
    """Aprova um usuário."""
    client = get_client()
    try:
        result = client.table("users").update({"approved": True}).eq("id", user_id).execute()
        return bool(result.data)
    except Exception:
        return False


def reject_user(user_id: int) -> bool:
    """Remove um usuário."""
    client = get_client()
    try:
        result = client.table("users").delete().eq("id", user_id).execute()
        return bool(result.data)
    except Exception:
        return False


def update_user_profile(
    user_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
) -> bool:
    """Atualiza perfil do usuário."""
    client = get_client()
    updates = {}

    if name is not None:
        updates["name"] = name

    if email is not None:
        existing = client.table("users").select("id").eq("email", email.lower()).execute()
        if existing.data and existing.data[0]["id"] != user_id:
            return False
        updates["email"] = email.lower()

    if not updates:
        return False

    try:
        result = client.table("users").update(updates).eq("id", user_id).execute()
        return bool(result.data)
    except Exception:
        return False


def update_user_password(user_id: int, new_password: str) -> bool:
    """Atualiza senha do usuário."""
    client = get_client()
    try:
        hashed = get_password_hash(new_password)
        result = client.table("users").update({"hashed_password": hashed}).eq("id", user_id).execute()
        return bool(result.data)
    except Exception:
        return False


def is_admin(user_id: int) -> bool:
    """Verifica se o usuário é admin."""
    user = get_user_by_id(user_id)
    return user.get("is_admin", False) if user else False
