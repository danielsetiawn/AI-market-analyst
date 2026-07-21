import yfinance as yf

data = yf.download("BTC-USD", period="6mo", interval="1d")
print(data.head())
print("\nJumlah baris data:", len(data))
print("Kolom:", list(data.columns))