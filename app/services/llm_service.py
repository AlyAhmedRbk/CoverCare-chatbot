from collections.abc import AsyncGenerator
from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPT
from app.schemas.chat import ChatMessage


BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_FILE = BASE_DIR / "data" / "insurance_knowledge.md"


def load_knowledge_base() -> str:
    if not KNOWLEDGE_FILE.exists():
        return "No insurance documentation available."

    return KNOWLEDGE_FILE.read_text(encoding="utf-8")


def create_llm_client() -> AsyncOpenAI:
    api_key = settings.OPENAI_API_KEY.strip()

    if not api_key:
        raise RuntimeError("API key is missing from .env")

    base_url = settings.OPENAI_BASE_URL.strip()

    if not base_url:
        raise RuntimeError("LLM API base URL is missing from .env")

    return AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": "http://localhost:8000",
            "X-OpenRouter-Title": "CoverCare AI",
        },
        timeout=60.0,
        max_retries=1,
    )


async def stream_llm_response(
    message: str,
    history: list[ChatMessage],
) -> AsyncGenerator[str, None]:

    client = create_llm_client()

    try:
        knowledge = load_knowledge_base()

        system_message = (
            f"{SYSTEM_PROMPT}\n\n"
            f"COMPANY INSURANCE KNOWLEDGE:\n{knowledge}"
        )

        messages = [
            {
                "role": "system",
                "content": system_message,
            }
        ]

        for item in history:
            messages.append({
                "role": item.role,
                "content": item.content,
            })

        messages.append({
            "role": "user",
            "content": message,
        })

        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=0.3,
            stream=True,
        )

        async for chunk in stream:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                yield content

    finally:
        await client.close()
