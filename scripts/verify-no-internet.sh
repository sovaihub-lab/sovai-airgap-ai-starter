#!/usr/bin/env bash
set -euo pipefail

echo "== Verifying host internet is disconnected =="

if command -v curl >/dev/null 2>&1; then
  if curl -I --connect-timeout 3 --max-time 5 https://pypi.org >/dev/null 2>&1; then
    echo "ERROR: Internet appears reachable from host."
    echo "Disconnect Wi-Fi / unplug network / disable VPN, then retry."
    exit 1
  fi
else
  python3 - <<'PY'
import socket, sys
try:
    socket.create_connection(("pypi.org", 443), timeout=3).close()
    print("ERROR: Internet appears reachable from host.")
    sys.exit(1)
except Exception:
    pass
PY
fi

echo "Internet blocked from host: OK"
