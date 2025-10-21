# contract_auto.py
import os
import json
import requests
import time

# ✅ Main and backup sources for Predictoor contract registry
OCEAN_PRIMARY = "https://raw.githubusercontent.com/oceanprotocol/contracts/main/addresses.json"
OCEAN_BACKUP = "https://contracts.oceanprotocol.com/addresses.json"

# ✅ Telegram for logs
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =============== CORE HELPERS ===================
def notify(msg: str):
    """Send Telegram update if available, else print."""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
                timeout=10
            )
        except Exception as e:
            print(f"Telegram notify failed: {e}")
    print(msg)


# =============== CONTRACT FETCHER ===================
def get_predictoor_contract():
    """Fetch the Predictoor contract from Ocean registry with fallback."""
    urls = [OCEAN_PRIMARY, OCEAN_BACKUP]
    for url in urls:
        try:
            r = requests.get(url, timeout=15)
            data = r.json()
            sapphire_contracts = data.get("sapphire-mainnet", {})
            predictoor = sapphire_contracts.get("Predictoor", "")
            if predictoor:
                with open("active_contracts.json", "w") as f:
                    json.dump({"predictoor_contract": predictoor}, f)
                notify(f"✅ Predictoor contract fetched:\n{predictoor}")
                return predictoor
        except Exception as e:
            notify(f"⚠️ Error fetching Predictoor contract from {url}: {e}")

    # fallback to local cache
    if os.path.exists("active_contracts.json"):
        try:
            with open("active_contracts.json") as f:
                cached = json.load(f).get("predictoor_contract")
                if cached:
                    notify(f"♻️ Using cached Predictoor contract:\n{cached}")
                    return cached
        except Exception as e:
            notify(f"❌ Cached contract corrupted: {e}")

    notify("🚨 Predictoor contract unavailable (network or JSON error).")
    return None


# =============== GELATO RELAYER ===================
def get_gelato_relayer():
    """Fetch the most active Gelato relayer address with fallback."""
    url = "https://api.gelato.network/v2/relayers"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        relayers = data.get("relayers", [])
        if not relayers:
            notify("⚠️ No relayers found on Gelato API.")
            return None

        # select the most active relayer
        best = max(relayers, key=lambda x: x.get("jobsExecuted", 0))
        relayer = best["address"]

        with open("gelato_relayer.json", "w") as f:
            json.dump({"relayer": relayer}, f)

        notify(f"✅ Selected Gelato relayer:\n{relayer}")
        return relayer

    except Exception as e:
        notify(f"❌ Error fetching Gelato relayers: {e}")
        # fallback to local
        if os.path.exists("gelato_relayer.json"):
            try:
                with open("gelato_relayer.json") as f:
                    cached = json.load(f).get("relayer")
                    if cached:
                        notify(f"♻️ Using cached relayer:\n{cached}")
                        return cached
            except Exception as e:
                notify(f"❌ Cached relayer corrupted: {e}")
        return None


# =============== EXECUTION ===================
if __name__ == "__main__":
    notify("🔄 Auto-updating contract and relayer…")
    contract = get_predictoor_contract()
    time.sleep(1)
    relayer = get_gelato_relayer()

    if contract and relayer:
        notify("✅ Contract + Relayer updated successfully.")
    else:
        notify("⚠️ Auto-update completed with some warnings.")
