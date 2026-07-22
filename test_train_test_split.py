import yfinance as yf
from core.backtest import run_backtest, split_train_test

data = yf.download("BTC-USD", period="2y", interval="1d")
data.columns = data.columns.get_level_values(0)

train_data, test_data = split_train_test(data, train_ratio=0.7)

print(f"Train period: {train_data.index[0].date()} s.d. {train_data.index[-1].date()} ({len(train_data)} hari)")
print(f"Test period : {test_data.index[0].date()} s.d. {test_data.index[-1].date()} ({len(test_data)} hari)")

print("\n=== HASIL DI TRAIN DATA ===")
train_result = run_backtest(train_data, min_agree=1, warmup=50, stop_loss_pct=0.03, take_profit_pct=0.06)
print("Total trades:", train_result["total_trades"])
print("Win rate    :", train_result["win_rate_pct"], "%")
print("Total return:", train_result["total_return_pct"], "%")
print("Sharpe      :", train_result["sharpe_ratio"])

print("\n=== HASIL DI TEST DATA (belum pernah 'dilihat') ===")
test_result = run_backtest(test_data, min_agree=1, warmup=50, stop_loss_pct=0.03, take_profit_pct=0.06)
print("Total trades:", test_result["total_trades"])
print("Win rate    :", test_result["win_rate_pct"], "%")
print("Total return:", test_result["total_return_pct"], "%")
print("Sharpe      :", test_result["sharpe_ratio"])