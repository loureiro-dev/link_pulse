import requests
from datetime import datetime
import os

TELEGRAM_BOT_TOKEN = os.getenv("8092102779:AAE-4GFgxheLkcXcbmC3-KlNRIH4jzGdl0c)
TELEGRAM_CHAT_ID = os.getenv("954773903")

def send_message(link, source):
    """Envia notificação formatada para o Telegram"""

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram não configurado — pulando envio.")
        return

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    msg = (
        "🚀 *Novo grupo encontrado!*\n\n"
        f"📌 *Campanha:* `{source}`\n"
        f"🔗 *Link:* {link}\n"
        f"📅 *Encontrado:* {timestamp}\n\n"
        "Monitoramento ativo ✔️"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, json=payload)
        print(f"Mensagem enviada: {link}")
    except Exception as e:
        print("Erro ao enviar para Telegram:", e)
