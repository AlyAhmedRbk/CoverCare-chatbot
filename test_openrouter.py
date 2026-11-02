import asyncio

from app.core.config import settings
from app.services.llm_service import create_llm_client


async def main():
    print("Testing CoverCare AI - OpenRouter")
    print("----------------------------------")

    print("API key configured:", bool(settings.OPENAI_API_KEY))
    print("Model:", settings.OPENAI_MODEL)
    print("Base URL:", settings.OPENAI_BASE_URL)

    client = create_llm_client()

    try:
        print("\nSending request...\n")

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a health insurance assistant. "
                        "Only discuss health insurance."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Explain what health insurance coverage means."
                    ),
                },
            ],
            stream=True,
            temperature=0.3,
        )

        print("LLM RESPONSE:")

        async for chunk in response:
            if chunk.choices:
                content = chunk.choices[0].delta.content

                if content:
                    print(content, end="", flush=True)

        print("\n\nSUCCESS: OpenRouter streaming works!")

    except Exception as error:
        print("\nFAILED:", type(error).__name__)
        print("DETAILS:", str(error))

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
