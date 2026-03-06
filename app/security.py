from __future__ import annotations

from fastapi import Header, HTTPException

from app.config import settings


async def authorize_request(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.service_api_key:
        return
    if x_api_key != settings.service_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
