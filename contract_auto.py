import os, json, time, requests

OCEAN_PREDICTOOR_REGISTRY = [
    "https://raw.githubusercontent.com/oceanprotocol/contracts/main/addresses.json",
    "https://contracts.oceanprotocol.com/addresses.json"
]
GELATO_RELAYER_API = "https://api.gelato.network/v2/relayers"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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
            print(f"Telegram notify failed: {e}")

def fetch_json(url):
    for i in range(3):
        try:
            r = requests.get(url, timeout=10)
            return r.json()
        except Exception as e:
            notify(f"Retry {i+1}/3 failed for {url}: {e}")
            time.sleep(5)
    return None

def get_active_contracts():
    for url in OCEAN_PREDICTOOR_REGISTRY:
        data = fetch_json(url)
        if not data: 
            continue
        sapphire = data.get("sapphire-mainnet", {})
        predictoor = sapphire.get("Predictoor")
        if predictoor:
            json.dump({"predictoor_contract": predictoor}, open("active_contracts.json", "w"))
            notify(f"✅ Predictoor contract auto-fetched:\n{predictoor}")
            return predictoor
    notify("⚠️ Predictoor contract unavailable (network or JSON error).")
    return None

def auto_get_relayer():
    data = fetch_json(GELATO_RELAYER_API)
    if not data:
        notify("❌ Unable to fetch Gelato relayers.")
        return None
    relayers = data.get("relayers", [])
    if not relayers:
        notify("⚠️ No relayers found.")
        return None
    best = max(relayers, key=lambda x: x.get("jobsExecuted", 0))
    relayer = best["address"]
    json.dump({"relayer": relayer}, open("gelato_relayer.json", "w"))
    notify(f"✅ Selected Gelato relayer:\n{relayer}")
    return relayer

if __name__ == "__main__":
    notify("Auto-updating contract and relayer...")
    get_active_contracts()
    auto_get_relayer()
    notify("⚠️ Auto-update completed with some warnings (if any).")
