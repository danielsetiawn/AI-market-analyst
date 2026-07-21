"""
Base class buat semua agent. Titik akses tunggal ke LLM,
biar gampang switch backend (Ollama <-> Claude API) tanpa ubah tiap agent.
"""

import json
import requests
from abc import ABC, abstractmethod

from config import settings


class BaseAgent(ABC):
    name: str = "base_agent"
    system_prompt: str = ""

    def _call_llm(self, user_message: str) -> dict:
        """
        Manggil LLM sesuai backend yang di-set di config.
        Return dict hasil parsing JSON (bukan string mentah).
        """
        full_prompt = f"{self.system_prompt}\n\n{user_message}"

        if settings.llm_backend == "ollama":
            return self._call_ollama(full_prompt)
        else:
            raise NotImplementedError(
                f"Backend '{settings.llm_backend}' belum diimplementasikan"
            )

    def _call_ollama(self, full_prompt: str) -> dict:
        response = requests.post(
            settings.ollama_url,
            json={
                "model": settings.ollama_model,
                "prompt": full_prompt,
                "format": "json",
                "stream": False,
            },
        )
        response.raise_for_status()
        raw_text = response.json()["response"]

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"[{self.name}] Gagal parse JSON dari LLM: {raw_text!r}"
            ) from e

    @abstractmethod
    def run(self, *args, **kwargs):
        """Setiap agent implement logika utamanya di sini."""
        raise NotImplementedError