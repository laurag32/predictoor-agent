import os
import json
import time
import requests
from datetime import datetime
from telegram import Bot

# === Load Agent Config ===
AGENT_JSON = "agent_instructions.json"

def load_agent_config():
    with open(AGENT_JSON, "r") as f:
        return json.load(f)

agent_config = load_agent_config()

# === Telegram Setup ===
telegram_bot = Bot(token=agent_config["telegram"]["bot_token"])
CHAT_ID = agent_config["telegram"]["chat_id"]

def notify(msg: str):
    print(msg)
    try:
        telegram_bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print(f"[WARN] Telegram notify failed: {e}")

# === Wallet & Gelato ===
WALLET_ADDRESS = agent_config["wallet"]["address"]
GELATO_RELAYER = agent_config["gelato"].get("relayer")
PREDICTOR_API = agent_config["predictor"]["api_endpoint"]

# === Logging Files ===
PERF_FILE = agent_config["logging"]["performance_file"]
ERROR_FILE = agent_config["logging"]["error_file"]

# === Safe POST ===
def safe_post(url, payload, retries=3, delay=5):
    for i in range(retries):
        try:
            r = requests.post(url, json=payload, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            notify(f"Retry {i+1}/{retries} failed for {url}: {e}")
            time.sleep(delay)
    return None

# === Adjust Accuracy Logic ===
def adjust_prediction_confidence(feed):
    """Simple example: slightly adjust confidence up or down randomly."""
    import random
    current_conf = feed.get("confidence", 0.7)
    change = random.uniform(-0.05, 0.05)
    new_conf = min(max(current_conf + change, 0.5), 0.95)
    feed["confidence"] = round(new_conf, 2)
    return feed

def submit_adjusted_feed(feed):
    payload = {
        "feed": feed["name"],
        "confidence": feed["confidence"],
        "wallet": WALLET_ADDRESS,
        "timestamp": datetime.utcnow().isoformat()
    }
    if GELATO_RELAYER:
        response = safe_post(GELATO_RELAYER, payload)
        if response:
            notify(f"✅ Submitted adjusted confidence for {feed['name']}: {feed['confidence']}")
        else:
            notify(f"❌ Failed to submit adjusted confidence for {feed['name']}")
    else:
        notify("❌ Gelato relayer unavailable. Skipping submission.")

# === Main Loop ===
def main():
    notify("🚀 Accuracy Adjuster started")
    FEEDS = agent_config["feeds"]
    INTERVAL = agent_config["predictor"]["interval_seconds"]

    while True:
        try:
            for feed in FEEDS:
                feed = adjust_prediction_confidence(feed)
                submit_adjusted_feed(feed)
                # Log performance
                with open(PERF_FILE, "a") as f:
                    f.write(f"{datetime.utcnow().isoformat()} - Adjusted {feed['name']} - confidence {feed['confidence']}\n")
            notify(f"Sleeping for {INTERVAL} seconds before next round...")
            time.sleep(INTERVAL)
        except Exception as e:
            notify(f"❌ Unhandled error in Accuracy Adjuster: {e}")
            with open(ERROR_FILE, "a") as f:
                f.write(f"{datetime.utcnow().isoformat()} - ERROR: {e}\n")
            time.sleep(30)

# === Entrypoint ===
if __name__ == "__main__":
    main()
