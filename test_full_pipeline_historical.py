import yfinance as yf
from agents.research_agent import ResearchAgent
from agents.strategy_agent import StrategyAnalystAgent
from agents.desk_manager_agent import DeskManagerAgent

# Override _fetch_price_data supaya pakai data "seolah-olah" tanggal 2025-11-04
TARGET_DATE = "2025-11-04"

def fetch_historical(self, ticker):
    data = yf.download(ticker, period="2y", interval="1d", progress=False)
    data.columns = data.columns.get_level_values(0)
    return data[data.index <= TARGET_DATE]

StrategyAnalystAgent._fetch_price_data = fetch_historical

research_agent = ResearchAgent()
strategy_agent = StrategyAnalystAgent()
desk_manager = DeskManagerAgent()

# Research context yang MENDUKUNG arah BUY, biar konsisten sama technical signal
research = research_agent.run(
    ticker="BTC-USD",
    raw_context=(
        "Bitcoin menunjukkan akumulasi oleh investor institusional dalam beberapa "
        "minggu terakhir, dengan inflow ke ETF Bitcoin mencatat rekor bulanan."
    ),
)
print("=== Research ===")
print(research["summary"])
print("Sentiment:", research["sentiment_score"])

strategy = strategy_agent.run(research)
print("\n=== Strategy (Engine A + Engine B combined) ===")
print("Final action     :", strategy["proposed_action"])
print("Technical signal  :", strategy["technical_signal"])
print("Regime            :", strategy["technical_regime"])
print("Backtest passed   :", strategy["backtest_passed"])
print("Rationale         :", strategy["rationale"])

decision = desk_manager.run(strategy, capital=10_000)
print("\n=== FULL PIPELINE RESULT ===")
print("Status               :", decision["status"])
print("Position size        : $", decision["position_size"])
print("Position % of capital:", decision["position_pct_of_capital"], "%")
print("Reasoning            :", decision["reasoning"])