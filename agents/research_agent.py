"""
Research Agent: analisis sentimen & temuan dari data mentah.
Sumber data (Firecrawl) belum diintegrasikan - untuk sekarang
raw_context dikasih manual biar kita bisa test alur intinya dulu.
"""

from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """Kamu adalah Research Agent di sistem trading multi-agent.
Tugas kamu: menganalisis data mentah tentang sebuah ticker, lalu
menghasilkan ringkasan riset yang OBJEKTIF dengan skor sentimen.

Balas HANYA dengan JSON, struktur PERSIS seperti ini:
{
  "summary": "ringkasan singkat temuan riset",
  "sentiment_score": <float antara -1.0 sampai 1.0>,
  "key_findings": ["temuan 1", "temuan 2"]
}

Jangan mengarang fakta yang tidak ada di data mentah yang diberikan."""


class ResearchAgent(BaseAgent):
    name = "research_agent"
    system_prompt = SYSTEM_PROMPT

    def run(self, ticker: str, raw_context: str) -> dict:
        user_message = f"Ticker: {ticker}\n\nData mentah:\n{raw_context}"

        result = self._call_llm(user_message)

        # Validasi dasar - pastikan field yang wajib ada, beneran ada
        required_fields = ["summary", "sentiment_score", "key_findings"]
        for field in required_fields:
            if field not in result:
                raise ValueError(
                    f"[{self.name}] Field '{field}' hilang dari output LLM: {result}"
                )

        result["ticker"] = ticker
        return result