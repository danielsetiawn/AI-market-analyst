import yfinance as yf
from core.backtest import run_backtest

data = yf.download("BTC-USD", period="2y", interval="1d")
data.columns = data.columns.get_level_values(0)

result = run_backtest(
    data, min_agree=1, fee_pct=0.001, slippage_pct=0.001,
    warmup=50, stop_loss_pct=0.03, take_profit_pct=0.06,
)

print("=== BACKTEST RESULT (BTC-USD, 2 tahun, dengan SL/TP) ===")
print("Total trades   :", result["total_trades"])
print("Win rate       :", result["win_rate_pct"], "%")
print("Total return   :", result["total_return_pct"], "%")
print("Max drawdown   :", result["max_drawdown_pct"], "%")
print("Sharpe ratio   :", result["sharpe_ratio"])
print("\n--- Detail 5 trade pertama ---")
for t in result["trades"][:5]:
    print(t)