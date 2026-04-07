"""
Rotas da API para configurações (Telegram e Facebook Ad Library)
Endpoints: /api/telegram/*, /api/facebook/*
"""

from fastapi import APIRouter, HTTPException, Depends
import requests
from datetime import datetime
from pydantic import BaseModel
from backend.auth.middleware import get_current_user
from backend.models import TelegramConfig
from backend.main import load_config, save_config, write_log

router = APIRouter(tags=["settings"])


# ─── FACEBOOK AD LIBRARY CONFIG ───────────────────────────────────────────────

class FacebookConfig(BaseModel):
    access_token: str


@router.get("/api/facebook/config")
async def get_facebook_config(current_user: dict = Depends(get_current_user)):
    """Retorna se o token do Facebook Ad Library está configurado"""
    config = load_config()
    fb_token = config.get("facebook", {}).get("access_token", "")
    return {
        "access_token": fb_token[:8] + "..." if len(fb_token) > 8 else fb_token,
        "configured": bool(fb_token),
    }


@router.post("/api/facebook/save")
async def save_facebook_config(
    data: FacebookConfig,
    current_user: dict = Depends(get_current_user),
):
    """Salva o token do Facebook Ad Library"""
    try:
        config = load_config()
        config["facebook"] = {"access_token": data.access_token.strip()}
        if save_config(config):
            write_log("Token Facebook Ad Library salvo")
            return {"success": True, "message": "Token salvo com sucesso"}
        raise HTTPException(status_code=500, detail="Erro ao salvar configuração")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/facebook/validate")
async def validate_facebook_token(current_user: dict = Depends(get_current_user)):
    """Valida se o token salvo tem acesso à Ad Library API"""
    from backend.services.discovery.facebook_ads_discovery import validate_token

    config = load_config()
    token = config.get("facebook", {}).get("access_token", "").strip()

    if not token:
        raise HTTPException(status_code=400, detail="Token do Facebook não configurado")

    result = validate_token(token)
    if not result["valid"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {"success": True, "message": result["message"]}


# ─── TELEGRAM CONFIG ──────────────────────────────────────────────────────────

router_telegram = APIRouter(prefix="/api/telegram", tags=["settings"])


@router_telegram.get("/config")
async def get_telegram_config(current_user: dict = Depends(get_current_user)):
    """Retorna a configuração atual do Telegram"""
    config = load_config()
    telegram_config = config.get("telegram", {})
    return {
        "bot_token": telegram_config.get("bot_token", ""),
        "chat_id": telegram_config.get("chat_id", ""),
        "configured": bool(telegram_config.get("bot_token") and telegram_config.get("chat_id"))
    }


@router_telegram.post("/save")
async def save_telegram_config(config: TelegramConfig, current_user: dict = Depends(get_current_user)):
    """Salva a configuração do Telegram"""
    try:
        current_config = load_config()
        current_config["telegram"] = {
            "bot_token": config.bot_token.strip(),
            "chat_id": config.chat_id.strip()
        }
        
        if save_config(current_config):
            write_log("Configuração Telegram atualizada")
            return {"success": True, "message": "Configuração salva com sucesso"}
        else:
            raise HTTPException(status_code=500, detail="Erro ao salvar configuração")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar: {str(e)}")


@router_telegram.post("/test")
async def test_telegram(current_user: dict = Depends(get_current_user)):
    """Envia uma mensagem de teste para o Telegram"""
    config = load_config()
    token = config.get("telegram", {}).get("bot_token", "").strip()
    chat_id = config.get("telegram", {}).get("chat_id", "").strip()
    
    if not token or not chat_id:
        raise HTTPException(status_code=400, detail="Telegram não configurado")
    
    msg = (
        "*TESTE DE NOTIFICAÇÃO*\n\n"
        f"Se você recebeu esta mensagem, o Telegram está configurado corretamente!\n\n"
        f"*Data/Hora:* {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "*Sistema operacional!*"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        write_log("Teste de Telegram enviado com sucesso")
        return {"success": True, "message": "Mensagem de teste enviada com sucesso!"}
    except Exception as e:
        write_log(f"Erro no teste de Telegram: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar teste: {str(e)}")


