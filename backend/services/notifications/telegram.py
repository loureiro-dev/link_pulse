"""
Telegram notification service
Sends formatted notifications to Telegram when new links are found
"""

import requests
from datetime import datetime
import os
from typing import Optional

# Note: These should be loaded from environment variables or config
# Keeping original structure for compatibility
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_message(link: str, source: str = "unknown", link_type: str = "group", is_relaunch: bool = False) -> bool:
    """
    Send formatted notification to Telegram with specialized alerts.
    """
    token = TELEGRAM_BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = TELEGRAM_CHAT_ID or os.getenv("TELEGRAM_CHAT_ID", "")
    
    if not token or not chat_id:
        print("Telegram não configurado — pulando envio.")
        return False

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Ícones e Avisos
    header = "🚀 *Novo grupo encontrado!*"
    warning = ""
    
    if is_relaunch:
        header = "🔄 *RELANÇAMENTO DETECTADO!*"
        warning += "\n⚠️ _Esta página já teve grupos antes. Um novo lançamento pode estar em andamento!_\n"
        
    if link_type == 'community':
        header = "📢 *COMUNIDADE DETECTADA!*"
        warning += "\n🚩 *AVISO:* Este link é de uma Comunidade WhatsApp, não de um grupo comum.\n"

    msg = (
        f"{header}\n\n"
        f"📌 *Campanha:* `{source}`\n"
        f"🔗 *Link:* {link}\n"
        f"📅 *Encontrado:* {timestamp}\n"
        f"{warning}\n"
        "Monitoramento LinkPulse IA ✔️"
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
        print(f"Mensagem enviada: {link}")
        return True
    except Exception as e:
        print("Erro ao enviar para Telegram:", e)
        return False


