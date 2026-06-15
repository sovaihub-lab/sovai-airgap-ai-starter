#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== SovAI Air-Gap AI Starter: connected preparation phase =="
echo "This phase requires internet access."

mkdir -p artifact-hub/images artifact-hub/wheelhouse artifact-hub/sbom artifact-hub/signatures data/audit

echo "== Checking Docker =="
docker version >/dev/null
docker compose version >/dev/null

echo "== Building application image =="
docker compose build sovai-app

echo "== Saving application image to artifact hub =="
docker save sovai-airgap/app:0.1 -o artifact-hub/images/sovai-airgap-app.tar

echo "== Downloading Python wheels into local wheelhouse =="
python3 -m pip download --dest artifact-hub/wheelhouse -r services/app/requirements.txt

echo "== Creating checksums =="
if command -v sha256sum >/dev/null 2>&1; then
  find artifact-hub -type f -print0 | sort -z | xargs -0 sha256sum > artifact-hub/checksums.sha256
else
  find artifact-hub -type f -print0 | sort -z | xargs -0 shasum -a 256 > artifact-hub/checksums.sha256
fi

echo "== Creating portable artifact bundle =="
tar -czf sovai-airgap-artifact-bundle.tar.gz artifact-hub data/documents docker-compose.yml services/app scripts tests README.md

echo ""
echo "Preparation complete."
echo "Created:"
echo "  artifact-hub/images/sovai-airgap-app.tar"
echo "  artifact-hub/wheelhouse/"
echo "  artifact-hub/checksums.sha256"
echo "  sovai-airgap-artifact-bundle.tar.gz"
echo ""
echo "Next:"
echo "  1. Disconnect internet"
echo "  2. Run ./scripts/bootstrap-offline.sh"
