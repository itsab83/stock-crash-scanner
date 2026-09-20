import os
import requests
import yfinance as yf

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

symbols = []

for filename in [
    "sp500.txt",
    "nasdaq100.txt",
    "dax40.txt"
]:

    try:

        with open(filename, "r") as f:

            for line in f:

                symbol = line.strip()

                if symbol:
                    symbols.append(symbol)

    except Exception as e:

        print(f"Fehler bei {filename}: {e}")

message = f"Scanner gestartet\n{len(symbols)} Aktien geladen"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(message)
