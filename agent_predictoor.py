import json, yaml, time, random, requests, os
from datetime import datetime

with open("feeds.yaml", "r") as f:
    feeds = yaml.safe_load(f)["feeds"]

RELAYER_URL = "https://relay.gelato.digital/meta-tx"
PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")  # set this secret in GitHub Actions
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

LOG_PATH = "performance_log.json"

def get_market_data(pair):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={pair}"
    try:
        resp = requests.get(url).json()
        return float(resp["price"])
    except Exception:
        return None

def make_prediction(feed):
    price = get_market_data(feed["pair"])
    if not price:
        print(f"[x] Failed to fetch {feed['pair']}")
        return None

    # generate pseudo prediction
    direction = random.choice(["UP", "DOWN"])
    confidence = feed["confidence"] + random.uniform(-0.05, 0.05)
    confidence = max(0.5, min(0.95, confidence))
    payload = {
        "pair": feed["pair"],
        "price": price,
        "direction": direction,
        "confidence": round(confidence, 3),
        "timestamp": datetime.utcnow().isoformat()
    }
    print(f"[+] Prediction: {payload}")

    # submit via Gelato relayer (mocked)
    tx = {
        "from": WALLET_ADDRESS,
        "data": json.dumps(payload),
        "signature": "signed_with_private_key"
    }
    # Simulate relay success
    print(f"[relay] Submitted gasless tx for {feed['pair']}")
    return payload

def log_result(feed, result):
    log = {}
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            log = json.load(f)

    if feed["pair"] not in log:
        log[feed["pair"]] = []

    log[feed["pair"]].append(result)
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

if __name__ == "__main__":
    for feed in feeds:
        if feed.get("skip"): continue
        result = make_prediction(feed)
        if result:
            log_result(feed, result)
        time.sleep(3)
