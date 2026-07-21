"""
Desk Manager Agent: gerbang validasi akhir + position sizing.

Hard rule di kode (bukan cuma di prompt):
- Kalau proposed_action == HOLD, langsung REJECTED tanpa manggil LLM
  (gak ada yang perlu divalidasi, hemat compute).
- position_size_pct di-cap maksimal 5% apapun kata LLM.
"""

from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """Kamu adalah Desk Manager Agent - pengawas risiko di sistem trading.
Kamu menerima usulan strategi dan tugas kamu MENANTANG usulan itu,
bukan menyetujuinya secara default.

Balas HANYA dengan JSON, struktur PERSIS seperti ini:
{
  "status": "APPROVED" atau "REJECTED" atau "NEEDS_REVIEW",
  "position_size_pct": <float 0.0 sampai 5.0>,
  "reasoning": "alasan keputusan, termasuk risiko yang dipertimbangkan"
}

position_size_pct TIDAK BOLEH lebih dari 5.0 apapun alasannya."""

MAX_POSITION_SIZE_PCT = 5.0


class DeskManagerAgent(BaseAgent):
    name = "desk_manager_agent"
    system_prompt = SYSTEM_PROMPT

    def run(self, strategy: dict) -> dict:
        # Hard gate: HOLD gak usah divalidasi, langsung tolak.
        if strategy["proposed_action"] == "HOLD":
            return {
                "ticker": strategy["ticker"],
                "action": "HOLD",
                "status": "REJECTED",
                "position_size_pct": 0.0,
                "reasoning": "Action HOLD dari Strategy Agent - tidak ada aksi yang perlu divalidasi.",
            }

        user_message = (
            f"Ticker: {strategy['ticker']}\n"
            f"Proposed action: {strategy['proposed_action']}\n"
            f"Backtest passed: {strategy['backtest_passed']}\n"
            f"Rationale: {strategy['rationale']}"
        )

        result = self._call_llm(user_message)

        required_fields = ["status", "position_size_pct", "reasoning"]
        for field in required_fields:
            if field not in result:
                raise ValueError(
                    f"[{self.name}] Field '{field}' hilang dari output LLM: {result}"
                )

        # --- Hard enforcement, tidak peduli apa kata LLM ---
        result["position_size_pct"] = min(
            float(result["position_size_pct"]), MAX_POSITION_SIZE_PCT
        )
        if not strategy["backtest_passed"]:
            result["status"] = "REJECTED"
            result["position_size_pct"] = 0.0
        # ----------------------------------------------------

        result["ticker"] = strategy["ticker"]
        result["action"] = strategy["proposed_action"]
        return result