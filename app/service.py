from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from app.chunking import chunk_text
from app.config import settings
from app.embeddings import Embedder
from app.extractors.file_extractor import extract_text_from_file
from app.extractors.web_extractor import extract_text_from_url
from app.tenants import TenantStore
from app.vector_store import VectorStore


class KnowledgeService:
    def __init__(self) -> None:
        self.tenants = TenantStore()
        self.embedder = Embedder()
        self.store = VectorStore()
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def ensure_tenant(self, tenant_id: str) -> None:
        if not self.tenants.tenant_exists(tenant_id):
            raise ValueError(f"tenant '{tenant_id}' not found")

    def ingest_text(self, tenant_id: str, source: str, text: str, metadata: dict | None = None) -> dict:
        self.ensure_tenant(tenant_id)
        pieces = chunk_text(text=text, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
        if not pieces:
            return {"tenant_id": tenant_id, "source": source, "chunks": 0}
        vectors = self.embedder.embed(pieces)
        count = self.store.upsert_chunks(tenant_id, vectors, pieces, source, metadata or {})
        return {"tenant_id": tenant_id, "source": source, "chunks": count}

    def ingest_url(self, tenant_id: str, url: str) -> dict:
        text = extract_text_from_url(url, max_chars=settings.max_url_chars)
        parsed = urlparse(url)
        return self.ingest_text(tenant_id, source=url, text=text, metadata={"host": parsed.netloc, "kind": "url"})

    def ingest_file(self, tenant_id: str, file_path: Path) -> dict:
        text = extract_text_from_file(file_path)
        return self.ingest_text(tenant_id, source=file_path.name, text=text, metadata={"kind": "file"})

    def query(self, tenant_id: str, query: str, top_k: int) -> dict:
        self.ensure_tenant(tenant_id)
        vector = self.embedder.embed([query])[0]
        points = self.store.search(tenant_id, vector, top_k)
        results = []
        snippets = []
        for p in points:
            payload = p.payload or {}
            text = str(payload.get("text", ""))
            if text:
                snippets.append(text)
            results.append(
                {
                    "source": str(payload.get("source", "unknown")),
                    "score": float(p.score or 0.0),
                    "text": text,
                    "metadata": payload,
                }
            )
        answer = "\n\n".join(snippets[:3])
        return {"tenant_id": tenant_id, "query": query, "answer": answer, "results": results}
