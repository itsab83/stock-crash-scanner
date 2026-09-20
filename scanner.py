import os
import requests
import yfinance as yf
from datetime import date, timedelta

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")


def get_reason(symbol):

    if not FINNHUB_API_KEY:
        return "Keine Newsanalyse verfügbar"

    try:

        to_date = date.today()
        from_date = to_date - timedelta(days=3)

        url = (
            "https://finnhub.io/api/v1/company-news"
            f"?symbol={symbol}"
            f"&from={from_date.isoformat()}"
            f"&to={to_date.isoformat()}"
            f"&token={FINNHUB_API_KEY}"
        )

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code != 200:
            return "News nicht abrufbar"

        news = response.json()

        if len(news) == 0:
            return "Keine aktuelle News"

        return news[0]["headline"]

    except Exception as e:

        print(f"Newsfehler {symbol}: {e}")
        return "Newsfehler"


symbols = set()

for filename in [
    "sp500.txt",
    "nasdaq100.txt",
    "dax40.txt",
    "stoxx50.txt",
    "ftse100.txt",
    "dowjones.txt"
]:

    try:

        with open(filename, "r") as f:

            for line in f:

                symbol = line.strip()

                if symbol:
                    symbols.add(symbol)

    except Exception:

        pass

results = []

for symbol in symbols:

    try:

        stock = yf.Ticker(symbol)

        hist = stock.history(
            period="2d"
        )

        if len(hist) < 2:
            continue

        previous_close = hist["Close"].iloc[-2]
        current_price = hist["Close"].iloc[-1]

        change = (
            (current_price - previous_close)
            / previous_close
        ) * 100

        # Nur relevante Crashes
        if change > -6:
            continue

        results.append({
            "symbol": symbol,
            "change": change
        })

    except Exception as e:

        print(
            f"Fehler bei {symbol}: {e}"
        )

results.sort(
    key=lambda x: x["change"]
)

top_losers = results[:10]

message = (
    "🚨 Börsencrash Scanner\n\n"
)

if len(top_losers) == 0:

    message += (
        "✅ Keine Aktien mit mehr "
        "als 6 % Verlust gefunden."
    )

else:

    for stock in top_losers:

        reason = get_reason(
            stock["symbol"]
        )

        message += (
            f"📉 {stock['symbol']}\n"
            f"{stock['change']:.2f}%\n"
            f"Grund: {reason}\n\n"
        )

url = (
    f"https://api.telegram.org/"
    f"bot{BOT_TOKEN}/sendMessage"
)

requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(message)
