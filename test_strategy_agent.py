from agents.research_agent import ResearchAgent
from agents.strategy_agent import StrategyAnalystAgent

research_agent = ResearchAgent()
strategy_agent = StrategyAnalystAgent()

research = research_agent.run(
    ticker="BBCA.JK",
    raw_context=(
        "Bank BCA melaporkan kenaikan laba bersih kuartalan sebesar 8% YoY. "
        "Beberapa analis menyoroti potensi perlambatan pertumbuhan kredit "
        "di sektor konsumer pada kuartal berikutnya."
    ),
)
print("=== Research Output ===")
print(research)

strategy = strategy_agent.run(research)
print("\n=== Strategy Output ===")
print("Hypothesis:", strategy["hypothesis"])
print("Proposed action (final):", strategy["proposed_action"])
print("Backtest passed:", strategy["backtest_passed"])
print("Rationale:", strategy["rationale"])