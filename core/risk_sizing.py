"""
ATR-based dynamic risk parameters. Menggantikan fixed stop-loss/trailing
percentage dengan yang otomatis menyesuaikan volatilitas TERKINI dari
aset yang dianalisis - baik itu perbedaan antar-aset (BTC vs ETH) maupun
perbedaan waktu (aset yang sama saat quiet vs saat volatile).
"""

import pandas as pd
import pandas_ta as ta


def calculate_dynamic_risk_params(
    data: pd.DataFrame,
    stop_loss_atr_multiplier: float = 0.8,
    trailing_activation_atr_multiplier: float = 1.5,
    trailing_stop_atr_multiplier: float = 1.2,
    atr_length: int = 14,
) -> dict:
    """
    Return stop-loss/trailing sebagai PERSENTASE dari harga saat ini,
    dihitung dari ATR terkini - bukan angka tetap.
    """
    atr = ta.atr(data["High"], data["Low"], data["Close"], length=atr_length)
    last_atr = atr.iloc[-1]
    last_close = data["Close"].iloc[-1]

    if pd.isna(last_atr):
        # Fallback konservatif kalau ATR belum bisa dihitung (data kurang)
        return {
            "stop_loss_pct": 0.03,
            "trailing_activation_pct": 0.05,
            "trailing_stop_pct": 0.04,
            "atr_pct": None,
        }

    atr_pct = last_atr / last_close

    return {
        "stop_loss_pct": round(atr_pct * stop_loss_atr_multiplier, 4),
        "trailing_activation_pct": round(atr_pct * trailing_activation_atr_multiplier, 4),
        "trailing_stop_pct": round(atr_pct * trailing_stop_atr_multiplier, 4),
        "atr_pct": round(atr_pct * 100, 2),
    }