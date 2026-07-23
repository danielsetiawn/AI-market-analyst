"""
Entry point utama. Jalankan: python main.py

Untuk sekarang, raw_context masih manual per ticker (RSS/scraping
otomatis masih di to-do list). Modal & watchlist bisa disesuaikan
di bagian bawah file ini.
"""

from core.orchestrator import MarketAnalystPipeline

CAPITAL = 10_000

WATCHLIST = [
    {
        "ticker": "BTC-USD",
        "raw_context": (
            "Bitcoin menunjukkan konsolidasi harga dalam beberapa minggu "
            "terakhir, dengan volume trading yang relatif stabil."
        ),
    },
    {
        "ticker": "ETH-USD",
        "raw_context": (
            "Ethereum mengalami peningkatan aktivitas developer di ekosistemnya, "
            "meski harga belum menunjukkan pergerakan signifikan."
        ),
    },
]


def main():
    pipeline = MarketAnalystPipeline()

    for item in WATCHLIST:
        result = pipeline.analyze(
            ticker=item["ticker"],
            raw_context=item["raw_context"],
            capital=CAPITAL,
        )
        pipeline.print_summary(result)


if __name__ == "__main__":
    main()