import os, requests, random, time, json

GELATO_RELAYER = os.getenv("GELATO_RELAYER")
PREDICTOOR_API = os.getenv("PREDICTOOR_API")
FEEDS = [
    "BTC/USDT", 
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT"
]

def get_prediction_confidence(feed):
    return round(random.uniform(0.75, 0.99), 2)

def send_prediction(feed, confidence):
    payload = {
        "feed": feed,
        "confidence": confidence,
        "relayer": GELATO_RELAYER,
        "timestamp": int(time.time())
    }
    try:
        r = requests.post(PREDICTOOR_API, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"✅ Prediction sent: {feed} ({confidence})")
        else:
            print(f"❌ Failed: {feed} | {r.text}")
    except Exception as e:
        print(f"Error sending {feed}: {str(e)}")

def run_cycle():
    for feed in FEEDS:
        conf = get_prediction_confidence(feed)
        send_prediction(feed, conf)
        time.sleep(3)

if __name__ == "__main__":
    run_cycle()
