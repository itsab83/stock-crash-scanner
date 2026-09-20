import os
import requests
import yfinance as yf
from datetime import date

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
FINNHUB_API_KEY = os.environ["FINNHUB_API_KEY"]


def get_reason(symbol):
    try:
        today = date.today().isoformat()

        url = (
            "https://finnhub.io/api/v1/company-news"
            f"?symbol={symbol}"
            f"&from={today}"
            f"&to={today}"
            f"&token={FINNHUB_API_KEY}"
        )

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return "Finnhub Anfrage fehlgeschlagen"

        news = response.json()

        if len(news) == 0:
            return "Keine aktuelle News gefunden"

        headline = news[0].get("headline", "")

        if headline:
            return headline

        return "Keine News gefunden"

    except Exception as e:
        print(f"News-Fehler bei {symbol}: {e}")
        return "News konnten nicht geladen werden"


symbols = set()

index_files = [
    "sp500.txt",
    "nasdaq100.txt",
    "dowjones.txt",
    "dax40.txt",
    "stoxx50.txt",
    "ftse100.txt"
]

for filename in index_files:

    try:

        with open(filename, "r") as f:

            for line in f:

                symbol = line.strip()

                if symbol:
                    symbols.add(symbol)

    except Exception:
        print(f"{filename} nicht gefunden")

symbols = list(symbols)

print(f"{len(symbols)} Aktien geladen")

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

        # mindestens 5 % Verlust
        if change > -5:
            continue

        results.append({
    "symbol": symbol,
    "change": change
})
