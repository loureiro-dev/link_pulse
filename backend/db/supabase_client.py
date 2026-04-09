import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_client = None

def get_client() -> Optional[Client]:
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        # Support both naming conventions
        key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            print("⚠️ [DB] SUPABASE_URL ou SUPABASE_KEY não configurados. Usando modo de fallback local.")
            return None
            
        try:
            _client = create_client(url, key)
        except Exception as e:
            print(f"❌ [DB] Erro ao conectar ao Supabase: {e}")
            return None
    return _client
