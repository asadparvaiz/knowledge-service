from __future__ import annotations

import logging
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.models import IngestUrlRequest, QueryRequest, QueryResponse, TenantCreateRequest
from app.security import authorize_request
from app.service import KnowledgeService

logger = logging.getLogger("knowledge-service")
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), format="[%(levelname)s] %(message)s")

app = FastAPI(title="Knowledge Service", version="0.1.0")
svc = KnowledgeService()


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/tenants", dependencies=[Depends(authorize_request)])
async def create_tenant(payload: TenantCreateRequest):
    try:
        result = svc.tenants.create_tenant(payload.tenant_id, payload.name)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))
    return result


@app.post("/ingest/url", dependencies=[Depends(authorize_request)])
async def ingest_url(payload: IngestUrlRequest):
    try:
        logger.info("[ingest/url] tenant=%s url=%s", payload.tenant_id, payload.url)
        result = svc.ingest_url(payload.tenant_id, payload.url)
        return result
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/ingest/file", dependencies=[Depends(authorize_request)])
async def ingest_file(tenant_id: str = Form(...), file: UploadFile = File(...)):
    try:
        suffix = Path(file.filename or "upload.bin").suffix
        tmp_path = svc.upload_dir / f"{tenant_id}_{file.filename}"
        tmp_path.write_bytes(await file.read())
        logger.info("[ingest/file] tenant=%s file=%s", tenant_id, file.filename)
        result = svc.ingest_file(tenant_id, tmp_path)
        return result
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/query", response_model=QueryResponse, dependencies=[Depends(authorize_request)])
async def query(payload: QueryRequest):
    try:
        logger.info("[query] tenant=%s q=%s", payload.tenant_id, payload.query)
        return svc.query(payload.tenant_id, payload.query, payload.top_k)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.exception_handler(Exception)
async def unhandled_error(_, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


def run() -> None:
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    run()
