"""
Regime detection: klasifikasi kondisi market jadi TRENDING_UP,
TRENDING_DOWN, atau SIDEWAYS - berdasarkan ADX (kekuatan trend)
dan arah EMA.

Prinsip: bukan buat "menang di semua kondisi", tapi buat TAU KAPAN
strategi tertentu gak cocok dipakai, dan sebaiknya diam.
"""

import pandas as pd
import pandas_ta as ta


def detect_regime(data: pd.DataFrame, adx_threshold: float = 25.0) -> dict:
    if len(data) < 200:
        return {"regime": "UNKNOWN", "adx": None, "detail": "Data kurang dari 200 hari, EMA200 belum bisa dihitung"}
    
    adx_df = ta.adx(data["High"], data["Low"], data["Close"], length=14)
    adx_col = [c for c in adx_df.columns if c.startswith("ADX_")][0]
    last_adx = adx_df[adx_col].iloc[-1]

    ema50 = ta.ema(data["Close"], length=50)
    ema200 = ta.ema(data["Close"], length=200)

    last_close = data["Close"].iloc[-1]
    last_ema50 = ema50.iloc[-1]

    ema50_slope = ema50.iloc[-1] - ema50.iloc[-6]

    if pd.isna(last_adx) or pd.isna(ema50_slope) or pd.isna(ema200.iloc[-1]):
        return {"regime": "UNKNOWN", "adx": None, "detail": "Data belum cukup buat hitung regime"}

    # Long-term trend confirmation: posisi harga relatif ke EMA200
    long_term_bullish = last_close > ema200.iloc[-1]

    is_trending_short = last_adx > adx_threshold
    short_term_up = last_close > last_ema50 and ema50_slope > 0
    short_term_down = last_close < last_ema50 and ema50_slope < 0

    # Regime final: gabungan konfirmasi jangka pendek (ADX+EMA50) DAN
    # arah besar (EMA200). Kalau dua-duanya sepakat, baru dianggap trending.
    if is_trending_short and short_term_up and long_term_bullish:
        regime = "TRENDING_UP"
    elif is_trending_short and short_term_down and not long_term_bullish:
        regime = "TRENDING_DOWN"
    elif is_trending_short and short_term_up and not long_term_bullish:
        # Trend jangka pendek naik tapi arah besar masih bearish -> anggap
        # ini bounce sementara, bukan trend baru. Lebih aman disebut SIDEWAYS.
        regime = "SIDEWAYS"
    elif is_trending_short and short_term_down and long_term_bullish:
        # Koreksi sementara di tengah bull market besar -> juga SIDEWAYS,
        # bukan TRENDING_DOWN penuh.
        regime = "SIDEWAYS"
    else:
        regime = "SIDEWAYS"

    return {
        "regime": regime,
        "adx": round(last_adx, 1),
        "long_term_bullish": long_term_bullish,
        "detail": f"ADX={last_adx:.1f}, short-term {'up' if short_term_up else 'down' if short_term_down else 'flat'}, "
                   f"long-term {'bullish' if long_term_bullish else 'bearish'} (vs EMA200)",
    }