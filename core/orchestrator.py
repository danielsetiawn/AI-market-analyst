"""
Orchestrator formal: 1 titik masuk untuk jalankan pipeline lengkap
(Research -> Strategy -> Desk Manager) untuk 1 ticker, tanpa perlu
nulis script test manual tiap kali.
"""

from agents.research_agent import ResearchAgent
from agents.strategy_agent import StrategyAnalystAgent
from agents.desk_manager_agent import DeskManagerAgent


class MarketAnalystPipeline:
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.strategy_agent = StrategyAnalystAgent()
        self.desk_manager = DeskManagerAgent()

    def analyze(self, ticker: str, raw_context: str, capital: float) -> dict:
        """
        Jalankan pipeline lengkap untuk 1 ticker.
        Return dict berisi hasil tiap tahap + keputusan final.
        """
        research = self.research_agent.run(ticker=ticker, raw_context=raw_context)
        strategy = self.strategy_agent.run(research)
        decision = self.desk_manager.run(strategy, capital=capital)

        return {
            "ticker": ticker,
            "research": research,
            "strategy": strategy,
            "decision": decision,
        }

    def print_summary(self, result: dict) -> None:
        """Tampilkan ringkasan hasil pipeline dengan format yang konsisten."""
        r, s, d = result["research"], result["strategy"], result["decision"]

        print(f"\n{'='*60}")
        print(f"TICKER: {result['ticker']}")
        print(f"{'='*60}")
        print(f"[Research]  Sentiment: {r['sentiment_score']}, Summary: {r['summary']}")
        print(f"[Strategy]  LLM+Confluence: {s['proposed_action']} "
              f"(technical={s['technical_signal']}, regime={s['technical_regime']}, "
              f"confirmed={s['backtest_passed']})")
        print(f"[Decision]  Status: {d['status']}")
        if d["status"] == "APPROVED":
            print(f"            Position: ${d['position_size']} ({d['position_pct_of_capital']}% modal)")
        print(f"            Reasoning: {d['reasoning']}")
        print(f"{'='*60}\n")