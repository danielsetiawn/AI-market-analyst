"""
Confluence layer: ngumpulin sinyal dari beberapa metode teknikal
independen, DIBOBOTI sesuai regime market saat itu, dan nentuin
apakah "cukup setuju" buat dianggap valid.
"""

from core.technical_analysis import ALL_METHODS
from core.regime import detect_regime

# Bobot tiap metode per regime. TRENDING methods lebih dipercaya saat
# trending, MEAN REVERSION (bollinger) lebih dipercaya saat sideways.
REGIME_WEIGHTS = {
    "TRENDING_UP": {
        "ema_rsi_pullback": 1.5,
        "macd_crossover": 1.5,
        "bollinger_squeeze": 0.5,
        "support_resistance_breakout": 1.2,
    },
    "TRENDING_DOWN": {
        "ema_rsi_pullback": 1.5,
        "macd_crossover": 1.5,
        "bollinger_squeeze": 0.5,
        "support_resistance_breakout": 1.2,
    },
    "SIDEWAYS": {
        "ema_rsi_pullback": 0.5,
        "macd_crossover": 0.5,
        "bollinger_squeeze": 1.8,
        "support_resistance_breakout": 0.7,
    },
    "UNKNOWN": {
        # Kalau regime gak diketahui, semua bobot normal - gak ada preferensi
        "ema_rsi_pullback": 1.0,
        "macd_crossover": 1.0,
        "bollinger_squeeze": 1.0,
        "support_resistance_breakout": 1.0,
    },
}


def evaluate_confluence(data, min_agree: int = 2, use_regime_weighting: bool = True) -> dict:
    """
    Jalanin semua metode, BOBOTI berdasarkan regime (kalau diaktifkan),
    dan tentuin sinyal final berdasarkan threshold min_agree.

    min_agree sekarang dihitung dari WEIGHTED VOTE, bukan cuma jumlah
    metode - metode dengan bobot tinggi "bernilai lebih" dari 1 vote.
    """
    results = [method(data) for method in ALL_METHODS]

    if use_regime_weighting:
        regime_info = detect_regime(data)
        regime = regime_info["regime"]
        weights = REGIME_WEIGHTS.get(regime, REGIME_WEIGHTS["UNKNOWN"])
    else:
        regime_info = {"regime": "DISABLED"}
        weights = {r["method"]: 1.0 for r in results}

    buy_weight = sum(weights.get(r["method"], 1.0) for r in results if r["signal"] == "BUY")
    sell_weight = sum(weights.get(r["method"], 1.0) for r in results if r["signal"] == "SELL")

    if buy_weight >= min_agree and buy_weight > sell_weight:
        final_signal = "BUY"
        agreeing = [r for r in results if r["signal"] == "BUY"]
    elif sell_weight >= min_agree and sell_weight > buy_weight:
        final_signal = "SELL"
        agreeing = [r for r in results if r["signal"] == "SELL"]
    else:
        final_signal = "HOLD"
        agreeing = []

    avg_confidence = (
        sum(r["confidence"] for r in agreeing) / len(agreeing)
        if agreeing else 0.0
    )

    return {
        "final_signal": final_signal,
        "confidence": round(avg_confidence, 1),
        "regime": regime_info["regime"],
        "buy_weight": round(buy_weight, 2),
        "sell_weight": round(sell_weight, 2),
        "all_results": results,
        "min_agree_threshold": min_agree,
    }