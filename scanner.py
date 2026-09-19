import os
import requests
import yfinance as yf

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

watchlist = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "TSLA",
    "PLTR",
    "CRWD",
    "SNOW",
    "AMD"
]

message = "🚨 US Crash Scanner\n\n"

found = False

for symbol in watchlist:

    try:

        stock = yf.Ticker(symbol)

        hist = stock.history(period="2d")

        if len(hist) < 2:
            continue

        yesterday = hist["Close"].iloc[-2]
        today = hist["Close"].iloc[-1]

        change = ((today - yesterday) / yesterday) * 100

        if change <= -3:

            found = True

            message += (
                f"{symbol}: {change:.2f}%\n"
            )

    except Exception:
        pass

if not found:
    message += "Keine größeren Kursstürze gefunden."

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(message)
