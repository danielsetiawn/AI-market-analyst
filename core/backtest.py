"""
Backtest engine: jalanin confluence rules terhadap seluruh history,
hari per hari, tanpa lookahead bias. Fee & slippage diperhitungkan.
"""

import pandas as pd
from core.confluence import evaluate_confluence
from core.risk_sizing import calculate_dynamic_risk_params

def run_backtest(
    data: pd.DataFrame,
    min_agree: float = 1.5,
    fee_pct: float = 0.001,
    slippage_pct: float = 0.001,
    warmup: int = 50,
    use_dynamic_risk: bool = True,
    stop_loss_pct: float = 0.03,             # dipakai HANYA kalau use_dynamic_risk=False
    trailing_activation_pct: float = 0.05,
    trailing_stop_pct: float = 0.04,
) -> dict:
    position = None
    trades = []
    equity = 1.0
    equity_curve = []

    for i in range(warmup, len(data)):
        window = data.iloc[: i + 1]
        today = window.iloc[-1]

        # Hitung risk params: dinamis (ATR-based) atau fixed, sesuai flag
        if use_dynamic_risk:
            risk_params = calculate_dynamic_risk_params(window)
            current_sl = risk_params["stop_loss_pct"]
            current_trail_activation = risk_params["trailing_activation_pct"]
            current_trail_stop = risk_params["trailing_stop_pct"]
        else:
            current_sl = stop_loss_pct
            current_trail_activation = trailing_activation_pct
            current_trail_stop = trailing_stop_pct

        if position is not None:
            current_price = today["Close"]

            if current_price > position["highest_price"]:
                position["highest_price"] = current_price

            change_from_entry = (current_price - position["entry_price"]) / position["entry_price"]
            change_from_peak = (current_price - position["highest_price"]) / position["highest_price"]

            forced_exit_reason = None
            if change_from_entry <= -current_sl:
                forced_exit_reason = "stop_loss"
            elif change_from_entry >= current_trail_activation and change_from_peak <= -current_trail_stop:
                forced_exit_reason = "trailing_stop"

            if forced_exit_reason:
                exit_price = current_price * (1 - slippage_pct)
                trade_return = (exit_price - position["entry_price"]) / position["entry_price"]
                equity *= (1 + trade_return) * (1 - fee_pct)
                trades.append({
                    "entry_date": position["entry_date"],
                    "exit_date": today.name,
                    "entry_price": position["entry_price"],
                    "exit_price": exit_price,
                    "return_pct": round(trade_return * 100, 2),
                    "exit_reason": forced_exit_reason,
                })
                position = None
                equity_curve.append({"date": today.name, "equity": equity})
                continue

        signal_result = evaluate_confluence(window, min_agree=min_agree, use_regime_weighting=True)
        signal = signal_result["final_signal"]

        if position is None and signal == "BUY":
            entry_price = today["Close"] * (1 + slippage_pct)
            position = {
                "entry_date": today.name,
                "entry_price": entry_price,
                "highest_price": entry_price,
            }
            equity *= (1 - fee_pct)

        elif position is not None and signal == "SELL":
            exit_price = today["Close"] * (1 - slippage_pct)
            trade_return = (exit_price - position["entry_price"]) / position["entry_price"]
            equity *= (1 + trade_return) * (1 - fee_pct)
            trades.append({
                "entry_date": position["entry_date"],
                "exit_date": today.name,
                "entry_price": position["entry_price"],
                "exit_price": exit_price,
                "return_pct": round(trade_return * 100, 2),
                "exit_reason": "confluence_sell",
            })
            position = None

        equity_curve.append({"date": today.name, "equity": equity})

    return _summarize(trades, equity_curve)

def split_train_test(data: pd.DataFrame, train_ratio: float = 0.7, buffer_days: int = 200):
    """
    Split kronologis, TAPI test_data dikasih buffer historis di depannya
    (data sebelum split point) biar indikator long-term (EMA200) punya
    cukup histori sejak awal window test - bukan cuma dari 0.

    Trading evaluation tetap cuma dihitung mulai split_idx, tapi backtest
    engine akan punya akses "look-back" yang cukup lewat buffer ini.
    """
    split_idx = int(len(data) * train_ratio)
    train_data = data.iloc[:split_idx]

    buffer_start = max(0, split_idx - buffer_days)
    test_data_with_buffer = data.iloc[buffer_start:]

    return train_data, test_data_with_buffer, split_idx - buffer_start

def _summarize(trades: list, equity_curve: list) -> dict:
    if not trades:
        return {
            "total_trades": 0,
            "win_rate_pct": 0.0,
            "total_return_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe_ratio": 0.0,
            "trades": [],
        }

    equity_df = pd.DataFrame(equity_curve).set_index("date")
    daily_returns = equity_df["equity"].pct_change().dropna()

    wins = [t for t in trades if t["return_pct"] > 0]
    win_rate = len(wins) / len(trades) * 100

    running_max = equity_df["equity"].cummax()
    drawdown = (equity_df["equity"] - running_max) / running_max
    max_drawdown = drawdown.min() * 100

    # Sharpe ratio disederhanakan: rata-rata return harian / std, annualized
    sharpe = 0.0
    if daily_returns.std() > 0:
        sharpe = (daily_returns.mean() / daily_returns.std()) * (252 ** 0.5)

    total_return = (equity_df["equity"].iloc[-1] - 1.0) * 100

    return {
        "total_trades": len(trades),
        "win_rate_pct": round(win_rate, 1),
        "total_return_pct": round(total_return, 1),
        "max_drawdown_pct": round(max_drawdown, 1),
        "sharpe_ratio": round(sharpe, 2),
        "trades": trades,
    }

    