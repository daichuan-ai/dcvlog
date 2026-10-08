#!/usr/bin/env python3
"""DCVlog anonymous usage telemetry (CloudBase).

Only sends a small allowlist of feature events to the publisher's CloudBase
endpoint. It never sends prompt text, photos, generated content, names, city,
studio name, customer information, or file contents.

Best-effort by design: disabled/offline/blocked/errors are silently ignored and
must never interrupt the learner's Skill task.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
import urllib.request
from pathlib import Path

ALLOWED_EVENTS = {
    "dcvlog_open",
    "write_vlog_start",
    "write_vlog_complete",
    "collage_start",
    "collage_complete",
    "update_requested",
}

SKILL_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = SKILL_ROOT / "telemetry-config.json"
STATE_DIR = Path.home() / ".dcvlog"
ANON_ID_PATH = STATE_DIR / "anonymous_id"
OPT_OUT_PATH = STATE_DIR / "no_telemetry"


def _load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _is_enabled(cfg: dict) -> bool:
    if os.environ.get("DCVLOG_TELEMETRY", "").strip().lower() in {"0", "false", "off", "no"}:
        return False
    if OPT_OUT_PATH.exists():
        return False
    if not cfg.get("enabled"):
        return False
    if cfg.get("provider") != "cloudbase":
        return False
    endpoint = str(cfg.get("endpoint", "")).strip()
    if not endpoint.startswith("https://"):
        return False
    return True


def _anonymous_id() -> str:
    try:
        if ANON_ID_PATH.exists():
            value = ANON_ID_PATH.read_text(encoding="utf-8").strip()
            if value:
                return value
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        value = str(uuid.uuid4())
        ANON_ID_PATH.write_text(value, encoding="utf-8")
        try:
            os.chmod(ANON_ID_PATH, 0o600)
        except Exception:
            pass
        return value
    except Exception:
        # Session-only random ID if the host cannot persist local state.
        return str(uuid.uuid4())


def capture(event: str) -> None:
    if event not in ALLOWED_EVENTS:
        return
    cfg = _load_config()
    if not _is_enabled(cfg):
        return

    payload = {
        "event_name": event,
        "anonymous_id": _anonymous_id(),
        "skill_version": str(cfg.get("skill_version", "1.8.1")),
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        str(cfg["endpoint"]),
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "DCVlog-Telemetry/1",
        },
        method="POST",
    )
    try:
        timeout = float(cfg.get("timeout_seconds", 1.2))
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read(32)
    except Exception:
        return


def main() -> int:
    if len(sys.argv) < 2:
        return 0
    capture(sys.argv[1].strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
