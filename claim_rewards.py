# claim_rewards.py
import os
import requests
import time
from datetime import datetime, timezone
from telegram_notify import send_telegram_message

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
# If claim API requires a key, make sure it's set as secret and use it
PREDICTOOR_API_KEY = os.getenv("PREDICTOOR_API_KEY", None)

# Example endpoints — replace if your project's endpoints differ.
OCEAN_CLAIM_URL = "https://api.predictoor.ai/v1/claim/ocean"
ROSE_CLAIM_URL  = "https://api.predictoor.ai/v1/claim/rose"

def _post_claim(url, token_name=""):
    headers = {}
    if PREDICTOOR_API_KEY:
        headers["Authorization"] = f"Bearer {PREDICTOOR_API_KEY}"
    payload = {"wallet": WALLET_ADDRESS}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            return True, r.json() if r.text else {}
        else:
            return False, {"status": r.status_code, "text": r.text}
    except Exception as e:
        return False, {"exception": str(e)}

def claim_rewards():
    now = datetime.now(timezone.utc).isoformat()
    print(f"[claim] Starting claim run at {now} for {WALLET_ADDRESS}")

    results = {}
    ok_ocean, res_ocean = _post_claim(OCEAN_CLAIM_URL, "OCEAN")
    results["OCEAN"] = {"ok": ok_ocean, "res": res_ocean}
    time.sleep(2)
    ok_rose, res_rose = _post_claim(ROSE_CLAIM_URL, "ROSE")
    results["ROSE"] = {"ok": ok_rose, "res": res_rose}

    # Build message
    summary_lines = [f"Claim run for {WALLET_ADDRESS} at {now}"]
    for tok, info in results.items():
        if info["ok"]:
            summary_lines.append(f"✅ {tok} claim OK")
        else:
            summary_lines.append(f"⚠️ {tok} claim FAILED -> {info['res']}")
    summary = "\n".join(summary_lines)
    print(summary)

    # Send Telegram alert (success or failure)
    send_telegram_message(summary)
    return results

if __name__ == "__main__":
    claim_rewards()
