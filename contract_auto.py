import json, requests, time, os

AGENT_JSON = "agent_instructions.json"

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
    return "0x7F645c91c3D177F0030041b98d89F2D9992c2125"

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
                relayers = data.get("relayers") or []
                if relayers:
                    relayer = relayers[0]
                    print(f"✅ Gelato relayer fetched: {relayer}")
                    return relayer
        except Exception as e:
            print(f"⚠️ Attempt {i} failed: {e}")
            time.sleep(2)
    print("⚠️ Using default Gelato relayer from JSON.")
    return "https://relay-fallback.gelato.digital"

def update_agent_json(contract, relayer):
    try:
        with open(AGENT_JSON, "r") as f:
            config = json.load(f)

        config["predictoor"]["contract_address"] = contract
        config["gelato"]["relayer"] = relayer

        with open(AGENT_JSON, "w") as f:
            json.dump(config, f, indent=4)

        print(f"✅ agent_instructions.json updated with latest contract & relayer.")
    except Exception as e:
        print(f"❌ Failed to update {AGENT_JSON}: {e}")

if __name__ == "__main__":
    print("🌐 Auto-updating Predictoor contract & Gelato relayer...")
    predictoor_contract = fetch_predictoor_contract()
    gelato_relayer = fetch_gelato_relayer()
    update_agent_json(predictoor_contract, gelato_relayer)
    print("✅ Auto-update completed.\n")
