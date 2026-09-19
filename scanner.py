import os
import requests
import pandas as pd
import yfinance as yf

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# S&P 500 laden
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

sp500 = pd.read_html(url)[0]

symbols = sp500["Symbol"].tolist()

results = []

for symbol in symbols:

    try:

        symbol = symbol.replace(".", "-")

        stock = yf.Ticker(symbol)

        hist = stock.history(period="2d")

        if len(hist) < 2:
            continue

        previous = hist["Close"].iloc[-2]
        current = hist["Close"].iloc[-1]

        change = ((current - previous) / previous) * 100

        results.append({
            "symbol": symbol,
            "change": change
        })

    except Exception:
        pass

results.sort(
    key=lambda x: x["change"]
)

top_losers = results[:10]

message = "🚨 Top Verlierer S&P 500\n\n"

for stock in top_losers:

    message += (
        f"{stock['symbol']} "
        f"{stock['change']:.2f}%\n"
    )

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(message)
