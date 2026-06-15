#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== SovAI Air-Gap AI Starter: offline bootstrap phase =="
echo "This phase should be run after disconnecting internet."

./scripts/verify-no-internet.sh

echo "== Verifying local artifact image exists =="
test -f artifact-hub/images/sovai-airgap-app.tar

echo "== Loading Docker image from local artifact hub =="
docker load -i artifact-hub/images/sovai-airgap-app.tar

echo "== Starting platform with local image only =="
docker compose up -d --no-build

echo "== Running smoke test =="
./scripts/run-smoke-test.sh

echo ""
echo "Offline bootstrap complete."
echo "Open: http://localhost:8080"
