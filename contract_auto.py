# contract_auto.py
import os
import json
import requests

# ✅ Updated stable endpoints
OCEAN_PREDICTOOR_REGISTRY = "https://oceanprotocol.github.io/contracts/addresses.mainnet.json"
GELATO_RELAYER_ENDPOINT = "https://relay.gelato.digital/api/v2/relayers"

# ✅ Telegram environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def notify(msg: str):
    """Send Telegram update if available, else print."""
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


def get_active_contracts():
    """Fetch and save the current Ocean Predictoor mainnet contract."""
    try:
        data = requests.get(OCEAN_PREDICTOOR_REGISTRY, timeout=10).json()
        # New JSON layout: look for the 'mainnet' section
        mainnet_contracts = data.get("mainnet", {})
        predictoor = mainnet_contracts.get("Predictoor", "")

        if predictoor:
            with open("active_contracts.json", "w") as f:
                json.dump({"predictoor_contract": predictoor}, f)
            notify(f"✅ Predictoor contract auto-fetched:\n{predictoor}")
        else:
            notify("⚠️ No Predictoor contract found in mainnet registry.")
    except Exception as e:
        notify(f"❌ Error fetching Predictoor contract: {e}")


def auto_get_relayer():
    """Select the most active Gelato relayer and save address."""
    try:
        r = requests.get(GELATO_RELAYER_ENDPOINT, timeout=10)
        relayers = r.json().get("relayers", [])
        if not relayers:
            notify("⚠️ No relayers found on Gelato API.")
            return None

        # Pick relayer with most executed jobs
        best = max(relayers, key=lambda x: x.get("jobsExecuted", 0))
        relayer = best["address"]

        with open("gelato_relayer.json", "w") as f:
            json.dump({"relayer": relayer}, f)

        notify(f"✅ Selected Gelato relayer:\n{relayer}")
        return relayer
    except Exception as e:
        notify(f"❌ Error fetching Gelato relayers: {e}")
        return None


if __name__ == "__main__":
    get_active_contracts()
    auto_get_relayer()
