from __future__ import annotations

import requests
from bs4 import BeautifulSoup


def extract_text_from_url(url: str, max_chars: int) -> str:
    response = requests.get(url, timeout=20, headers={"User-Agent": "KnowledgeServiceBot/1.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
    return text[:max_chars]
