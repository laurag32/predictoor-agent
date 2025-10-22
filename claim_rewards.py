import os
import json
import time
import requests
from datetime import datetime
from telegram import Bot

# === Load config ===
with open("agent_instructions.json", "r") as f:
    cfg = json.load(f)

# Wallet & Predictoor
WALLET_ADDRESS = os.getenv(cfg["wallet"]["address_env"])
WALLET_PRIVATE_KEY = os.getenv(cfg["wallet"]["private_key_env"])
PREDICTOOR_API = os.getenv(cfg["predictor"]["api_endpoint_env"])

# Telegram
bot = Bot(token=os.getenv(cfg["telegram"]["bot_token_env"]))
CHAT_ID = os.getenv(cfg["telegram"]["chat_id_env"])

# Logging
CLAIM_FILE = cfg["logging"]["claim_file"]
ERROR_FILE = cfg["logging"]["error_file"]

# === Functions ===
def notify(msg):
    print(msg)
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print(f"Telegram notify failed: {e}")

def claim_rewards():
    """
    Claims rewards from Predictoor mainnet for your wallet
    """
    payload = {"wallet": WALLET_ADDRESS}

    try:
        headers = {"Authorization": f"Bearer {PREDICTOOR_API}"}
        resp = requests.post(f"{PREDICTOOR_API}/claim", json=payload, headers=headers, timeout=10)
        resp.raise_for_status()

        result = resp.json()
        with open(CLAIM_FILE, "a") as f:
            f.write(f"{datetime.utcnow().isoformat()} - Claimed rewards: {result}\n")

        notify(f"✅ Claimed rewards successfully: {result}")

    except Exception as e:
        with open(ERROR_FILE, "a") as f:
            f.write(f"{datetime.utcnow().isoformat()} - ERROR claiming rewards: {e}\n")
        notify(f"❌ Error claiming rewards: {e}")

# === Main loop ===
def main():
    while True:
        try:
            notify("🚀 Starting reward claim cycle")
            claim_rewards()
            # Claim every 4 hours by default
            interval = cfg["predictor"].get("claim_interval_seconds", 14400)
            notify(f"Sleeping for {interval} seconds until next claim...")
            time.sleep(interval)

        except Exception as e:
            notify(f"❌ Unhandled error in claim loop: {e}")
            time.sleep(30)  # retry after small delay

# === Entrypoint ===
if __name__ == "__main__":
    main()
