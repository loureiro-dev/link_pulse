import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_client = None

def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidos nas variáveis de ambiente.")
        _client = create_client(url, key)
    return _client
