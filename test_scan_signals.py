import yfinance as yf
from core.confluence import evaluate_confluence

tickers = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"]

for ticker in tickers:
    data = yf.download(ticker, period="2y", interval="1d", progress=False)
    data.columns = data.columns.get_level_values(0)
    result = evaluate_confluence(data, min_agree=1.5, use_regime_weighting=True)
    print(f"{ticker:<10} regime={result['regime']:<15} signal={result['final_signal']:<6} confidence={result['confidence']}%")