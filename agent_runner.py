import os
import sys
import time
import json
import requests
from datetime import datetime
from telegram import Bot

# === LOAD INSTRUCTIONS ===
with open("agent_instructions.json", "r") as f:
    instructions = json.load(f)

FEEDS = instructions["feeds"]
PRED_INTERVAL = instructions["prediction_interval_minutes"]
FALLBACK_CONTRACT = instructions["fallback_predictoor"]
RELAYER_FALLBACK = instructions["gelato"]["fallback"]
CONTRACT_URLS = instructions["predictoor_contracts"]
RELAYER_URLS = instructions["gelato"]["relayer_urls"]

TELEGRAM_BOT_TOKEN = os.getenv(instructions["telegram"]["bot_token_env"])
TELEGRAM_CHAT_ID = os.getenv(instructions["telegram"]["chat_id_env"])
WALLET_PRIVATE_KEY = os.getenv(instructions["wallet"]["private_key_env"])
WALLET_ADDRESS = os.getenv(instructions["wallet"]["address_env"])

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# === TELEGRAM NOTIFY ===
def notify(msg):
    print(msg)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        except Exception as e:
            print(f"Telegram notify failed: {e}")

# === SAFE REQUEST ===
def safe_get(url, retries=3, delay=3):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.text
        except Exception as e:
            notify(f"Retry {i+1}/{retries} failed for {url}: {e}")
            time.sleep(delay)
    return None

# === GET PREDICTOOR CONTRACT ===
def get_predictoor_contract():
    for url in CONTRACT_URLS:
        text = safe_get(url)
        if text:
            try:
                data = json.loads(text)
                contract = data.get("sapphire-mainnet", {}).get("Predictoor")
                if contract:
                    notify(f"✅ Using Predictoor contract: {contract}")
                    return contract
            except Exception as e:
                notify(f"JSON parse failed for {url}: {e}")
    notify(f"⚠️ Using fallback Predictoor contract: {FALLBACK_CONTRACT}")
    return FALLBACK_CONTRACT

# === GET GELATO RELAYER ===
def get_gelato_relayer():
    for url in RELAYER_URLS:
        text = safe_get(url)
        if text:
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list) and len(parsed) > 0:
                    relayer = parsed[0].get("address") or RELAYER_FALLBACK
                    notify(f"✅ Selected Gelato relayer: {relayer}")
                    return relayer
            except Exception as e:
                notify(f"Relayer parse failed for {url}: {e}")
    notify(f"⚠️ Using fallback Gelato relayer: {RELAYER_FALLBACK}")
    return RELAYER_FALLBACK

# === AUTO RESTART ===
def auto_restart(reason=None):
    notify(f"⚠️ Agent restarting: {reason}")
    time.sleep(10)
    os.execv(sys.executable, ['python'] + sys.argv)

# === MAIN LOOP ===
def main():
    while True:
        try:
            contract = get_predictoor_contract()
            relayer = get_gelato_relayer()

            # Simulate submitting predictions
            timestamp = datetime.utcnow().isoformat()
            notify(f"[{timestamp}] Submitting predictions to {relayer} using {contract}")
            for feed in FEEDS:
                # Normally: call prediction API here
                notify(f"📊 Predicted feed: {feed}")

            # Save performance/log
            perf_file = instructions["logging"]["performance_file"]
            with open(perf_file, "a") as f:
                f.write(f"{timestamp} - Submitted predictions for {', '.join(FEEDS)}\n")

            time.sleep(PRED_INTERVAL * 60)

        except Exception as e:
            notify(f"❌ Unhandled error: {e}")
            auto_restart(str(e))

if __name__ == "__main__":
    notify("🚀 Starting Predictoor Agent...")
    main()
