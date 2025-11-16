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

def send_message(link: str, source: str = "unknown") -> bool:
    """
    Send formatted notification to Telegram
    
    Args:
        link: WhatsApp link found
        source: Source/campaign name
        
    Returns:
        True if sent successfully, False otherwise
    """
    token = TELEGRAM_BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = TELEGRAM_CHAT_ID or os.getenv("TELEGRAM_CHAT_ID", "")
    
    if not token or not chat_id:
        print("Telegram não configurado — pulando envio.")
        return False

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    msg = (
        "🚀 *Novo grupo encontrado!*\n\n"
        f"📌 *Campanha:* `{source}`\n"
        f"🔗 *Link:* {link}\n"
        f"📅 *Encontrado:* {timestamp}\n\n"
        "Monitoramento ativo ✔️"
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


