import os
import requests
import yfinance as yf

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Aktien aus Dateien laden
symbols = set()

files = [
    "sp500.txt",
    "nasdaq100.txt",
    "dowjones.txt",
    "dax40.txt",
    "stoxx50.txt",
    "ftse100.txt"
]

for filename in files:

    try:

        with open(filename, "r") as f:

            for line in f:

                symbol = line.strip()

                if symbol:
                    symbols.add(symbol)

    except Exception:
        pass

symbols = list(symbols)

results = []

for symbol in symbols:

    try:

        stock = yf.Ticker(symbol)

        hist = stock.history(period="2d")

        if len(hist) < 2:
            continue

        previous_close = hist["Close"].iloc[-2]
        current_price = hist["Close"].iloc[-1]

        change = (
            (current_price - previous_close)
            / previous_close
        ) * 100
if change > -5:
    continue
        results.append({
            "symbol": symbol,
            "change": change
        })

    except Exception as e:
        print(f"Fehler bei {symbol}: {e}")

# Nach stärkstem Verlust sortieren
results.sort(
    key=lambda x: x["change"]
)

# Top 10 Verlierer
top_losers = results[:10]

message = "🚨 Börsencrash Scanner\n\n"

for stock in top_losers:

   message += (
    f"📉 {stock['symbol']}\n"
    f"{stock['change']:.2f}%\n\n"
)

# Telegram senden
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(response.status_code)
print(response.text)
print(message)
