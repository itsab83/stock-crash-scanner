import yfinance as yf

ticker = yf.Ticker("AAPL")

hist = ticker.history(period="5d")

print(hist.tail())
