import yfinance as yf
from core.confluence import evaluate_confluence

data = yf.download("BTC-USD", period="2y", interval="1d", progress=False)
data.columns = data.columns.get_level_values(0)

print("Scanning semua hari, cari yang bukan HOLD...")
found = 0
for i in range(200, len(data)):
    window = data.iloc[:i+1]
    result = evaluate_confluence(window, min_agree=1.5, use_regime_weighting=True)
    if result["final_signal"] != "HOLD":
        date = window.index[-1].date()
        print(f"{date}: regime={result['regime']:<15} signal={result['final_signal']:<6} confidence={result['confidence']}%")
        found += 1

print(f"\nTotal hari dengan sinyal non-HOLD: {found} dari {len(data)-200} hari yang di-scan")