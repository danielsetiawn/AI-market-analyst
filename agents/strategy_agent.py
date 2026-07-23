"""
Strategy Analyst Agent: usulkan hipotesis strategi dari hasil riset,
LALU KONFIRMASI dengan technical confluence (Engine B) sebelum dianggap
valid. Kedua "otak" - LLM sentiment reasoning dan rule-based technical
analysis - harus SEPAKAT arahnya sebelum proposed_action lolos.

Kalau LLM bilang BUY tapi confluence teknikal bilang SELL/HOLD (atau
sebaliknya), sinyal dipaksa HOLD - karena itu tanda 2 sumber informasi
independen tidak setuju, jadi belum cukup kuat untuk actionable.
"""

import yfinance as yf

from agents.base_agent import BaseAgent
from core.confluence import evaluate_confluence
from core.risk_sizing import calculate_dynamic_risk_params

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

    def _fetch_price_data(self, ticker: str):
        data = yf.download(ticker, period="2y", interval="1d", progress=False)
        data.columns = data.columns.get_level_values(0)
        return data

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

        llm_action = result["proposed_action"]

        # --- Konfirmasi dengan Engine B (technical confluence) ---
        price_data = self._fetch_price_data(research["ticker"])
        confluence_result = evaluate_confluence(price_data, min_agree=1.5, use_regime_weighting=True)
        technical_signal = confluence_result["final_signal"]

        # Backtest_passed sekarang berarti: LLM dan confluence teknikal SEPAKAT,
        # dan keduanya bukan HOLD. Ini validasi 2-sumber-independen, bukan lagi
        # placeholder buta.
        signals_agree = (llm_action == technical_signal) and (llm_action != "HOLD")
        backtest_passed = signals_agree

        final_action = llm_action if backtest_passed else "HOLD"

        risk_params = calculate_dynamic_risk_params(price_data)

        if not backtest_passed:
            result["rationale"] = (
                f"[TIDAK TERKONFIRMASI] LLM usulkan {llm_action}, "
                f"technical confluence bilang {technical_signal} (regime: {confluence_result['regime']}). "
                f"Alasan LLM: {result['rationale']}"
            )
        else:
            result["rationale"] = (
                f"[TERKONFIRMASI] LLM dan technical confluence sepakat {final_action} "
                f"(regime: {confluence_result['regime']}, confidence teknikal: {confluence_result['confidence']}%). "
                f"Alasan LLM: {result['rationale']}"
            )

        return {
            "ticker": research["ticker"],
            "proposed_action": final_action,
            "backtest_passed": backtest_passed,
            "rationale": result["rationale"],
            "technical_signal": technical_signal,
            "technical_regime": confluence_result["regime"],
            "stop_loss_pct": risk_params["stop_loss_pct"],
        }