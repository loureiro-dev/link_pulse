"""
Rotas de configuração de integrações.

  /api/telegram/*  → Bot Token + Chat ID
  /api/youtube/*   → YouTube Data API Key
"""

from fastapi import APIRouter, HTTPException, Depends
import requests
from datetime import datetime
from pydantic import BaseModel
try:
    from backend.auth.middleware import get_current_user
    from backend.models import TelegramConfig
    from backend.main import load_config, save_config, write_log
except ImportError:
    from auth.middleware import get_current_user
    from models import TelegramConfig
    from main import load_config, save_config, write_log

router = APIRouter(tags=["settings"])
router_telegram = APIRouter(tags=["settings"])
router_youtube = APIRouter(tags=["settings"])
router_ai = APIRouter(tags=["settings"])


# ─── TELEGRAM ─────────────────────────────────────────────────────────────────

@router_telegram.get("/config")
async def get_telegram_config(current_user: dict = Depends(get_current_user)):
    config = load_config()
    t = config.get("telegram", {})
    return {
        "bot_token": t.get("bot_token", ""),
        "chat_id": t.get("chat_id", ""),
        "configured": bool(t.get("bot_token") and t.get("chat_id")),
    }


@router_telegram.post("/save")
async def save_telegram_config(
    config: TelegramConfig,
    current_user: dict = Depends(get_current_user),
):
    try:
        current = load_config()
        current["telegram"] = {
            "bot_token": config.bot_token.strip(),
            "chat_id": config.chat_id.strip(),
        }
        if save_config(current):
            write_log("Configuração Telegram atualizada")
            return {"success": True, "message": "Configuração salva com sucesso"}
        raise HTTPException(status_code=500, detail="Erro ao salvar configuração")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_telegram.post("/set-webhook")
async def set_telegram_webhook(current_user: dict = Depends(get_current_user)):
    """
    Ativa o webhook do bot Telegram para receber URLs automaticamente.
    Quando ativo, qualquer URL enviada ao bot é coletada imediatamente.
    """
    import os
    config = load_config()
    token = config.get("telegram", {}).get("bot_token", "").strip()

    if not token:
        raise HTTPException(status_code=400, detail="Configure o bot Telegram primeiro.")

    backend_url = os.getenv("BACKEND_URL", "").strip().rstrip("/")
    if not backend_url:
        raise HTTPException(
            status_code=400,
            detail="BACKEND_URL não configurada. Adicione ao .env: BACKEND_URL=https://seu-backend.com"
        )

    webhook_url = f"{backend_url}/api/telegram/bot-webhook"
    api_url = f"https://api.telegram.org/bot{token}/setWebhook"

    try:
        resp = requests.post(api_url, json={"url": webhook_url, "allowed_updates": ["message"]}, timeout=10)
        data = resp.json()
        if data.get("ok"):
            write_log(f"Webhook Telegram ativado: {webhook_url}")
            return {"success": True, "message": f"Webhook ativado! Bot pronto para receber URLs.", "webhook_url": webhook_url}
        raise HTTPException(status_code=400, detail=data.get("description", "Erro ao ativar webhook"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_telegram.delete("/set-webhook")
async def remove_telegram_webhook(current_user: dict = Depends(get_current_user)):
    """Remove o webhook do bot Telegram."""
    config = load_config()
    token = config.get("telegram", {}).get("bot_token", "").strip()
    if not token:
        raise HTTPException(status_code=400, detail="Bot Telegram não configurado.")
    try:
        resp = requests.post(f"https://api.telegram.org/bot{token}/deleteWebhook", timeout=10)
        if resp.json().get("ok"):
            return {"success": True, "message": "Webhook removido com sucesso"}
        raise HTTPException(status_code=400, detail="Erro ao remover webhook")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_telegram.post("/test")
async def test_telegram(current_user: dict = Depends(get_current_user)):
    config = load_config()
    token = config.get("telegram", {}).get("bot_token", "").strip()
    chat_id = config.get("telegram", {}).get("chat_id", "").strip()

    if not token or not chat_id:
        raise HTTPException(status_code=400, detail="Telegram não configurado")

    msg = (
        "*TESTE DE NOTIFICAÇÃO*\n\n"
        f"Telegram configurado corretamente!\n\n"
        f"*Data/Hora:* {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n*LinkPulse — Sistema ativo!*"
    )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        write_log("Teste de Telegram enviado")
        return {"success": True, "message": "Mensagem de teste enviada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar teste: {str(e)}")


# ─── YOUTUBE ──────────────────────────────────────────────────────────────────

class YoutubeApiKeyConfig(BaseModel):
    api_key: str


@router_youtube.get("/config")
async def get_youtube_config(current_user: dict = Depends(get_current_user)):
    config = load_config()
    key = config.get("youtube", {}).get("api_key", "")
    return {
        "api_key": key[:8] + "..." if len(key) > 8 else key,
        "configured": bool(key),
    }


@router_youtube.post("/save")
async def save_youtube_config(
    data: YoutubeApiKeyConfig,
    current_user: dict = Depends(get_current_user),
):
    try:
        config = load_config()
        config["youtube"] = {"api_key": data.api_key.strip()}
        if save_config(config):
            write_log("Chave YouTube API salva")
            return {"success": True, "message": "Chave salva com sucesso"}
        raise HTTPException(status_code=500, detail="Erro ao salvar")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_youtube.post("/validate")
async def validate_youtube_key(current_user: dict = Depends(get_current_user)):
    try:
        from backend.services.discovery.youtube_discovery import validate_api_key
    except ImportError:
        from services.discovery.youtube_discovery import validate_api_key

    config = load_config()
    key = config.get("youtube", {}).get("api_key", "").strip()

    if not key:
        raise HTTPException(status_code=400, detail="Chave da YouTube API não configurada")

    result = validate_api_key(key)
    if not result["valid"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {"success": True, "message": result["message"]}


# ─── AI / GEMINI ──────────────────────────────────────────────────────────────

class AiSaveRequest(BaseModel):
    api_key: str
    provider: str = "gemini"
    min_confidence: float = 0.6
    enabled: bool = True

@router_ai.get("/config")
async def get_ai_config(current_user: dict = Depends(get_current_user)):
    config = load_config()
    ai = config.get("ai", {})
    key = ai.get("api_key", "")
    return {
        "configured": bool(key),
        "enabled": ai.get("enabled", True),
        "provider": ai.get("provider", "gemini"),
        "min_confidence": ai.get("min_confidence", 0.6),
        "api_key_preview": key[:6] + "..." if len(key) > 6 else key
    }

@router_ai.post("/save")
async def save_ai_config(
    data: AiSaveRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        config = load_config()
        config["ai"] = {
            "api_key": data.api_key.strip(),
            "provider": data.provider,
            "min_confidence": data.min_confidence,
            "enabled": data.enabled
        }
        if save_config(config):
            write_log(f"Configuração AI atualizada (user {current_user['id']})")
            return {"success": True, "message": "Configurações de IA salvas com sucesso"}
        raise HTTPException(status_code=500, detail="Erro ao salvar")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router_ai.post("/validate")
async def validate_ai_key(current_user: dict = Depends(get_current_user)):
    try:
        from backend.services.ai.google_gemini import GeminiService
    except ImportError:
        from services.ai.google_gemini import GeminiService
    
    config = load_config()
    ai_cfg = config.get("ai", {})
    key = ai_cfg.get("api_key", "").strip()
    
    if not key:
        raise HTTPException(status_code=400, detail="Chave AI não configurada")
    
    # Simples teste de conexão
    try:
        service = GeminiService(api_key=key)
        # Tenta uma resposta mínima
        response = service.model.generate_content("hello")
        if response.text:
            return {"success": True, "message": "Chave Gemini validada com sucesso!"}
        return {"success": False, "message": "Sem resposta da API"}
    except Exception as e:
        return {"success": False, "message": f"Erro de validação: {str(e)}"}

# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

def _get_ai_config(user_id: int):
    """Retorna configuração de IA (para uso interno)"""
    config = load_config()
    ai = config.get("ai", {})
    return {
        "api_key": ai.get("api_key", ""),
        "provider": ai.get("provider", "gemini"),
        "min_confidence": ai.get("min_confidence", 0.6),
        "enabled": ai.get("enabled", True)
    }
