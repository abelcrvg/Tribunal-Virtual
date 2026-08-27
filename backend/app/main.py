import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router as process_router
from .courtroom_api import router as courtroom_router
from .agents_api import router as agents_router
from .database import Base, engine
from . import db_models  # noqa: F401

Base.metadata.create_all(bind=engine)
app=FastAPI(title="Tribunal Virtual API",version="0.3.0",description="API do simulador educacional de processos judiciais brasileiros.")
_origins=os.getenv("CORS_ORIGINS","").strip()
allow_origins=[x.strip() for x in _origins.split(",") if x.strip()] or ["*"]
app.add_middleware(CORSMiddleware,allow_origins=allow_origins,allow_credentials=False,allow_methods=["*"],allow_headers=["*"])
app.include_router(process_router); app.include_router(courtroom_router); app.include_router(agents_router)
@app.get("/health")
def health(): return {"status":"ok","service":"tribunal-virtual-api"}
@app.get("/api/v1")
def api_info(): return {"name":"Tribunal Virtual API","version":"0.3.0"}
