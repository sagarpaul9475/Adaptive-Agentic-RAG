from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend for the Adaptive Agentic RAG project.",
)

app.include_router(documents_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
