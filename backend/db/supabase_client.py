"""
Cliente Supabase singleton para o backend.
Usa a service_role key para ter acesso completo (bypassa RLS).
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client() -> Client:
    """Retorna o cliente Supabase singleton. Inicializa apenas quando necessário."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL", "").strip()
        key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()
        
        if not url or not key:
            print("\n[ERRO CRÍTICO] SUPABASE_URL ou SUPABASE_SERVICE_KEY não configurados!")
            print("Configure estas variáveis no dashboard do Render/Vercel para que o banco de dados funcione.\n")
            # Em vez de crashar o servidor, vamos retornar um erro amigável ao tentar usar
            raise RuntimeError("Configuração do Supabase ausente. Verifique as Variáveis de Ambiente.")
            
        _client = create_client(url, key)
    return _client
