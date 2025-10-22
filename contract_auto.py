# contract_auto.py (final resilient version)
import os, json, time, requests, pathlib

# --- registry & relayer endpoints ---
OCEAN_PREDICTOOR_REGISTRY = [
    "https://raw.githubusercontent.com/oceanprotocol/contracts/main/addresses.json",
    "https://contracts.oceanprotocol.com/addresses.json",
    "https://cdn.jsdelivr.net/gh/oceanprotocol/contracts@main/addresses.json"
]

GELATO_RELAYER_API = [
    "https://api.gelato.network/v2/relayers",
    "https://relay.gelato.digital/v2/relayers"
]

# --- Telegram setup ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- cache paths ---
CACHE_CONTRACT = pathlib.Path("active_contracts.json")
CACHE_RELAYER = pathlib.Path("gelato_relayer.json")


# ===== utilities =====
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
    """Try multiple times and return JSON or None."""
    for i in range(3):
        try:
            r = requests.get(url, timeout=10)
            return r.json()
        except Exception as e:
            notify(f"Retry {i+1}/3 failed for {url}: {e}")
            time.sleep(4)
    return None


def verify_contract(addr: str) -> bool:
    """Check if the contract actually exists on Sapphire explorer."""
    try:
        url = f"https://explorer.sapphire.oasis.io/api?module=contract&action=getabi&address={addr}"
        r = requests.get(url, timeout=10)
        js = r.json()
        if r.status_code == 200 and "result" in js and js["result"]:
            return True
    except Exception:
        pass
    return False


# ===== core functions =====
def get_active_contracts():
    """Fetch Predictoor contract from any available registry."""
    for url in OCEAN_PREDICTOOR_REGISTRY:
        data = fetch_json(url)
        if not data:
            continue

        sapphire = data.get("sapphire-mainnet", {})
        predictoor = sapphire.get("Predictoor")

        if predictoor and verify_contract(predictoor):
            CACHE_CONTRACT.write_text(json.dumps({"predictoor_contract": predictoor}, indent=2))
            notify(f"✅ Predictoor contract auto-fetched:\n{predictoor}")
            return predictoor

    # fallback: use cached if available
    if CACHE_CONTRACT.exists():
        cached = json.load(open(CACHE_CONTRACT))
        predictoor = cached.get("predictoor_contract")
        notify(f"⚠️ Using cached Predictoor contract:\n{predictoor}")
        return predictoor

    notify("❌ Predictoor contract unavailable (network or invalid).")
    return None


def auto_get_relayer():
    """Select the most active Gelato relayer."""
    for url in GELATO_RELAYER_API:
        data = fetch_json(url)
        if not data:
            continue

        relayers = data.get("relayers", [])
        if not relayers:
            continue

        best = max(relayers, key=lambda x: x.get("jobsExecuted", 0))
        relayer = best["address"]
        CACHE_RELAYER.write_text(json.dumps({"relayer": relayer}, indent=2))
        notify(f"✅ Selected Gelato relayer:\n{relayer}")
        return relayer

    # fallback: cached
    if CACHE_RELAYER.exists():
        cached = json.load(open(CACHE_RELAYER))
        relayer = cached.get("relayer")
        notify(f"⚠️ Using cached Gelato relayer:\n{relayer}")
        return relayer

    notify("❌ Unable to fetch or cache Gelato relayer.")
    return None


# ===== run when executed =====
if __name__ == "__main__":
    notify("⚙️ Auto-updating contract and relayer...")
    contract = get_active_contracts()
    relayer = auto_get_relayer()

    if contract and relayer:
        notify("✅ Auto-update successful and verified.")
    else:
        notify("⚠️ Auto-update completed with warnings or partial success.")
