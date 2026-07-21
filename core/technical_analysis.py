"""
4 metode technical analysis independen. Masing-masing menganalisis
data OHLCV dan return sinyal + confidence sendiri-sendiri, TANPA
tahu metode lain bilang apa. Voting/confluence dihitung di layer
terpisah (belum di file ini).
"""

import pandas as pd
import pandas_ta as ta


def method_ema_rsi_pullback(data: pd.DataFrame) -> dict:
    """Trend filter EMA50 + entry saat RSI oversold di tengah uptrend."""
    close = data["Close"]
    ema50 = ta.ema(close, length=50)
    rsi14 = ta.rsi(close, length=14)

    last_close = close.iloc[-1]
    last_ema = ema50.iloc[-1]
    last_rsi = rsi14.iloc[-1]

    uptrend = last_close > last_ema

    if uptrend and last_rsi < 30:
        return {"method": "ema_rsi_pullback", "signal": "BUY", "confidence": 75.0,
                "detail": f"Uptrend (Close>{last_ema:.0f}) + RSI oversold ({last_rsi:.1f})"}
    if not uptrend and last_rsi > 70:
        return {"method": "ema_rsi_pullback", "signal": "SELL", "confidence": 70.0,
                "detail": f"Downtrend + RSI overbought ({last_rsi:.1f})"}
    return {"method": "ema_rsi_pullback", "signal": "HOLD", "confidence": 50.0,
            "detail": f"Tidak ada kondisi pullback jelas (RSI={last_rsi:.1f})"}


def method_macd_crossover(data: pd.DataFrame) -> dict:
    """Sinyal saat MACD line cross signal line."""
    macd_df = ta.macd(data["Close"])
    macd_line = macd_df["MACD_12_26_9"]
    signal_line = macd_df["MACDs_12_26_9"]

    prev_diff = macd_line.iloc[-2] - signal_line.iloc[-2]
    curr_diff = macd_line.iloc[-1] - signal_line.iloc[-1]

    if prev_diff < 0 and curr_diff > 0:
        return {"method": "macd_crossover", "signal": "BUY", "confidence": 65.0,
                "detail": "MACD baru cross ke atas signal line (bullish crossover)"}
    if prev_diff > 0 and curr_diff < 0:
        return {"method": "macd_crossover", "signal": "SELL", "confidence": 65.0,
                "detail": "MACD baru cross ke bawah signal line (bearish crossover)"}
    return {"method": "macd_crossover", "signal": "HOLD", "confidence": 40.0,
            "detail": "Tidak ada crossover baru"}


def method_bollinger_squeeze(data: pd.DataFrame) -> dict:
    """Mean reversion: sinyal saat harga nyentuh band bawah/atas."""
    bbands = ta.bbands(data["Close"], length=20)
    lower = bbands["BBL_20_2.0_2.0"].iloc[-1]
    upper = bbands["BBU_20_2.0_2.0"].iloc[-1]
    last_close = data["Close"].iloc[-1]

    if last_close <= lower:
        return {"method": "bollinger_squeeze", "signal": "BUY", "confidence": 60.0,
                "detail": f"Close ({last_close:.0f}) nyentuh/lewat lower band ({lower:.0f})"}
    if last_close >= upper:
        return {"method": "bollinger_squeeze", "signal": "SELL", "confidence": 60.0,
                "detail": f"Close ({last_close:.0f}) nyentuh/lewat upper band ({upper:.0f})"}
    return {"method": "bollinger_squeeze", "signal": "HOLD", "confidence": 45.0,
            "detail": "Harga masih di dalam band"}


def method_support_resistance_breakout(data: pd.DataFrame, lookback: int = 20) -> dict:
    """Sinyal saat harga breakout dari level resistance/support historis."""
    recent = data.iloc[-lookback:-1]  # exclude hari ini biar gak "curang"
    resistance = recent["High"].max()
    support = recent["Low"].min()
    last_close = data["Close"].iloc[-1]

    if last_close > resistance:
        return {"method": "support_resistance_breakout", "signal": "BUY", "confidence": 70.0,
                "detail": f"Close ({last_close:.0f}) breakout resistance ({resistance:.0f})"}
    if last_close < support:
        return {"method": "support_resistance_breakout", "signal": "SELL", "confidence": 70.0,
                "detail": f"Close ({last_close:.0f}) breakdown support ({support:.0f})"}
    return {"method": "support_resistance_breakout", "signal": "HOLD", "confidence": 45.0,
            "detail": f"Harga masih di range {support:.0f}-{resistance:.0f}"}


ALL_METHODS = [
    method_ema_rsi_pullback,
    method_macd_crossover,
    method_bollinger_squeeze,
    method_support_resistance_breakout,
]