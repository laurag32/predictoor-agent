# accuracy_adjuster.py
import yaml
import json
import os
from telegram_notify import send_telegram_message

FEEDS_FILE = "feeds.yaml"
LOG_FILE = "performance_log.json"
MIN_ENTRIES = 5  # minimum records to compute accuracy
SKIP_THRESHOLD = 0.40

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def load_yaml(path):
    if not os.path.exists(path):
        return {"feeds": []}
    with open(path, "r") as f:
        return yaml.safe_load(f)

def save_yaml(path, data):
    with open(path, "w") as f:
        yaml.safe_dump(data, f)

def compute_accuracy(logs, pair):
    if pair not in logs: 
        return None
    entries = logs[pair]
    if len(entries) < MIN_ENTRIES:
        return None
    # simple accuracy rule: treat "UP" vs actual outcome isn't available here,
    # so we use a placeholder metric: fraction of entries with "direction" == "UP"
    ups = sum(1 for e in entries if e.get("direction") == "UP")
    return ups / len(entries)

def adjust():
    logs = load_json(LOG_FILE)
    conf = load_yaml(FEEDS_FILE)
    feeds = conf.get("feeds", conf)  # support list or dict shape

    updated = []
    notifications = []
    for feed in feeds:
        pair = feed.get("pair") or feed.get("name")
        if not pair:
            updated.append(feed); continue

        acc = compute_accuracy(logs, pair)
        old_conf = feed.get("confidence", 0.6)
        if acc is None:
            # Not enough data: keep unchanged
            feed["confidence"] = round(old_conf, 3)
            updated.append(feed)
            continue

        # Adjust rules:
        if acc > 0.65:
            feed["confidence"] = round(min(old_conf + 0.03, 0.95), 3)
        elif acc < 0.45:
            feed["confidence"] = round(max(old_conf - 0.03, 0.5), 3)
        else:
            feed["confidence"] = round(old_conf, 3)

        # Skip feed if very poor accuracy
        if acc < SKIP_THRESHOLD:
            feed["skip"] = True
            msg = f"⚠️ Feed {pair} disabled. Accuracy {acc:.2f} < {SKIP_THRESHOLD}"
            notifications.append(msg)
        updated.append(feed)

    # write back (respecting original structure)
    if isinstance(conf, dict) and "feeds" in conf:
        conf["feeds"] = updated
    else:
        conf = {"feeds": updated}
    save_yaml(FEEDS_FILE, conf)
    print("[accuracy] Adjustment complete.")

    # send summary notifications if any critical items
    if notifications:
        body = "Accuracy adjuster flagged issues:\n" + "\n".join(notifications)
        send_telegram_message(body)

if __name__ == "__main__":
    adjust()
