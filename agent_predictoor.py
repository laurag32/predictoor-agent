import os
import json
import time
import requests
from datetime import datetime
from web3 import Web3
from telegram import Bot

# === Load config ===
with open("agent_instructions.json", "r") as f:
    cfg = json.load(f)

FEEDS = cfg["feeds"]
INTERVAL = cfg["predictor"]["interval_seconds"]
CONF_THRESHOLD = cfg["predictor"]["confidence_threshold"]

# Wallet & Gelato
WALLET_PRIVATE_KEY = os.getenv(cfg["wallet"]["private_key_env"])
WALLET_ADDRESS = os.getenv(cfg["wallet"]["address_env"])
PREDICTOOR_API = os.getenv(cfg["predictor"]["api_endpoint_env"])
GELATO_API_KEY = os.getenv(cfg["gelato"]["api_key_env"])
GELATO_RELAYER = os.getenv(cfg["gelato"]["relayer_env"])

# Telegram
bot = Bot(token=os.getenv(cfg["telegram"]["bot_token_env"]))
CHAT_ID = os.getenv(cfg["telegram"]["chat_id_env"])

# Logging
PERF_FILE = cfg["logging"]["performance_file"]
ERROR_FILE = cfg["logging"]["error_file"]

# === Functions ===
def notify(msg):
    print(msg)
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print(f"Telegram notify failed: {e}")

def send_prediction(feed):
    """
    Submits prediction payload to Predictoor API via Gelato relayer
    """
    payload = {
        "feed": feed,
        "confidence": CONF_THRESHOLD,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        # Send to Predictoor API (simulate mainnet gasless)
        headers = {"Authorization": f"Bearer {PREDICTOOR_API}"}
        resp = requests.post(PREDICTOOR_API, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()

        # Log performance
        with open(PERF_FILE, "a") as f:
            f.write(f"{datetime.utcnow().isoformat()} - Submitted {feed} - {resp.text}\n")

        notify(f"✅ Prediction sent for {feed} | Response: {resp.status_code}")

    except Exception as e:
        with open(ERROR_FILE, "a") as f:
            f.write(f"{datetime.utcnow().isoformat()} - ERROR {feed}: {e}\n")
        notify(f"❌ Error sending prediction for {feed}: {e}")

# === Main loop ===
def main():
    while True:
        try:
            for feed in FEEDS:
                send_prediction(feed)

            notify(f"Sleeping for {INTERVAL} seconds until next predictions...")
            time.sleep(INTERVAL)

        except Exception as e:
            notify(f"❌ Unhandled error in main loop: {e}")
            time.sleep(30)  # small retry delay

# === Entrypoint ===
if __name__ == "__main__":
    notify("🚀 Predictoor Agent started")
    main()
