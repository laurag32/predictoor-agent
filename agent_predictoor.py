import os
import json
import time
import random
import requests
from datetime import datetime
from telegram import Bot

# === CONFIG ===
AGENT_JSON = "agent_instructions.json"

def load_agent_config():
    with open(AGENT_JSON, "r") as f:
        return json.load(f)

agent_config = load_agent_config()
telegram_bot = Bot(token=agent_config["telegram"]["bot_token"])
wallet = agent_config["wallet"]
feeds = agent_config["feeds"]
predictoor = agent_config["predictoor"]
gelato_relayer = agent_config["gelato"].get("relayer")

# === TELEGRAM NOTIFY ===
def notify(msg):
    print(msg)
    try:
        telegram_bot.send_message(chat_id=agent_config["telegram"]["chat_id"], text=msg)
    except Exception as e:
        print(f"[WARN] Telegram notify failed: {e}")

# === SAFE REQUEST ===
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

# === PREDICTION LOGIC ===
def prepare_prediction(feed):
    """
    Simple example: mock prediction payload.
    In real case: build model based on previous epochs.
    """
    prediction_confidence = random.uniform(0.6, 0.9)
    direction = "up" if prediction_confidence >= 0.7 else "down"
    payload = {
        "feed": feed["name"],
        "exchange": feed["exchange"],
        "direction": direction,
        "confidence": round(prediction_confidence, 2),
        "wallet": wallet["address"],
        "timestamp": datetime.utcnow().isoformat()
    }
    return payload

# === SUBMIT TO GELATO RELAYER ===
def submit_prediction(payload):
    if not gelato_relayer:
        notify("❌ Gelato relayer unavailable.")
        return False
    response = safe_post(gelato_relayer, payload)
    if response:
        notify(f"✅ Submitted prediction for {payload['feed']} | {payload['direction']} @ {payload['confidence']}")
        return True
    else:
        notify(f"❌ Submission failed for {payload['feed']}")
        return False

# === MAIN LOOP ===
def main():
    notify("Starting Predictoor Agent...")
    while True:
        for feed in feeds:
            payload = prepare_prediction(feed)
            submit_prediction(payload)
        notify(f"Sleeping for {feeds[0]['interval_minutes']} minutes before next round...")
        time.sleep(feeds[0]["interval_minutes"] * 60)  # repeat per feed interval

# === ENTRYPOINT ===
if __name__ == "__main__":
    main()
