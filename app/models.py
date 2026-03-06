from __future__ import annotations

from pydantic import BaseModel, Field


class TenantCreateRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=128)
    name: str = Field(default="", max_length=255)


class IngestUrlRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=128)
    url: str = Field(min_length=5, max_length=2048)
    crawl: bool = Field(default=False)
    max_depth: int = Field(default=1, ge=0, le=5)
    max_pages: int = Field(default=20, ge=1, le=500)
    same_domain_only: bool = Field(default=True)


class QueryRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=128)
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=25)


class SourceChunk(BaseModel):
    source: str
    score: float
    text: str
    metadata: dict


class QueryResponse(BaseModel):
    tenant_id: str
    query: str
    answer: str
    results: list[SourceChunk]
