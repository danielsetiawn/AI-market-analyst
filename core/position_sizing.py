"""
Fixed fractional position sizing: risk per trade dijaga konstan
(sebagai % dari modal), position size dihitung mundur dari situ
berdasarkan jarak stop-loss (yang sekarang ATR-based, adaptif per aset).

Ini prinsip standar quant/prop desk - bukan "alokasikan X% modal ke
tiap trade", tapi "rugi maksimal Y% modal per trade kalau salah".
"""


def calculate_position_size(
    capital: float,
    stop_loss_pct: float,
    risk_per_trade_pct: float = 0.01,
    max_position_pct: float = 0.25,
) -> dict:
    """
    max_position_pct: hard cap - berapapun hasil kalkulasi, gak boleh
    lebih dari ini (proteksi kalau stop_loss_pct kebetulan sangat kecil,
    yang bisa menghasilkan position size tidak realistis besar).
    """
    if stop_loss_pct <= 0:
        raise ValueError("stop_loss_pct harus > 0")

    risk_amount = capital * risk_per_trade_pct
    raw_position_size = risk_amount / stop_loss_pct

    position_pct_of_capital = raw_position_size / capital
    capped_pct = min(position_pct_of_capital, max_position_pct)

    final_position_size = capital * capped_pct
    was_capped = position_pct_of_capital > max_position_pct

    return {
        "position_size": round(final_position_size, 2),
        "position_pct_of_capital": round(capped_pct * 100, 2),
        "risk_amount": round(risk_amount, 2),
        "was_capped": was_capped,
    }