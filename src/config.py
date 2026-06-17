from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
VISION_MODEL = os.getenv("VISION_MODEL", CHAT_MODEL)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICE = os.getenv("TTS_VOICE", "alloy")

KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
CHROMA_DIR = BASE_DIR / "chroma_db"
AUDIO_DIR = BASE_DIR / "audio_output"
UPLOADS_DIR = BASE_DIR / "uploads"
COLLECTION_NAME = "eventplanner_ai_knowledge"

SYSTEM_PROMPT = """
You are EventPlanner AI, a professional Hebrew AI assistant for an inflatable-event business.
Your role is to help customers and business operators choose event packages, understand logistics,
answer questions from the private knowledge base, analyze venue images, and give practical sales recommendations.

Rules:
1. Answer mainly in Hebrew unless the user asks for English.
2. Be helpful, clear, and business-oriented.
3. When RAG context is provided, ground your answer in that context and do not invent unsupported exact prices.
4. If image analysis is provided, explicitly use it in the answer.
5. If important information is missing, ask only the most essential follow-up questions and still give a useful next step.
6. Keep the tone professional, natural, and suitable for a course demo.
7. Never reveal API keys or private environment values.
""".strip()
