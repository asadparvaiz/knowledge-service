#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose exec -T knowledge-service python - <<'PY'
import urllib.request

for url in [
    "http://host.docker.internal:11434/api/tags",
    "http://host.docker.internal:11434/v1/models",
]:
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            print(url, "OK", r.status)
            print(r.read(200).decode("utf-8", "ignore"))
    except Exception as e:
        print(url, "FAIL", e)
PY
