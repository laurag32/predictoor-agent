# profit_tracker.py
import os, json, time, requests
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

# Ocean or Sapphire block explorer API for balance tracking
EXPLORER_API = f"https://api.sapphire.oasis.io/api/v1/accounts/{WALLET_ADDRESS}"

def notify(msg: str):
    """Send Telegram message or print fallback."""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
                timeout=10
            )
        except Exception as e:
            print(f"[ProfitTracker] Telegram notify failed: {e}")
    print(msg)

def get_balance():
    """Fetch current wallet balance from Sapphire explorer API."""
    try:
        r = requests.get(EXPLORER_API, timeout=10)
        data = r.json()
        balance = int(data.get("balance", 0)) / 1e18  # convert from wei
        return balance
    except Exception as e:
        notify(f"[ProfitTracker] ❌ Error fetching balance: {e}")
        return None

def track_profit():
    """Compare today’s and yesterday’s wallet balances."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    last_balance = 0
    prev_file = "profit_log.json"

    new_balance = get_balance()
    if new_balance is None:
        return

    if os.path.exists(prev_file):
        with open(prev_file, "r") as f:
            history = json.load(f)
            last_entry = history[-1] if history else {}
            last_balance = last_entry.get("balance", 0)
    else:
        history = []

    profit = new_balance - last_balance
    entry = {"date": today, "balance": new_balance, "profit": profit}

    history.append(entry)
    with open(prev_file, "w") as f:
        json.dump(history, f, indent=2)

    msg = f"📊 *Daily Profit Summary*\n" \
          f"Date: {today}\n" \
          f"Current Balance: {new_balance:.4f} OCEAN\n" \
          f"Change (24h): {profit:+.4f} OCEAN\n"
    notify(msg)

if __name__ == "__main__":
    track_profit()
