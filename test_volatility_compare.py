import yfinance as yf
import pandas_ta as ta

for ticker in ["BTC-USD", "ETH-USD"]:
    data = yf.download(ticker, period="2y", interval="1d")
    data.columns = data.columns.get_level_values(0)

    daily_returns = data["Close"].pct_change().dropna()
    atr = ta.atr(data["High"], data["Low"], data["Close"], length=14)
    atr_pct = (atr / data["Close"]) * 100  # ATR sebagai % dari harga, biar bisa dibandingkan

    print(f"=== {ticker} ===")
    print(f"Daily return std (volatility): {daily_returns.std() * 100:.2f}%")
    print(f"Average ATR (% of price)      : {atr_pct.mean():.2f}%")
    print()