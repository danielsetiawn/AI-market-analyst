import yfinance as yf
from core.backtest import split_train_test
from core.regime import detect_regime

data = yf.download("BTC-USD", period="2y", interval="1d")
data.columns = data.columns.get_level_values(0)

train_data, test_data, warmup_offset = split_train_test(data, train_ratio=0.7, buffer_days=200)

print(f"Test data length (dengan buffer): {len(test_data)}, warmup_offset: {warmup_offset}")

def scan_regimes(dataset, label, start_from=0, step=15):
    print(f"\n=== SCAN REGIME SEPANJANG {label} ===")
    counts = {"TRENDING_UP": 0, "TRENDING_DOWN": 0, "SIDEWAYS": 0, "UNKNOWN": 0}
    for i in range(max(200, start_from), len(dataset), step):
        window = dataset.iloc[:i+1]
        result = detect_regime(window)
        counts[result["regime"]] += 1
    print(counts)

scan_regimes(train_data, "TRAIN (bull, +30.5%)")
scan_regimes(test_data, "TEST dengan buffer (bear, -23.8%)", start_from=warmup_offset)