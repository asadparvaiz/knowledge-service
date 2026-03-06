from __future__ import annotations

import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import settings


class VectorStore:
    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)

    def _collection(self, tenant_id: str) -> str:
        return f"tenant_{tenant_id}"

    def ensure_collection(self, tenant_id: str, vector_size: int) -> str:
        name = self._collection(tenant_id)
        collections = {c.name for c in self.client.get_collections().collections}
        if name not in collections:
            self.client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )
        return name

    def upsert_chunks(self, tenant_id: str, vectors: list[list[float]], chunks: list[str], source: str, metadata: dict[str, Any]) -> int:
        if not vectors or len(vectors) != len(chunks):
            return 0
        collection = self.ensure_collection(tenant_id, len(vectors[0]))
        points: list[models.PointStruct] = []
        for idx, (vector, chunk) in enumerate(zip(vectors, chunks)):
            payload = {
                "tenant_id": tenant_id,
                "source": source,
                "chunk_index": idx,
                "text": chunk,
                **metadata,
            }
            points.append(models.PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload))
        self.client.upsert(collection_name=collection, points=points)
        return len(points)

    def search(self, tenant_id: str, vector: list[float], top_k: int):
        collection = self._collection(tenant_id)
        return self.client.query_points(collection_name=collection, query=vector, limit=top_k).points
