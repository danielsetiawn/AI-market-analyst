"""
Strategy Analyst Agent: usulin hipotesis strategi dari hasil riset.

CATATAN PENTING: backtest engine beneran BELUM diimplementasikan.
Selama itu placeholder, proposed_action DIPAKSA jadi "HOLD" apapun
kata LLM - biar gak ada sinyal actionable yang keluar tanpa validasi
statistik asli. Ini prinsip dari dokumentasi awal proyek lo.
"""

from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """Kamu adalah Strategy Analyst Agent di sistem trading multi-agent.
Kamu menerima hasil riset (sentimen + temuan) tentang sebuah ticker, dan
tugas kamu adalah mengusulkan HIPOTESIS strategi trading yang konkret.

Balas HANYA dengan JSON, struktur PERSIS seperti ini:
{
  "hypothesis": "deskripsi hipotesis strategi yang bisa diuji",
  "proposed_action": "BUY" atau "SELL" atau "HOLD",
  "rationale": "alasan singkat berbasis data riset yang diberikan"
}

Kalau data riset tidak cukup kuat/meyakinkan, proposed_action harus "HOLD"."""


class StrategyAnalystAgent(BaseAgent):
    name = "strategy_analyst_agent"
    system_prompt = SYSTEM_PROMPT

    def run(self, research: dict) -> dict:
        user_message = (
            f"Ticker: {research['ticker']}\n"
            f"Sentiment score: {research['sentiment_score']}\n"
            f"Ringkasan riset: {research['summary']}\n"
            f"Temuan kunci: {research['key_findings']}"
        )

        result = self._call_llm(user_message)

        required_fields = ["hypothesis", "proposed_action", "rationale"]
        for field in required_fields:
            if field not in result:
                raise ValueError(
                    f"[{self.name}] Field '{field}' hilang dari output LLM: {result}"
                )

        # --- Backtest belum diimplementasikan -> paksa HOLD ---
        backtest_passed = False  # placeholder jujur, akan diganti langkah berikutnya

        if not backtest_passed:
            result["proposed_action"] = "HOLD"
            result["rationale"] = (
                f"[BACKTEST BELUM DIVALIDASI] Usulan asli LLM: {result['proposed_action']}. "
                f"Alasan LLM: {result['rationale']}"
            )

        result["ticker"] = research["ticker"]
        result["backtest_passed"] = backtest_passed
        return result