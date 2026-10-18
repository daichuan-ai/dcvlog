#!/usr/bin/env python3
"""Consent-gated upload of a *final* DCVlog narration for a small pilot.

This is separate from telemetry.py. It is disabled until the teacher deploys
an independent collection endpoint and enables review-config.json. No prompt,
chat history, photo, file name, or credential is ever sent by this module.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path

from telemetry import _anonymous_id


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "review-config.json"
STATE_DIR = Path.home() / ".dcvlog"
CONSENT_FILE = STATE_DIR / "review_consent.json"

PHONE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
EMAIL = re.compile(r"(?<![\w.-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?!\w)")
ID_CARD = re.compile(r"(?<!\d)\d{17}[0-9Xx](?!\w)")
WECHAT = re.compile(r"(?i)(?:微信号|微信|vx|v信|wechat)\s*[:：=]?\s*([a-z][\w-]{5,19})")


def load_config() -> dict:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        return config if isinstance(config, dict) else {}
    except (OSError, ValueError):
        return {}


def feature_ready(config: dict) -> bool:
    """Never collect content when the teacher hasn't enabled the endpoint."""
    if os.environ.get("DCVLOG_REVIEW_UPLOAD", "").lower() in {"0", "false", "off", "no"}:
        return False
    endpoint = config.get("endpoint", "")
    return (config.get("enabled") is True and
            config.get("provider") == "cloudbase" and
            isinstance(endpoint, str) and endpoint.startswith("https://") and
            bool(config.get("consent_version")))


def read_consent(config: dict) -> str:
    if not feature_ready(config):
        return "disabled"
    try:
        info = json.loads(CONSENT_FILE.read_text(encoding="utf-8"))
        if info.get("consent_version") != config["consent_version"]:
            return "unset"
        if info.get("decision") == "yes":
            return "agreed"
        if info.get("decision") == "no":
            return "declined"
    except (OSError, ValueError, AttributeError):
        pass
    return "unset"


def set_consent(config: dict, decision: str) -> bool:
    if not feature_ready(config):
        return False
    if decision not in ("yes", "no"):
        return False
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = CONSENT_FILE.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as writer:
            json.dump({"decision": decision, "consent_version": config["consent_version"]}, writer)
        os.chmod(tmp, 0o600)
        tmp.replace(CONSENT_FILE)
        return True
    except OSError:
        return False


def redact_personal_contacts(value: str) -> str:
    """Mask recognizable contact/ID formats; this is *not* complete anonymization."""
    value = EMAIL.sub("[邮箱已隐去]", value)
    value = PHONE.sub("[手机号已隐去]", value)
    value = ID_CARD.sub("[身份证号已隐去]", value)
    value = WECHAT.sub("[微信号已隐去]", value)
    return value


def prepare_submission(config: dict, final_text: str, facts_summary: str,
                       client_count: int, draft_status: str, submission_id: str) -> dict:
    final_text = redact_personal_contacts(final_text.strip())
    facts_summary = redact_personal_contacts(facts_summary.strip())
    if not 20 <= len(final_text) <= 12000:
        raise ValueError("final_text must be 20-12000 characters")
    if len(facts_summary) > 1600:
        raise ValueError("facts_summary must be <=1600 characters")
    if not 1 <= client_count <= 20:
        raise ValueError("client_count must be 1-20")
    if draft_status not in {"ready", "limited"}:
        raise ValueError("unknown draft_status")
    try:
        submission_id = str(uuid.UUID(submission_id))
    except (ValueError, AttributeError) as exc:
        raise ValueError("submission_id must be UUID") from exc
    return {
        "submission_id": submission_id,
        "anonymous_id": _anonymous_id(),
        "skill_version": "1.8.7",
        "client_count": client_count,
        "draft_status": draft_status,
        "final_text": final_text,
        "facts_summary": facts_summary,
        "consent": True,
        "consent_version": config["consent_version"],
    }


def submit(config: dict, final_file: Path, facts_file: Path | None,
           client_count: int, draft_status: str, submission_id: str) -> bool:
    """Returns False on *every* failure; never interrupts an author's script."""
    if read_consent(config) != "agreed":
        return False
    try:
        final_text = final_file.read_text(encoding="utf-8")
        facts = facts_file.read_text(encoding="utf-8") if facts_file else ""
        body = prepare_submission(config, final_text, facts, client_count,
                                  draft_status, submission_id)
        req = urllib.request.Request(
            config["endpoint"],
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "DCVlog-Review/1"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=float(config.get("timeout_seconds", 4))) as reply:
            result = json.loads(reply.read(512).decode("utf-8"))
            return 200 <= reply.status < 300 and result.get("accepted") is True
    except (OSError, ValueError, TypeError, urllib.error.URLError):
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DCVlog consent-based final narration collection")
    cmds = parser.add_subparsers(dest="command", required=True)
    cmds.add_parser("status")
    cmds.add_parser("agree")
    cmds.add_parser("decline")
    upload = cmds.add_parser("submit")
    upload.add_argument("--final-file", required=True, type=Path)
    upload.add_argument("--facts-file", type=Path)
    upload.add_argument("--clients", required=True, type=int)
    upload.add_argument("--draft-status", default="ready", choices=("ready", "limited"))
    upload.add_argument("--submission-id", default=None)
    args = parser.parse_args(argv)
    config = load_config()
    if args.command == "status":
        print(json.dumps({"status": read_consent(config)}, ensure_ascii=False))
    elif args.command in ("agree", "decline"):
        decision = "yes" if args.command == "agree" else "no"
        written = set_consent(config, decision)
        print(json.dumps({"saved": written, "status": read_consent(config)}, ensure_ascii=False))
    else:
        submission_id = args.submission_id or str(uuid.uuid4())
        success = submit(config, args.final_file, args.facts_file, args.clients,
                         args.draft_status, submission_id)
        # No copy of the final narration is printed to stdout or log.
        print(json.dumps({"uploaded": success}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
