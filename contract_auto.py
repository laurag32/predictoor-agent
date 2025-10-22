# contract_auto.py
import os
import json
import time
import requests

AGENT_JSON = "agent_instructions.json"

# Telegram
cfg = json.load(open(AGENT_JSON))
TELEGRAM_BOT_TOKEN = cfg["telegram"]["bot_token"]
TELEGRAM_CHAT_ID = cfg["telegram"]["chat_id"]

# Contract & Relayer sources
OCEAN_REGISTRY_URLS = [
    "https://raw.githubusercontent.com/oceanprotocol/contracts/main/addresses.json",
    "https://contracts.oceanprotocol.com/addresses.json",
    "https://cdn.jsdelivr.net/gh/oceanprotocol/contracts@main/addresses.json"
]
GELATO_RELAYER_URLS = [
    "https://api.gelato.network/v2/relayers",
    "https://relay.gelato.digital/v2/relayers"
]

def notify(msg: str):
    print(msg)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
                timeout=10
            )
        except Exception as e:
            print(f"[WARN] Telegram notify failed: {e}")

def safe_get(url, retries=3, delay=5):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.text
        except Exception as e:
            notify(f"Retry {i+1}/{retries} failed for {url}: {e}")
            time.sleep(delay)
    return None

def get_predictoor_contract():
    for url in OCEAN_REGISTRY_URLS:
        text = safe_get(url)
        if text:
            try:
                data = json.loads(text)
                predictoor = data.get("sapphire-mainnet", {}).get("Predictoor")
                if predictoor:
                    json.dump({"predictoor_contract": predictoor}, open("active_contracts.json", "w"))
                    notify(f"✅ Predictoor contract auto-fetched:\n{predictoor}")
                    return predictoor
            except Exception as e:
                notify(f"Error parsing JSON from {url}: {e}")
    notify("⚠️ Predictoor contract unavailable (network or JSON error).")
    return None

def get_gelato_relayer():
    for url in GELATO_RELAYER_URLS:
        text = safe_get(url)
        if text:
            try:
                data = json.loads(text)
                relayers = data.get("relayers", []) if isinstance(data, dict) else data
                if relayers:
                    best = max(relayers, key=lambda x: x.get("jobsExecuted", 0))
                    relayer = best.get("address") or best.get("url") or str(best)
                    json.dump({"relayer": relayer}, open("gelato_relayer.json", "w"))
                    notify(f"✅ Selected Gelato relayer: {relayer}")
                    return relayer
            except Exception as e:
                notify(f"Error parsing relayer JSON from {url}: {e}")
    notify("❌ Unable to fetch Gelato relayer, using fallback.")
    return "https://relay-fallback.gelato.digital"

if __name__ == "__main__":
    notify("Auto-updating contract and relayer...")
    get_predictoor_contract()
    get_gelato_relayer()
    notify("✅ Auto-update completed.")
