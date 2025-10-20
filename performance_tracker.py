import json, os, statistics

LOG_PATH = "performance_log.json"

def calculate_accuracy(logs):
    acc = {}
    for pair, entries in logs.items():
        if len(entries) < 5:
            continue
        # dummy accuracy = % of “UP” predictions (placeholder metric)
        ups = sum(1 for e in entries if e["direction"] == "UP")
        acc[pair] = ups / len(entries)
    return acc

if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r") as f:
        logs = json.load(f)
        acc = calculate_accuracy(logs)
        print(json.dumps(acc, indent=2))
else:
    print("No logs yet.")
