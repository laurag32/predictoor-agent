import json, requests, time

def fetch_predictoor_contract():
    urls = [
        "https://raw.githubusercontent.com/oceanprotocol/addresses/main/predictoor.json",
        "https://cdn.jsdelivr.net/gh/oceanprotocol/addresses@main/predictoor.json",
        "https://oceanprotocol.github.io/addresses/predictoor.json"
    ]
    for i, url in enumerate(urls, 1):
        try:
            print(f"🔄 Fetching Predictoor contract (attempt {i})...")
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            data = response.json()
            contract = data.get("predictoor", {}).get("address")
            if contract:
                print(f"✅ Found Predictoor contract: {contract}")
                return contract
        except Exception as e:
            print(f"⚠️ Attempt {i} failed: {e}")
            time.sleep(2)
    print("⚠️ Using hardcoded fallback contract.")
    return "0x7F645c91c3D177F0030041b98d89F2D9992c2125"  # fallback

def fetch_gelato_relayer():
    urls = [
        "https://relay.gelato.network/api/v2/relayers",
        "https://relay.gelato.digital/api/v2/relayers"
    ]
    for i, url in enumerate(urls, 1):
        try:
            print(f"🔄 Fetching Gelato relayer (attempt {i})...")
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, dict):
                relayer = list(data.get("relayers", []))[0]
                print(f"✅ Gelato relayer fetched: {relayer}")
                return relayer
        except Exception as e:
            print(f"⚠️ Attempt {i} failed: {e}")
            time.sleep(2)
    print("⚠️ Using default Gelato relayer from JSON.")
    return "https://relay-fallback.gelato.digital"

if __name__ == "__main__":
    print("Auto-updating contract and relayer...")
    predictoor_contract = fetch_predictoor_contract()
    gelato_relayer = fetch_gelato_relayer()
    print(f"✅ Auto-update completed.\nContract: {predictoor_contract}\nRelayer: {gelato_relayer}")
