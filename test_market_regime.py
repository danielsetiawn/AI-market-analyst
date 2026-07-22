import yfinance as yf

data = yf.download("BTC-USD", period="2y", interval="1d")
data.columns = data.columns.get_level_values(0)

from core.backtest import split_train_test
train_data, test_data = split_train_test(data, train_ratio=0.7)

# Buy-and-hold return: apa yang terjadi kalau kita cuma beli di awal
# dan pegang terus tanpa strategi apapun, buat jadi pembanding "baseline"
train_bnh = (train_data["Close"].iloc[-1] / train_data["Close"].iloc[0] - 1) * 100
test_bnh = (test_data["Close"].iloc[-1] / test_data["Close"].iloc[0] - 1) * 100

print("=== BUY & HOLD BASELINE ===")
print(f"Train period buy-and-hold: {train_bnh:.1f}%")
print(f"Test period buy-and-hold : {test_bnh:.1f}%")

print(f"\nTrain price: {train_data['Close'].iloc[0]:.0f} -> {train_data['Close'].iloc[-1]:.0f}")
print(f"Test price : {test_data['Close'].iloc[0]:.0f} -> {test_data['Close'].iloc[-1]:.0f}")

print(f"\nTrain highest: {train_data['Close'].max():.0f}, lowest: {train_data['Close'].min():.0f}")
print(f"Test highest : {test_data['Close'].max():.0f}, lowest: {test_data['Close'].min():.0f}")