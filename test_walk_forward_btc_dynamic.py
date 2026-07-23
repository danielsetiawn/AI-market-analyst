import yfinance as yf
from core.walk_forward import walk_forward_validate

data = yf.download("BTC-USD", period="2y", interval="1d")
data.columns = data.columns.get_level_values(0)

results = walk_forward_validate(data, test_window_days=60, step_days=60, use_dynamic_risk=True)

print(f"{'Periode':<25} {'Strategi':>10} {'Buy&Hold':>10} {'Outperform':>12} {'Trades':>8} {'WinRate':>8}")
for r in results:
    period = f"{r['test_start']} - {r['test_end']}"
    print(f"{period:<25} {r['strategy_return_pct']:>9}% {r['buy_hold_return_pct']:>9}% {r['outperformance_pp']:>11}pp {r['trades']:>8} {r['win_rate_pct']:>7}%")

outperform_count = sum(1 for r in results if r["outperformance_pp"] > 0)
print(f"\nOutperform: {outperform_count}/8 window")