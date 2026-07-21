"""
Konfigurasi global. Model & backend LLM diatur di sini,
biar gampang ganti dari Ollama ke Claude API nanti tanpa bongkar agent.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # "ollama" = lokal gratis, "anthropic" = Claude API (berbayar)
    llm_backend: str = "ollama"

    # Model buat masing-masing backend
    ollama_model: str = "qwen2.5:7b-instruct"
    ollama_url: str = "http://localhost:11434/api/generate"

    anthropic_model: str = "claude-sonnet-5"
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")

    audit_db_path: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "audit_log.db"
    )


settings = Settings()