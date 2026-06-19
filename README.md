

# SovAIHub
# Rana Kumar
# SovAI Air-Gap AI Starter

Open-source laptop MVP for demonstrating an air-gap-ready Sovereign AI pattern.

This demo proves:

- no runtime internet dependency
- local approved artifact hub
- private document RAG with citations
- tiny pure-Python ML classifier
- approved local agent tools only
- JSONL audit logging
- Docker Desktop based offline bootstrap

## Requirements

Use Docker Desktop with Docker Compose.

On Windows, run the scripts from WSL or Git Bash.

## Step 1: Prepare artifacts while internet is ON

```bash
chmod +x scripts/*.sh
./scripts/prepare-online.sh
```

## Step 2: Disconnect internet

Turn off Wi-Fi / unplug network / disable VPN.

## Step 3: Bootstrap offline

```bash
./scripts/bootstrap-offline.sh
```

## Step 4: Open the UI

```text
http://localhost:8080
```

## Useful API calls

Ask private RAG:

```bash
curl -s http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Who can access confidential finance reports?"}' | jq
```

Classify a business request:

```bash
curl -s http://localhost:8080/ml/classify \
  -H "Content-Type: application/json" \
  -d '{"text":"User cannot access the VPN and needs MFA reset"}' | jq
```

Run approved agent tool:

```bash
curl -s http://localhost:8080/agent/run \
  -H "Content-Type: application/json" \
  -d '{"tool":"calculator","input":"(12 * 7) + 5"}' | jq
```

Try a blocked tool:

```bash
curl -s http://localhost:8080/agent/run \
  -H "Content-Type: application/json" \
  -d '{"tool":"web_search","input":"latest AI news"}' | jq
```

## Important

This is not a production TL4 platform. It is a laptop reference implementation that demonstrates the core sovereign AI rule:

> Runtime workloads consume only approved internal artifacts.

This version intentionally avoids compiled Python ML dependencies such as scikit-learn, numpy, and scipy so the offline preparation step is simpler on Windows. Later, this can be expanded to local LLM runtime, model registry, vector DB, internal PyPI, internal container registry, Kubernetes, or disconnected OpenShift.
