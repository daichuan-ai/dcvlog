"""Read-only, best-effort DCVlog version check on explicit /dcvlog launch."""
import json
import re
import urllib.request
from pathlib import Path

VERSION_URL = "https://raw.githubusercontent.com/daichuan-ai/dcvlog/main/VERSION"
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
FRONTMATTER_VERSION = re.compile(r'^version:\s*"?(?P<version>\d+\.\d+\.\d+)"?\s*$', re.M)


def parse_version(value):
    value = value.strip()
    if not VERSION_PATTERN.fullmatch(value):
        raise ValueError("invalid version")
    return tuple(int(part) for part in value.split("."))


def installed_version(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    skill = root / "SKILL.md"
    body = skill.read_text(encoding="utf-8")
    if not body.startswith("---\n"):
        raise ValueError("invalid frontmatter")
    frontmatter = body.split("---", 2)[1]
    if not re.search(r'^name:\s*["\']?dcvlog["\']?\s*$', frontmatter, re.M):
        raise ValueError("invalid skill identity")
    match = FRONTMATTER_VERSION.search(frontmatter)
    version_file = root / "VERSION"
    file_version = version_file.read_text(encoding="utf-8").strip() if version_file.is_file() else None
    if file_version is not None:
        parse_version(file_version)
    if match and file_version and match.group("version") != file_version:
        raise ValueError("installed versions disagree")
    if match:
        return match.group("version")
    if file_version:
        return file_version
    raise ValueError("missing version")


def remote_version():
    request = urllib.request.Request(
        VERSION_URL,
        headers={"User-Agent": "DCVlog-Version-Check/1.9.4", "Accept": "text/plain"},
    )
    with urllib.request.urlopen(request, timeout=2.5) as response:
        raw = response.read(48)
    value = raw.decode("utf-8").strip()
    parse_version(value)
    return value


def compare_versions(installed, remote):
    left = parse_version(installed)
    right = parse_version(remote)
    return {
        "status": "update_available" if right > left else "up_to_date",
        "installed_version": installed,
        "latest_version": remote,
    }


def check():
    try:
        return compare_versions(installed_version(), remote_version())
    except Exception:
        # Read-only checks may fail in the host or on the learner's network.
        # Do not interrupt their writing/collage workflow.
        return {"status": "unavailable"}


if __name__ == "__main__":
    print(json.dumps(check(), ensure_ascii=False, separators=(",", ":")))
