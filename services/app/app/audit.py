import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict

AUDIT_LOG_PATH = Path(os.getenv("AUDIT_LOG_PATH", "/app/data/audit/audit-log.jsonl"))

def write_audit(event_type: str, payload: Dict[str, Any]) -> str:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    event_id = str(uuid.uuid4())
    event = {
        "event_id": event_id,
        "event_type": event_type,
        "timestamp_unix": time.time(),
        "offline_mode": os.getenv("SOVAI_OFFLINE_MODE", "false").lower() == "true",
        "payload": payload,
    }
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event_id
