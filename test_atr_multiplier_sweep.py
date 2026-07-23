import yfinance as yf
from core.walk_forward import walk_forward_validate
from core.backtest import run_backtest
from core.risk_sizing import calculate_dynamic_risk_params
import core.backtest as backtest_module

data = yf.download("ETH-USD", period="2y", interval="1d")
data.columns = data.columns.get_level_values(0)

# Coba beberapa kombinasi multiplier ATR
multiplier_sets = [
    {"sl": 0.5, "trail_act": 1.0, "trail_stop": 0.8},
    {"sl": 0.8, "trail_act": 1.5, "trail_stop": 1.2},
    {"sl": 1.0, "trail_act": 1.8, "trail_stop": 1.5},
    {"sl": 1.5, "trail_act": 2.5, "trail_stop": 2.0},
]

for m in multiplier_sets:
    # Monkey-patch sementara buat testing cepat tanpa ubah file core
    original_fn = backtest_module.calculate_dynamic_risk_params
    def patched(window, **kwargs):
        return original_fn(
            window,
            stop_loss_atr_multiplier=m["sl"],
            trailing_activation_atr_multiplier=m["trail_act"],
            trailing_stop_atr_multiplier=m["trail_stop"],
        )
    backtest_module.calculate_dynamic_risk_params = patched

    results = walk_forward_validate(data, test_window_days=60, step_days=60, use_dynamic_risk=True)
    outperform = sum(1 for r in results if r["outperformance_pp"] > 0)
    avg_return = sum(r["strategy_return_pct"] for r in results) / len(results)
    worst = min(results, key=lambda r: r["outperformance_pp"])

    print(f"SL={m['sl']}x, TrailAct={m['trail_act']}x, TrailStop={m['trail_stop']}x -> "
          f"Outperform: {outperform}/8, Avg return: {avg_return:.1f}%, Worst gap: {worst['outperformance_pp']}pp")

    backtest_module.calculate_dynamic_risk_params = original_fn