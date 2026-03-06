from __future__ import annotations


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    clean = " ".join(text.split())
    if not clean:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + chunk_size)
        piece = clean[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(clean):
            break
        start = max(0, end - chunk_overlap)
    return chunks
