# contract_auto.py
import requests, json

OCEAN_PREDICTOOR_REGISTRY = "https://raw.githubusercontent.com/oceanprotocol/contracts/main/addresses.json"

def get_active_contracts():
    try:
        data = requests.get(OCEAN_PREDICTOOR_REGISTRY, timeout=10).json()
        sapphire_contracts = data.get("sapphire-mainnet", {})
        predictoor = sapphire_contracts.get("Predictoor", "")
        if predictoor:
            print(f"[AutoFetch] Using Predictoor contract: {predictoor}")
            with open("active_contracts.json", "w") as f:
                json.dump({"predictoor_contract": predictoor}, f)
        else:
            print("[AutoFetch] No Predictoor contract found.")
    except Exception as e:
        print("[AutoFetch] Error:", e)

if __name__ == "__main__":
    get_active_contracts()
