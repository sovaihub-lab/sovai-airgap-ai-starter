#!/usr/bin/env bash
set -euo pipefail

echo "== Waiting for service =="
for i in $(seq 1 30); do
  if curl -s http://127.0.0.1:8090/health >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "== Status =="
curl -s http://127.0.0.1:8090/status || true
echo ""

echo "== RAG test =="
curl -s http://127.0.0.1:8090/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Who can access confidential finance reports?","top_k":3}'
echo ""

echo "== ML test =="
curl -s http://127.0.0.1:8090/ml/classify \
  -H "Content-Type: application/json" \
  -d '{"text":"User cannot access VPN and needs MFA reset"}'
echo ""

echo "== Agent allowed tool test =="
curl -s http://127.0.0.1:8090/agent/run \
  -H "Content-Type: application/json" \
  -d '{"tool":"calculator","input":"(12 * 7) + 5"}'
echo ""

echo "== Agent blocked tool test =="
curl -s http://127.0.0.1:8090/agent/run \
  -H "Content-Type: application/json" \
  -d '{"tool":"web_search","input":"latest AI news"}'
echo ""

echo "Smoke test complete."
