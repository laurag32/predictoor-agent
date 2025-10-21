import os, requests, json

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def notify(msg: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(msg)
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
        )
    except Exception as e:
        print(f"Telegram notify failed: {e}")

def auto_get_relayer():
    url = "https://api.gelato.network/v2/relayers"
    try:
        r = requests.get(url, timeout=10)
        relayers = r.json().get("relayers", [])
        if not relayers:
            notify("⚠️ No relayers found on Gelato API.")
            return None
        best = max(relayers, key=lambda x: x.get("jobsExecuted", 0))
        relayer = best["address"]
        notify(f"✅ Selected Gelato relayer:\n{relayer}")
        with open("gelato_relayer.json", "w") as f:
            json.dump({"relayer": relayer}, f)
        return relayer
    except Exception as e:
        notify(f"❌ Error fetching relayers: {e}")
        return None

if __name__ == "__main__":
    auto_get_relayer()
