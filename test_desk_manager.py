from agents.research_agent import ResearchAgent
from agents.strategy_agent import StrategyAnalystAgent
from agents.desk_manager_agent import DeskManagerAgent

research_agent = ResearchAgent()
strategy_agent = StrategyAnalystAgent()
desk_manager = DeskManagerAgent()

research = research_agent.run(
    ticker="BBCA.JK",
    raw_context=(
        "Bank BCA melaporkan kenaikan laba bersih kuartalan sebesar 8% YoY. "
        "Beberapa analis menyoroti potensi perlambatan pertumbuhan kredit "
        "di sektor konsumer pada kuartal berikutnya."
    ),
)
strategy = strategy_agent.run(research)
decision = desk_manager.run(strategy)

print("=== FULL PIPELINE RESULT ===")
print("Ticker         :", decision["ticker"])
print("Action         :", decision["action"])
print("Status         :", decision["status"])
print("Position size  :", decision["position_size_pct"], "%")
print("Reasoning      :", decision["reasoning"])