from __future__ import annotations

from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def _fetch_html(url: str) -> str:
    response = requests.get(url, timeout=20, headers={"User-Agent": "KnowledgeServiceBot/1.0"})
    response.raise_for_status()
    return response.text


def _extract_text_from_html(html: str, max_chars: int) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
    return text[:max_chars]


def _normalize_link(base_url: str, href: str) -> str | None:
    if not href:
        return None
    candidate = urljoin(base_url, href.strip())
    candidate, _ = urldefrag(candidate)
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"}:
        return None
    return candidate


def extract_text_from_url(url: str, max_chars: int) -> str:
    return _extract_text_from_html(_fetch_html(url), max_chars=max_chars)


def crawl_site(
    start_url: str,
    *,
    max_chars: int,
    max_depth: int,
    max_pages: int,
    same_domain_only: bool = True,
) -> list[dict]:
    start = start_url.strip()
    if not start:
        return []
    start_host = urlparse(start).netloc.lower()
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    visited: set[str] = set()
    pages: list[dict] = []

    while queue and len(pages) < max_pages:
        current_url, depth = queue.popleft()
        if current_url in visited:
            continue
        visited.add(current_url)

        try:
            html = _fetch_html(current_url)
        except Exception:
            continue

        text = _extract_text_from_html(html, max_chars=max_chars)
        pages.append({"url": current_url, "text": text})

        if depth >= max_depth:
            continue

        soup = BeautifulSoup(html, "html.parser")
        for anchor in soup.find_all("a"):
            href = anchor.get("href")
            normalized = _normalize_link(current_url, href)
            if not normalized or normalized in visited:
                continue
            if same_domain_only and urlparse(normalized).netloc.lower() != start_host:
                continue
            queue.append((normalized, depth + 1))

    return pages
