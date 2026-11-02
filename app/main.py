from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.chat import router as chat_router
from app.core.config import settings
from app.schemas.chat import HealthResponse


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "A restricted Generative AI health insurance "
        "assistant with real-time response streaming."
    ),
    version="1.0.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(
    chat_router,
    prefix="/api/v1",
    tags=["Chat"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="running",
        application=settings.APP_NAME,
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        application=settings.APP_NAME,
    )
