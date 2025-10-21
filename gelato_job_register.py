import os, requests, time, json

GELATO_API = "https://api.gelato.network/v2/jobs"
GELATO_API_KEY = os.getenv("GELATO_API_KEY")
RELAYER = os.getenv("GELATO_RELAYER")
PREDICTOOR_API = os.getenv("PREDICTOOR_API")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

FEEDS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT"
]

def notify(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
        )
    except Exception as e:
        print(f"Telegram error: {e}")

def get_jobs():
    try:
        headers = {"Authorization": f"Bearer {GELATO_API_KEY}"}
        r = requests.get(GELATO_API, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json().get("jobs", [])
        else:
            notify(f"⚠️ Failed to fetch jobs: {r.text}")
            return []
    except Exception as e:
        notify(f"❌ Error fetching jobs: {str(e)}")
        return []

def register_job(feed):
    payload = {
        "name": f"Predictoor_{feed.replace('/', '_')}",
        "taskSpec": {
            "execAddress": RELAYER,
            "execData": json.dumps({"feed": feed}),
        },
        "trigger": {
            "interval": 1800  # every 30 minutes
        }
    }

    headers = {"Authorization": f"Bearer {GELATO_API_KEY}"}
    try:
        r = requests.post(GELATO_API, headers=headers, json=payload, timeout=15)
        if r.status_code == 200:
            job_id = r.json().get("id")
            notify(f"🧠 Gelato Job Registered for {feed}: {job_id}")
        else:
            notify(f"⚠️ Job registration failed for {feed}: {r.text}")
    except Exception as e:
        notify(f"❌ Job registration error for {feed}: {str(e)}")

def verify_jobs():
    existing_jobs = get_jobs()
    active_feeds = [j["name"].replace("Predictoor_", "").replace("_", "/") for j in existing_jobs]

    for feed in FEEDS:
        if feed not in active_feeds:
            register_job(feed)
        else:
            notify(f"✅ {feed} still active on Gelato")

if __name__ == "__main__":
    notify("🚀 Starting Gelato Job Verification...")
    verify_jobs()
    notify("✅ Gelato Job Verification Completed.")
