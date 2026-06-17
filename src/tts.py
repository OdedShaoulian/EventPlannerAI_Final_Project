from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openai import OpenAI

from src.config import AUDIO_DIR, TTS_MODEL, TTS_VOICE


def create_speech(openai_client: OpenAI, text: str) -> Path:
    """OpenAI Text-to-Speech capability. Returns a local MP3 path."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    safe_text = text.strip()[:3500]
    if not safe_text:
        raise ValueError("Cannot create speech from empty text.")

    output_path = AUDIO_DIR / f"answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

    with openai_client.audio.speech.with_streaming_response.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=safe_text,
    ) as response:
        response.stream_to_file(output_path)

    return output_path
