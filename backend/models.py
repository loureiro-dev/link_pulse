"""
Modelos Pydantic para validação de dados da API
Centraliza todos os modelos para evitar importações circulares
"""

from pydantic import BaseModel
from typing import List, Optional

class LinkResponse(BaseModel):
    """Modelo de resposta para um link coletado"""
    url: str
    source: str
    found_at: str

class PageRequest(BaseModel):
    """Modelo de requisição para criar/atualizar uma página"""
    url: str
    name: str

class PageResponse(BaseModel):
    """Modelo de resposta para uma página cadastrada"""
    url: str
    name: str

class TelegramConfig(BaseModel):
    """Modelo para configuração do Telegram"""
    bot_token: str
    chat_id: str

class ScraperResponse(BaseModel):
    """Modelo de resposta da execução do scraper"""
    success: bool
    total_checked: int
    links_found: int
    links: List[dict]
    message: str

