import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.schemas.chat import ChatRequest
from app.services.guardrail_service import (
    get_out_of_scope_response,
    is_in_scope,
)
from app.services.llm_service import stream_llm_response


router = APIRouter()
logger = logging.getLogger(__name__)


def sse_event(event_type: str, content: str) -> str:
    payload = json.dumps(
        {
            "type": event_type,
            "content": content,
        }
    )

    return f"data: {payload}\n\n"


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):

    message = request.message.strip()

    if not message:
        return StreamingResponse(
            iter([sse_event("error", "Message cannot be empty.")]),
            media_type="text/event-stream",
        )

    if len(message) > settings.MAX_MESSAGE_LENGTH:
        return StreamingResponse(
            iter([sse_event("error", "Message is too long.")]),
            media_type="text/event-stream",
        )

    if not is_in_scope(message):

        async def restricted_response():
            yield sse_event(
                "token",
                get_out_of_scope_response(),
            )
            yield sse_event("done", "")

        return StreamingResponse(
            restricted_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    history = request.history[-settings.MAX_HISTORY_MESSAGES :]

    async def generate_response():
        try:
            async for token in stream_llm_response(
                message=message,
                history=history,
            ):
                yield sse_event("token", token)

            yield sse_event("done", "")

        except Exception:
            logger.exception("LLM streaming failed")

            yield sse_event(
                "error",
                "I'm sorry, but I couldn't generate a response. "
                "Please try again later.",
            )

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
