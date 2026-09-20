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
        from_date = to_date - timedelta(days=7)

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


def classify_reason(reason):

    text = reason.lower()

    if any(word in text for word in [
        "downgrade",
        "cuts price target",
        "lowers price target",
        "analyst"
    ]):
        return "🟡 Analysten-Downgrade"

    if any(word in text for word in [
        "earnings",
        "revenue",
        "guidance",
        "forecast",
        "outlook"
    ]):
        return "🔴 Schwache Quartalszahlen / Ausblick"

    if any(word in text for word in [
        "lawsuit",
        "investigation",
        "sec",
        "probe"
    ]):
        return "🔴 Rechtliches Risiko"

    if any(word in text for word in [
        "offering",
        "share sale",
        "secondary offering"
    ]):
        return "🟠 Kapitalmaßnahme"

    return "⚪ Nicht eindeutig"


def get_6m_performance(symbol):

    try:

        stock = yf.Ticker(symbol)

        hist = stock.history(
            period="6mo"
        )

        if len(hist) < 2:
            return None

        first_price = hist["Close"].iloc[0]
        last_price = hist["Close"].iloc[-1]

        performance = (
            (last_price - first_price)
            / first_price
        ) * 100

        return performance

    except Exception:

        return None


def get_distance_to_52w_high(symbol):

    try:

        stock = yf.Ticker(symbol)

        hist = stock.history(
            period="1y"
        )

        if len(hist) < 2:
            return None

        high_52w = hist["High"].max()
        current_price = hist["Close"].iloc[-1]

        distance = (
            (current_price - high_52w)
            / high_52w
        ) * 100

        return distance

    except Exception:

        return None


symbols = set()

for filename in [
    "sp500.txt",
    "nasdaq100.txt",
    "dowjones.txt",
    "dax40.txt",
    "stoxx50.txt",
    "ftse100.txt"
]:

    try:

        with open(filename, "r") as f:

            for line in f:

                symbol = line.strip()

                if symbol:
                    symbols.add(symbol)

    except Exception as e:

        print(f"Fehler bei {filename}: {e}")

results = []

for symbol in symbols:

    try:

        stock = yf.Ticker(symbol)

        hist = stock.history(
    period="3mo"
)

if len(hist) < 60:
    continue

previous_close = hist["Close"].iloc[-2]
current_price = hist["Close"].iloc[-1]

change = (
    (current_price - previous_close)
    / previous_close
) * 100

current_volume = hist["Volume"].iloc[-1]

avg_volume = (
    hist["Volume"]
    .tail(60)
    .mean()
)

volume_factor = (
    current_volume / avg_volume
)

# Nur relevante Kursstürze
if change > -4:
    continue

# Nur erhöhtes Handelsvolumen
if volume_factor < 1.5:
    continue

results.append({
    "symbol": symbol,
    "change": change,
    "volume_factor": volume_factor
})

    except Exception as e:

        print(f"Fehler bei {symbol}: {e}")

results.sort(
    key=lambda x: x["change"]
)

top_losers = results[:10]

if len(top_losers) == 0:

    print(
        "Keine Aktien mit mehr als 4% Verlust gefunden."
    )

    exit()

message = "🚨 Börsencrash Scanner\n\n"

for stock in top_losers:

    reason = get_reason(
        stock["symbol"]
    )

    category = classify_reason(
        reason
    )

    perf_6m = get_6m_performance(
        stock["symbol"]
    )

    distance_52w = get_distance_to_52w_high(
        stock["symbol"]
    )

    if perf_6m is None:
        perf_text = "nicht verfügbar"
    else:
        perf_text = f"{perf_6m:.1f}%"

    if distance_52w is None:
        high_text = "nicht verfügbar"
    else:
        high_text = f"{distance_52w:.1f}%"

    chart_url = (
        f"https://finance.yahoo.com/chart/"
        f"{stock['symbol']}"
    )

    message += (
    f"📉 {stock['symbol']}\n"
    f"Heute: {stock['change']:.2f}%\n"
    f"Volumen: {stock['volume_factor']:.1f}x\n"
    f"6 Monate: {perf_text}\n"
    f"52W-Hoch: {high_text}\n"
    f"Kategorie: {category}\n"
    f"Grund: {reason}\n"
    f"Chart: {chart_url}\n\n"
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
