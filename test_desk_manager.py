from agents.research_agent import ResearchAgent
from agents.strategy_agent import StrategyAnalystAgent
from agents.desk_manager_agent import DeskManagerAgent

research_agent = ResearchAgent()
strategy_agent = StrategyAnalystAgent()
desk_manager = DeskManagerAgent()

research = research_agent.run(
    ticker="ETH-USD",
    raw_context=(
        "Ethereum menunjukkan momentum kuat setelah upgrade jaringan terbaru, "
        "dengan volume transaksi naik signifikan dalam sebulan terakhir."
    ),
)
print("=== Research ===")
print(research["summary"])
print("Sentiment:", research["sentiment_score"])

strategy = strategy_agent.run(research)
print("\n=== Strategy (Engine A + Engine B combined) ===")
print("LLM proposed vs final:", strategy["proposed_action"])
print("Technical signal      :", strategy["technical_signal"])
print("Regime                :", strategy["technical_regime"])
print("Backtest passed       :", strategy["backtest_passed"])
print("Rationale             :", strategy["rationale"])

decision = desk_manager.run(strategy, capital=10_000)
print("\n=== FULL PIPELINE RESULT ===")
print("Status               :", decision["status"])
print("Position size        : $", decision["position_size"])
print("Position % of capital:", decision["position_pct_of_capital"], "%")
print("Reasoning            :", decision["reasoning"])