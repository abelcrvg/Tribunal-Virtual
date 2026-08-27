from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as process_router
from .database import Base, engine
from . import db_models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tribunal Virtual API",
    version="0.1.0",
    description="API do simulador educacional de processos judiciais brasileiros.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "tribunal-virtual-api"}


@app.get("/api/v1")
def api_info() -> dict[str, str]:
    return {"name": "Tribunal Virtual API", "version": "0.1.0"}
