#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${KNOWLEDGE_BASE_URL:-http://127.0.0.1:8090}"
TENANT_ID="${TENANT_ID:-tenant-demo}"
TENANT_NAME="${TENANT_NAME:-Demo Tenant}"
TARGET_URL="${TARGET_URL:-https://example.com}"
QUESTION="${QUESTION:-What is this site about?}"
API_KEY="${KNOWLEDGE_API_KEY:-}"
CRAWL="${CRAWL:-false}"
MAX_DEPTH="${MAX_DEPTH:-1}"
MAX_PAGES="${MAX_PAGES:-20}"

AUTH_HEADER=()
if [[ -n "${API_KEY}" ]]; then
  AUTH_HEADER=(-H "x-api-key: ${API_KEY}")
fi

echo "[1/3] Create tenant: ${TENANT_ID}"
curl -sS -X POST "${BASE_URL}/tenants" \
  -H 'Content-Type: application/json' \
  "${AUTH_HEADER[@]}" \
  -d "{\"tenant_id\":\"${TENANT_ID}\",\"name\":\"${TENANT_NAME}\"}" || true

echo
echo "[2/3] Ingest URL: ${TARGET_URL}"
curl -sS -X POST "${BASE_URL}/ingest/url" \
  -H 'Content-Type: application/json' \
  "${AUTH_HEADER[@]}" \
  -d "{\"tenant_id\":\"${TENANT_ID}\",\"url\":\"${TARGET_URL}\",\"crawl\":${CRAWL},\"max_depth\":${MAX_DEPTH},\"max_pages\":${MAX_PAGES},\"same_domain_only\":true}"

echo
echo "[3/3] Query tenant index"
curl -sS -X POST "${BASE_URL}/query" \
  -H 'Content-Type: application/json' \
  "${AUTH_HEADER[@]}" \
  -d "{\"tenant_id\":\"${TENANT_ID}\",\"query\":\"${QUESTION}\",\"top_k\":5}"
echo
