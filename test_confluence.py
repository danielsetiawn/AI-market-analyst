import yfinance as yf
from core.confluence import evaluate_confluence

data = yf.download("BTC-USD", period="2y", interval="1d")
data.columns = data.columns.get_level_values(0)

result = evaluate_confluence(data, min_agree=1.5, use_regime_weighting=True)

print("=== CONFLUENCE RESULT (regime-weighted) ===")
print("Regime:", result["regime"])
print("Final signal:", result["final_signal"])
print("Confidence:", result["confidence"], "%")
print("Buy weight:", result["buy_weight"], "| Sell weight:", result["sell_weight"])