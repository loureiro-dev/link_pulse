"""
Rotas da API para configurações (Telegram)
Endpoints: /api/telegram/config, /api/telegram/save, /api/telegram/test
"""

from fastapi import APIRouter, HTTPException, Depends
import requests
from datetime import datetime
from backend.auth.middleware import get_current_user
from backend.main import TelegramConfig, load_config, save_config, write_log

router = APIRouter(prefix="/api/telegram", tags=["settings"])


@router.get("/config")
async def get_telegram_config(current_user: dict = Depends(get_current_user)):
    """Retorna a configuração atual do Telegram"""
    config = load_config()
    telegram_config = config.get("telegram", {})
    return {
        "bot_token": telegram_config.get("bot_token", ""),
        "chat_id": telegram_config.get("chat_id", ""),
        "configured": bool(telegram_config.get("bot_token") and telegram_config.get("chat_id"))
    }


@router.post("/save")
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


@router.post("/test")
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

