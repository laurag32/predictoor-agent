# telegram_notify.py
import os
import requests
from datetime import datetime

def send_telegram_message(text: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        # Telegram not configured — log and return
        print("[telegram] TELEGRAM_TOKEN or TELEGRAM_CHAT_ID missing, skipping notification.")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code == 200:
            print("[telegram] Notification sent.")
            return True
        else:
            print(f"[telegram] Failed to send: {r.status_code} {r.text}")
            return False
    except Exception as e:
        print(f"[telegram] Exception sending message: {e}")
        return False
