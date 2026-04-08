from typing import Dict, Optional
from backend.services.ai.google_gemini import get_gemini_service
from backend.db.supabase_client import get_client

def classify_page(url: str, title: str, html_content: str) -> Dict:
    """
    Classifica uma página de destino usando IA com Cache no Supabase.
    """
    client = get_client()
    
    # 1. Verificar Cache
    try:
        cached = client.table("ai_cache").select("*").eq("url", url).execute()
        if cached.data:
            return cached.data[0]["analysis"]
    except Exception:
        # Tabela de cache pode não existir
        pass

    # 2. Se não estiver no cache, analisar com Gemini
    gemini = get_gemini_service()
    # Pega apenas os primeiros 2000 caracteres do HTML para economizar tokens
    snippet = html_content[:2000]
    
    analysis = gemini.analyze_page(title, snippet)
    
    # 3. Salvar no Cache (se a análise foi bem sucedida)
    if "error" not in analysis:
        try:
            client.table("ai_cache").insert({
                "url": url,
                "analysis": analysis
            }).execute()
        except Exception:
            pass
            
    return analysis

def is_valid_launch(analysis: Dict) -> bool:
    """
    Verifica se a análise da IA indica que é um lançamento válido.
    """
    return analysis.get("is_launch", False) and analysis.get("confidence", 0) > 0.6
