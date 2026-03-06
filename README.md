# Knowledge Service

Multi-tenant ingestion and retrieval service for chatbot/MCP knowledge grounding.

## Features

- Multi-tenant isolation by `tenant_id`
- Ingest file inputs (`pdf`, `docx`, `txt`, `md`)
- Ingest URL content (HTML extraction)
- Chunk + embed + store in Qdrant
- Query endpoint for semantic retrieval

## Run (Docker Compose)

```bash
docker compose up -d --build
```

Service: `http://127.0.0.1:8090`
Qdrant: `http://127.0.0.1:6333`

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
