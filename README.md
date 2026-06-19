# SovAI Air-Gap AI Starter

SovAIHub ([SovAIHub.com](https://SovAIHub.com))

Open-source laptop MVP for demonstrating an air-gap-ready Sovereign AI pattern.

## Phase 1: Offline Runtime Demo

### Short Description

The Offline Runtime Demo is the foundation layer of the SovAI Air-Gap AI Platform. It demonstrates how an AI application can be prepared while internet access is available, packaged into approved local artifacts, and then executed without runtime internet connectivity.

This phase does not focus on advanced AI generation. Instead, it proves the most important air-gap principle: once the runtime starts, it should depend only on local artifacts, local documents, approved tools, and internal logs.

The demo includes local document retrieval, a lightweight ML classifier, controlled agent tools, and audit logging. It is designed as a laptop-friendly reference implementation for sovereign AI and disconnected enterprise environments.

## What This Phase Proves

- The application can run without internet after preparation.
- Required dependencies are packaged before going offline.
- Docker images are built and saved as local artifacts.
- Runtime services use local documents only.
- Agent tools are restricted to an approved list.
- Unapproved tools such as web search are blocked.
- All important actions are written to an audit log.

## Repository

```bash
git clone <your-github-repo-url>
cd sovai-airgap-ai-starter
```

## Prerequisites

- Docker Desktop installed
- Git Bash, WSL, or Linux/macOS terminal
- Internet access during preparation only

On Windows, run the scripts from WSL or Git Bash.

## Setup: Connected Preparation Phase

Run this while internet is available:

```bash
chmod +x scripts/*.sh
./scripts/prepare-online.sh
```

This script performs the connected preparation step:

1. Builds the Docker application image
2. Installs required Python packages into the image
3. Saves the image as a local artifact
4. Downloads Python wheels into the local wheelhouse
5. Creates checksums
6. Creates an artifact bundle

Generated artifacts include:

```text
artifact-hub/images/sovai-airgap-app.tar
artifact-hub/wheelhouse/
artifact-hub/checksums.sha256
sovai-airgap-artifact-bundle.tar.gz
```

## Setup: Offline Runtime Phase

Disconnect internet first:

```text
Turn off Wi-Fi, unplug network, or disable VPN.
```

Then run:

```bash
./scripts/bootstrap-offline.sh
```

This script:

1. Verifies host internet is disconnected
2. Loads the saved Docker image from artifact-hub/images
3. Starts the application using Docker Compose
4. Runs smoke tests

Open the application:

```text
http://127.0.0.1:8080
```

## Configuration

Main configuration file:

```text
docker-compose.yml
```

Important environment variables:

```text
SOVAI_OFFLINE_MODE: "true"
APPROVED_TOOLS: "calculator,document_search,ticket_classifier"
DOCUMENTS_DIR: "/app/data/documents"
AUDIT_LOG_PATH: "/app/data/audit/audit-log.jsonl"
```

Documents are stored in:

```text
data/documents/
```

Audit logs are written to:

```text
data/audit/audit-log.jsonl
```

Approved tools are listed in:

```text
artifact-hub/tools/approved-tools.yaml
```

## Test Commands

Check health:

```bash
curl http://127.0.0.1:8080/health
```

Check status:

```bash
curl http://127.0.0.1:8080/status
```

Ask a private document question:

```bash
curl -s http://127.0.0.1:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Who can access confidential finance reports?","top_k":3}'
```

Run local ML classifier:

```bash
curl -s http://127.0.0.1:8080/ml/classify \
  -H "Content-Type: application/json" \
  -d '{"text":"User cannot access VPN and needs MFA reset"}'
```

Run approved agent tool:

```bash
curl -s http://127.0.0.1:8080/agent/run \
  -H "Content-Type: application/json" \
  -d '{"tool":"calculator","input":"(12 * 7) + 5"}'
```

Test blocked tool:

```bash
curl -s http://127.0.0.1:8080/agent/run \
  -H "Content-Type: application/json" \
  -d '{"tool":"web_search","input":"latest AI news"}'
```

Expected result:

```json
{
  "allowed": false
}
```

## Troubleshooting

### Problem: scikit-learn build failed on Windows

Earlier versions used `scikit-learn`, `numpy`, and `scipy`. On Windows, pip sometimes downloaded the source package and tried to compile it, causing errors such as:

```text
ERROR: Unknown compiler(s)
metadata-generation-failed
```

Fix:

The current version removes compiled ML dependencies and uses pure-Python retrieval and classification.

Use the patched version that only requires:

```text
fastapi
uvicorn
pydantic
jinja2
```

### Problem: Container runs but browser cannot access the app

Check:

```bash
docker compose ps
docker port sovai-airgap-app
```

Expected:

```text
8080/tcp -> 0.0.0.0:8080
```

If no port is shown, recreate the container:

```bash
docker compose down --remove-orphans
docker rm -f sovai-airgap-app 2>/dev/null || true
docker compose up -d --no-build --force-recreate
```

### Problem: localhost does not work

Use:

```text
http://127.0.0.1:8080
```

instead of:

```text
http://localhost:8080
```

### Problem: Docker network blocks browser access

For the laptop demo, use:

```yaml
networks:
  sovai_internal:
    driver: bridge
```

Avoid this for the first demo:

```yaml
internal: true
```

because it can make local browser testing harder.

### Problem: Port 8080 already used

Change the port mapping:

```yaml
ports:
  - "8090:8080"
```

Then recreate:

```bash
docker compose down
docker compose up -d --no-build --force-recreate
```

Open:

```text
http://127.0.0.1:8090
```

## Positioning

This phase is not a full enterprise TL4 platform. It is a laptop reference implementation that demonstrates the offline runtime pattern:

- Prepare while connected.
- Run while disconnected.
- Consume only local artifacts.
- Log every important action.

The current version intentionally avoids compiled Python ML dependencies such as scikit-learn, numpy, and scipy so the offline preparation step is simpler on Windows. Later, this can be expanded to local LLM runtime, model registry, vector DB, internal PyPI, internal container registry, Kubernetes, or disconnected OpenShift.

## Contributor

- Rana Kumar - [LinkedIn](https://www.linkedin.com/in/rana-kumar-333b56127/) - SovAIHub ([SovAIHub.com](https://SovAIHub.com))
