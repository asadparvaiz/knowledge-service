from __future__ import annotations

import hashlib
from typing import Iterable

from openai import OpenAI

from app.config import settings


class Embedder:
    def __init__(self) -> None:
        self.provider = settings.embedding_provider.lower()
        self.model = settings.embedding_model
        self._client = None
        self.dim = 256
        if self.provider == "openai" and settings.openai_api_key:
            self._client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        items = list(texts)
        if not items:
            return []
        if self._client is not None:
            response = self._client.embeddings.create(model=self.model, input=items)
            vectors = [row.embedding for row in response.data]
            if vectors:
                self.dim = len(vectors[0])
            return vectors
        return [self._fallback_vector(text) for text in items]

    def _fallback_vector(self, text: str) -> list[float]:
        # Deterministic fallback to keep service runnable without embedding creds.
        data = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
        vector = []
        while len(vector) < self.dim:
            for b in data:
                vector.append((b / 127.5) - 1.0)
                if len(vector) >= self.dim:
                    break
        return vector
