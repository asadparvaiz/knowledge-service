from __future__ import annotations

from openai import OpenAI

from app.config import settings


class AnswerGenerator:
    def __init__(self) -> None:
        self.provider = settings.generation_provider.lower()
        self.model = settings.generation_model
        self.system_prompt = settings.generation_system_prompt
        self.temperature = settings.generation_temperature
        self.max_tokens = settings.generation_max_tokens

        api_key = settings.generation_api_key or settings.openai_api_key
        base_url = settings.generation_base_url or settings.openai_base_url
        self.client = None
        if self.provider == "openai" and api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, query: str, contexts: list[dict]) -> str:
        if not contexts:
            return "I could not find relevant context for this tenant yet."

        context_block = []
        for idx, item in enumerate(contexts, start=1):
            source = item.get("source", "unknown")
            text = item.get("text", "")
            context_block.append(f"[{idx}] Source: {source}\n{text}")

        prompt = (
            "Use only the context below to answer the user question. "
            "When possible, cite source numbers like [1], [2].\n\n"
            f"Question:\n{query}\n\n"
            f"Context:\n{'\n\n'.join(context_block)}"
        )

        if self.client is None:
            # Fallback answer: return stitched top snippets if model is unavailable.
            return "\n\n".join(item.get("text", "") for item in contexts[:3]).strip()

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return (response.choices[0].message.content or "").strip()
