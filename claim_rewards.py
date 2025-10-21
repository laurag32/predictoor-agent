import os, requests, time

PREDICTOOR_API = os.getenv("PREDICTOOR_API")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def notify(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        )
    except:
        pass

def claim_rewards():
    try:
        r = requests.post(f"{PREDICTOOR_API}/claim", timeout=15)
        if r.status_code == 200:
            earned = r.json().get("earned", 0)
            if earned > 0:
                notify(f"💰 Payout received: {earned} USDT")
            else:
                print("No payout this round.")
        else:
            notify(f"⚠️ Claim failed: {r.text}")
    except Exception as e:
        notify(f"❌ Claim error: {str(e)}")

if __name__ == "__main__":
    claim_rewards()
