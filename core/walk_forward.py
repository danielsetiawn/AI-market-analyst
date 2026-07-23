"""
Walk-forward validation: geser window test ke depan berulang kali,
biar kita tau strategi konsisten across banyak periode - bukan cuma
kebetulan bagus di 1 split tertentu.
"""

import pandas as pd
from core.backtest import run_backtest


def walk_forward_validate(
    data: pd.DataFrame,
    test_window_days: int = 60,
    step_days: int = 60,
    buffer_days: int = 200,
    min_agree: float = 1.5,
    use_dynamic_risk: bool = True,
) -> list[dict]:
    results = []
    start = buffer_days

    while start + test_window_days <= len(data):
        window_with_buffer = data.iloc[start - buffer_days : start + test_window_days]
        test_start_date = data.index[start]
        test_end_date = data.index[start + test_window_days - 1]

        bnh_return = (
            data["Close"].iloc[start + test_window_days - 1] / data["Close"].iloc[start] - 1
        ) * 100

        result = run_backtest(
            window_with_buffer,
            min_agree=min_agree,
            warmup=buffer_days,
            use_dynamic_risk=use_dynamic_risk,
        )

        results.append({
            "test_start": test_start_date.date(),
            "test_end": test_end_date.date(),
            "strategy_return_pct": result["total_return_pct"],
            "buy_hold_return_pct": round(bnh_return, 1),
            "outperformance_pp": round(result["total_return_pct"] - bnh_return, 1),
            "trades": result["total_trades"],
            "win_rate_pct": result["win_rate_pct"],
        })

        start += step_days

    return results