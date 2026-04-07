"""
Cliente Supabase singleton para o backend.
Usa a service_role key para ter acesso completo (bypassa RLS).
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_URL e SUPABASE_SERVICE_KEY precisam estar definidos no .env"
    )

_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_client() -> Client:
    """Retorna o cliente Supabase singleton."""
    return _client
