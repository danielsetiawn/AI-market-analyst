import yfinance as yf
from core.technical_analysis import ALL_METHODS

data = yf.download("BTC-USD", period="6mo", interval="1d")
data.columns = data.columns.get_level_values(0)

for method in ALL_METHODS:
    result = method(data)
    print(f"[{result['method']}] {result['signal']} ({result['confidence']}%) - {result['detail']}")