# Knowledge Service

Multi-tenant ingestion and retrieval service for chatbot/MCP knowledge grounding.

## Features

- Multi-tenant isolation by `tenant_id`
- Ingest file inputs (`pdf`, `docx`, `txt`, `md`)
- Ingest URL content (HTML extraction)
- Optional recursive crawl for linked pages
- Chunk + embed + store in Qdrant
- Query endpoint for semantic retrieval + generated answers

## Run (Docker Compose)

```bash
docker compose up -d --build
```

Service: `http://127.0.0.1:8090`
Qdrant: `http://127.0.0.1:6333`
Admin UI: `http://127.0.0.1:8090/ui`

## Qwen setup (no OpenAI)

Set `.env` to a Qwen-compatible API endpoint for embeddings and generation.

Example with OpenRouter:

```env
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=your_openrouter_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1

GENERATION_PROVIDER=openai
GENERATION_MODEL=qwen/qwen-2.5-14b-instruct
GENERATION_API_KEY=your_openrouter_key
GENERATION_BASE_URL=https://openrouter.ai/api/v1
GENERATION_TEMPERATURE=0.2
GENERATION_MAX_TOKENS=800
```

If you use another provider exposing OpenAI-compatible APIs, set `*_BASE_URL`, keys, and model names accordingly.

## Run (local)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090
```

## API

- `GET /health`
- `POST /tenants`
- `POST /ingest/url`
- `POST /ingest/file` (multipart)
- `POST /query`

## Admin UI

Open:

```bash
http://127.0.0.1:8090/ui
```

UI supports:

- create/list tenants
- ingest URL (single page or crawl)
- upload files
- run semantic queries

## MCP Integration

In `mcp-python` set:

```env
DEFAULT_CONNECTOR_ID=knowledge
KNOWLEDGE_SERVICE_URL=http://127.0.0.1:8090/query
KNOWLEDGE_SERVICE_API_KEY=
KNOWLEDGE_TOP_K=5
```

Then send completion with tenant context:

```json
{
  "prompt": "What is your return policy?",
  "context": {
    "tenant_id": "tenant-a"
  }
}
```

## Example

Create tenant:

```bash
curl -X POST http://127.0.0.1:8090/tenants \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"tenant-a","name":"Tenant A"}'
```

Ingest URL:

```bash
curl -X POST http://127.0.0.1:8090/ingest/url \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"tenant-a","url":"https://example.com"}'
```

Ingest URL with crawl:

```bash
curl -X POST http://127.0.0.1:8090/ingest/url \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"tenant-a","url":"https://example.com/docs","crawl":true,"max_depth":1,"max_pages":20,"same_domain_only":true}'
```

Query:

```bash
curl -X POST http://127.0.0.1:8090/query \
  -H 'Content-Type: application/json' \
  -d '{"tenant_id":"tenant-a","query":"What does this site describe?","top_k":5}'
```

## Demo script

End-to-end tenant URL ingest + query:

```bash
./scripts/tenant_url_query_demo.sh
```

With overrides:

```bash
TENANT_ID=tenant-a \
TARGET_URL=https://docs.example.com \
QUESTION=\"How do I reset password?\" \
./scripts/tenant_url_query_demo.sh
```
