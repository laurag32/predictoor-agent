# telegram_notify.py
import os
import requests
import json
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send(msg: str, level: str = "info", data: dict | None = None):
    """Send formatted Telegram message with optional JSON payload"""
    if not BOT_TOKEN or not CHAT_ID:
        print("[Notify] Missing Telegram config.")
        return

    icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warn": "⚠️"}
    icon = icons.get(level, "📢")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    text = f"{icon} *Predictoor Agent*\n\n{msg}\n\n🕒 `{timestamp}`"
    if data:
        text += f"\n\n📊 Data:\n<pre>{json.dumps(data, indent=2)}</pre>"

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        print("[Notify] Message sent to Telegram successfully.")
    except Exception as e:
        print(f"[Notify] Telegram send failed: {e}")

if __name__ == "__main__":
    # Quick manual test
    send("Telegram notification system connected successfully.", "success")
