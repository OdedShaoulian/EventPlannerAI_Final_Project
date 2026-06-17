from __future__ import annotations

import base64
from typing import Optional

from openai import OpenAI

from src.config import CHAT_MODEL, SYSTEM_PROMPT, VISION_MODEL


def create_openai_client(api_key: str | None = None) -> OpenAI:
    """Create an OpenAI client using a provided key or the local environment."""
    if api_key:
        return OpenAI(api_key=api_key)
    return OpenAI()


def extract_output_text(response) -> str:
    """Extract text from OpenAI Responses API results with a safe fallback."""
    text = getattr(response, "output_text", None)
    if text:
        return text.strip()

    try:
        parts: list[str] = []
        for item in response.output:
            for content in getattr(item, "content", []) or []:
                value = getattr(content, "text", None)
                if value:
                    parts.append(value)
        joined = "\n".join(parts).strip()
        if joined:
            return joined
    except Exception:
        pass

    return str(response)


def build_user_prompt(user_message: str, rag_context: str = "", image_analysis: str = "") -> str:
    """Build a single grounded prompt that combines user text, RAG, and image context."""
    sections = [f"User request:\n{user_message.strip()}"]

    if rag_context.strip():
        sections.append(
            "Private knowledge base context retrieved with RAG. "
            "Use this information when relevant and do not invent details that contradict it:\n"
            f"{rag_context.strip()}"
        )

    if image_analysis.strip():
        sections.append(
            "Image analysis from the uploaded event/venue image. "
            "Use it when answering logistics or package recommendations:\n"
            f"{image_analysis.strip()}"
        )

    return "\n\n---\n\n".join(sections)


def chat_with_ai(openai_client: OpenAI, user_message: str, rag_context: str = "", image_analysis: str = "") -> str:
    """Conversational AI through OpenAI Responses API."""
    final_prompt = build_user_prompt(user_message, rag_context, image_analysis)
    response = openai_client.responses.create(
        model=CHAT_MODEL,
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": final_prompt},
                ],
            }
        ],
    )
    return extract_output_text(response)


def analyze_image(openai_client: OpenAI, image_bytes: bytes, mime_type: str, prompt: Optional[str] = None) -> str:
    """Multimodal image analysis through OpenAI Vision input in Responses API."""
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:{mime_type};base64,{b64_image}"
    user_prompt = prompt or (
        "נתח את התמונה בהקשר של תכנון אירוע עם בובות מתנפחות. "
        "ציין מה רואים, האם המקום נראה מתאים, אילו מגבלות לוגיסטיות קיימות, "
        "ואיזו המלצה עסקית היית נותן ללקוח."
    )

    response = openai_client.responses.create(
        model=VISION_MODEL,
        instructions=(
            "You are a Hebrew event-planning assistant. Analyze images carefully, "
            "focus on visible venue logistics, and avoid claiming certainty about hidden details."
        ),
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": user_prompt},
                    {"type": "input_image", "image_url": image_url, "detail": "auto"},
                ],
            }
        ],
    )
    return extract_output_text(response)
