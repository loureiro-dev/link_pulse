import os
import google.generativeai as genai
from typing import Optional, Dict

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def analyze_page(self, title: str, content_snippet: str) -> Dict:
        """
        Analisa o conteúdo de uma página para identificar se é um lançamento,
        qual o nicho e qual o provável público.
        """
        if not self.model:
            return {"error": "Gemini API key not configured"}

        prompt = f"""
        Analise os dados desta página de destino (Landing Page):
        Título: {title}
        Conteúdo: {content_snippet}

        Responda em JSON com os seguintes campos:
        - is_launch (boolean): Se a página parece ser uma captura de leads para lançamento de produto digital.
        - niche (string): O nicho do produto (ex: Finanças, Marketing, Saúde, etc).
        - product_name (string): O nome do produto ou evento.
        - confidence (float): Nível de confiança da análise (0 a 1).
        - summary (string): Breve resumo do que se trata.

        Responda APENAS o JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extrair JSON da resposta (limpar blockquotes se houver)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            
            import json
            return json.loads(text)
        except Exception as e:
            return {"error": str(e)}

# Singleton instance
_instance = None

def get_gemini_service():
    global _instance
    if _instance is None:
        _instance = GeminiService()
    return _instance
