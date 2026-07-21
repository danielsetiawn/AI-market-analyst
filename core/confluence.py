"""
Confluence layer: ngumpulin sinyal dari beberapa metode teknikal
independen, dan nentuin apakah "cukup setuju" buat dianggap valid.
"""

from core.technical_analysis import ALL_METHODS


def evaluate_confluence(data, min_agree: int = 2) -> dict:
    """
    Jalanin semua metode, hitung berapa yang setuju BUY vs SELL,
    dan tentuin sinyal final berdasarkan threshold min_agree.
    """
    results = [method(data) for method in ALL_METHODS]

    buy_votes = [r for r in results if r["signal"] == "BUY"]
    sell_votes = [r for r in results if r["signal"] == "SELL"]

    buy_count = len(buy_votes)
    sell_count = len(sell_votes)

    if buy_count >= min_agree and buy_count > sell_count:
        final_signal = "BUY"
        agreeing = buy_votes
    elif sell_count >= min_agree and sell_count > buy_count:
        final_signal = "SELL"
        agreeing = sell_votes
    else:
        final_signal = "HOLD"
        agreeing = []

    # Confidence final = rata-rata confidence dari metode yang setuju
    avg_confidence = (
        sum(r["confidence"] for r in agreeing) / len(agreeing)
        if agreeing else 0.0
    )

    return {
        "final_signal": final_signal,
        "confidence": round(avg_confidence, 1),
        "votes": {"BUY": buy_count, "SELL": sell_count, "HOLD": len(results) - buy_count - sell_count},
        "all_results": results,
        "min_agree_threshold": min_agree,
    }