import yfinance as yf
from core.confluence import evaluate_confluence

data = yf.download("BTC-USD", period="6mo", interval="1d")
data.columns = data.columns.get_level_values(0)

result = evaluate_confluence(data, min_agree=2)

print("=== CONFLUENCE RESULT ===")
print("Final signal:", result["final_signal"])
print("Confidence:", result["confidence"], "%")
print("Votes:", result["votes"])
print("\nDetail tiap metode:")
for r in result["all_results"]:
    print(f"  [{r['method']}] {r['signal']} ({r['confidence']}%) - {r['detail']}")