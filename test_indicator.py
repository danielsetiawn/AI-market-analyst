import yfinance as yf
import pandas_ta as ta

data = yf.download("BTC-USD", period="6mo", interval="1d")

# yfinance return MultiIndex columns, kita flatten dulu
data.columns = data.columns.get_level_values(0)

data["EMA50"] = ta.ema(data["Close"], length=50)
data["RSI14"] = ta.rsi(data["Close"], length=14)

print(data[["Close", "EMA50", "RSI14"]].tail(10))