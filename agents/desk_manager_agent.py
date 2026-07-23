"""
Desk Manager Agent: gerbang validasi akhir + position sizing.

Position size MAKSIMAL dihitung dari fixed fractional risk (matematika,
berdasarkan stop-loss ATR-based aset tersebut) - bukan ditebak LLM.
LLM cuma bisa MENGECILKAN size lebih lanjut (misal kalau reasoning-nya
menemukan red flag tambahan), TIDAK PERNAH bisa membesarkan di atas
hasil kalkulasi. Ini mencegah LLM confidence (yang bukan probabilitas
statistik asli) dipakai buat menaikkan risiko.
"""

from agents.base_agent import BaseAgent
from core.position_sizing import calculate_position_size

SYSTEM_PROMPT = """Kamu adalah Desk Manager Agent - bertugas fine-tuning position size,
BUKAN memutuskan approve/reject (itu sudah ditentukan sebelum kamu dipanggil).

Kamu menerima sinyal yang SUDAH terkonfirmasi oleh 2 validator independen
(LLM sentiment analysis dan technical confluence), beserta batas maksimal
position size yang sudah dihitung secara matematis (fixed fractional risk
berdasarkan stop-loss ATR aset tersebut - volatilitas sudah diperhitungkan
di sini).

Balas HANYA dengan JSON, struktur PERSIS seperti ini:
{
  "size_adjustment_factor": <float 0.0 sampai 1.0>,
  "reasoning": "alasan penyesuaian size, jika ada"
}

Default 1.0 (pakai batas maksimal penuh) KECUALI kamu menemukan red flag
SPESIFIK pada data yang diberikan (bukan kekhawatiran umum soal volatilitas
kripto - itu sudah diperhitungkan). Jangan terlalu konservatif tanpa alasan
konkret - sinyal ini sudah melewati validasi ketat sebelum sampai ke kamu."""


class DeskManagerAgent(BaseAgent):
    name = "desk_manager_agent"
    system_prompt = SYSTEM_PROMPT

    def run(self, strategy: dict, capital: float) -> dict:
    # Hitung batas maksimal SEBELUM tanya LLM apapun.
        max_size_info = calculate_position_size(
            capital=capital,
            stop_loss_pct=strategy["stop_loss_pct"],
            risk_per_trade_pct=0.01,
            max_position_pct=0.25,
        )

        if strategy["proposed_action"] == "HOLD":
            return {
                "ticker": strategy["ticker"],
                "action": "HOLD",
                "status": "REJECTED",
                "position_size": 0.0,
                "position_pct_of_capital": 0.0,
                "reasoning": "Action HOLD dari Strategy Agent - tidak ada aksi yang perlu divalidasi.",
            }

    # --- Keputusan APPROVE/REJECT ditentukan oleh KODE, bukan LLM ---
    # backtest_passed = True berarti LLM sentiment DAN technical confluence
    # sudah sepakat (2 validator independen). Itu sudah proses validasi yang
    # cukup ketat - LLM Desk Manager tidak diberi hak veto biner di sini,
    # karena terbukti bisa terlalu konservatif secara inkonsisten (menolak
    # meski 2 validator sepakat, dengan alasan generik "kripto kan volatile").
        if not strategy["backtest_passed"]:
            return {
                "ticker": strategy["ticker"],
                "action": strategy["proposed_action"],
                "status": "REJECTED",
                "position_size": 0.0,
                "position_pct_of_capital": 0.0,
                "reasoning": f"Sinyal tidak terkonfirmasi 2 validator independen. {strategy['rationale']}",
            }

    # Sampai sini, backtest_passed=True -> otomatis APPROVED.
    # LLM cuma dipakai untuk fine-tuning position size (nuansa halus),
    # BUKAN untuk keputusan APPROVE/REJECT.
        user_message = (
            f"Ticker: {strategy['ticker']}\n"
            f"Action (sudah terkonfirmasi 2 validator independen): {strategy['proposed_action']}\n"
            f"Regime: {strategy['technical_regime']}\n"
            f"Rationale: {strategy['rationale']}\n"
            f"Batas maksimal position size (hasil kalkulasi risk management): "
            f"{max_size_info['position_pct_of_capital']}% dari modal "
            f"(${max_size_info['position_size']}), risiko ${max_size_info['risk_amount']} kalau stop-loss kena.\n\n"
            "Sinyal ini SUDAH APPROVED (2 validator independen sepakat). "
            "Tugasmu HANYA menentukan apakah perlu mengecilkan position size lebih "
            "lanjut dari batas maksimal, berdasarkan konteks risiko spesifik yang "
            "kamu lihat (bukan kekhawatiran umum soal volatilitas kripto - itu "
            "sudah diperhitungkan di kalkulasi stop-loss)."
        )

        result = self._call_llm(user_message)

        if "size_adjustment_factor" not in result or "reasoning" not in result:
            raise ValueError(
                f"[{self.name}] Field wajib hilang dari output LLM: {result}"
            )

        adjustment = min(float(result["size_adjustment_factor"]), 1.0)
        adjustment = max(adjustment, 0.0)

        final_position_size = max_size_info["position_size"] * adjustment
        final_pct = max_size_info["position_pct_of_capital"] * adjustment

        return {
            "ticker": strategy["ticker"],
            "action": strategy["proposed_action"],
            "status": "APPROVED",
            "position_size": round(final_position_size, 2),
            "position_pct_of_capital": round(final_pct, 2),
            "max_calculated_size": max_size_info["position_size"],
            "size_adjustment_factor": adjustment,
            "reasoning": result["reasoning"],
        }