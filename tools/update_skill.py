"""Synchronize the loaded DCVlog installation with the official main commit.

Stdlib only. No installer subprocesses, credentials, telemetry, or user-data access.
Run with --skill-dir pointing to the directory of the SKILL.md actually loaded.
"""
import argparse
import contextlib
import datetime
import hashlib
import http.client
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse
import uuid
import xml.etree.ElementTree as ElementTree
import zipfile

REPOSITORY = "daichuan-ai/dcvlog"
API = "https://api.github.com/repos/" + REPOSITORY
FEED = "https://github.com/" + REPOSITORY + "/commits/main.atom"
ARCHIVE = "https://codeload.github.com/" + REPOSITORY + "/tar.gz/"
ZIP_ARCHIVE = "https://codeload.github.com/" + REPOSITORY + "/zip/"
MAIN_ARCHIVE = ZIP_ARCHIVE + "refs/heads/main"
STATE_FILE = ".dcvlog-update-state.json"
SHA = re.compile(r"^[0-9a-f]{40}$")
HASH = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r'^version:\s*"?(\d+\.\d+\.\d+)"?\s*$', re.M)
RAW_CASE = "references/corpus/batch-003-raw-20261016/cases.md"
RAW_SHA256 = "4e0edfafe1adfa894213b7cbbe7778a46d67e5525e79fc8afaa3386336dbf067"
REQUIRED = (
    "SKILL.md", "VERSION", "tools/update_skill.py", "tools/case_catalog.py", "tools/telemetry.py",
    "tools/review_upload.py", "references/version-check.md",
    "references/creative-engine-e02.md", "references/corpus/corpus-index.md",
    "references/corpus/catalog.json",
    "references/corpus/batch-002-new/B002-001.md",
    "references/corpus/batch-002-new/B002-002.md",
    "references/corpus/batch-002-new/B002-003.md",
    RAW_CASE,
)
MAX_ARCHIVE = 16 * 1024 * 1024
MAX_UNPACKED = 64 * 1024 * 1024
NETWORK_ERRORS = (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException)


class UpdateError(Exception):
    def __init__(self, status, message, **details):
        super().__init__(message)
        self.status, self.details = status, details


def relative_path(value):
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise UpdateError("invalid_release", "Unsafe relative path")
    return path


def safe_path(root, relative):
    path = root
    for part in relative_path(relative).parts:
        path = path / part
        if path.is_symlink():
            raise UpdateError("unsafe_path", "Managed path contains a symbolic link")
    return path


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def installed_version(root):
    body = safe_path(root, "SKILL.md").read_text(encoding="utf-8")
    parts = body.split("---", 2)
    match = VERSION.search(parts[1]) if body.startswith("---\n") and len(parts) == 3 else None
    identity = re.search(r'^name:\s*["\']?dcvlog["\']?\s*$', parts[1], re.M) if len(parts) == 3 else None
    if not identity:
        raise UpdateError("invalid_target", "Cannot read the loaded Skill version")
    version_file = safe_path(root, "VERSION")
    file_version = version_file.read_text(encoding="utf-8").strip() if version_file.is_file() else None
    if file_version is not None and not re.fullmatch(r"\d+\.\d+\.\d+", file_version):
        raise UpdateError("invalid_target", "Invalid VERSION file")
    if match and file_version and match.group(1) != file_version:
        raise UpdateError("invalid_target", "Installed versions disagree")
    if match:
        return match.group(1)
    # Real Doubao 1.9.0 packages have name/description frontmatter but only
    # store their version in VERSION. Do not mistake this for a bad target.
    if file_version:
        return file_version
    raise UpdateError("invalid_target", "Cannot read the loaded Skill version")


def get_bytes(url, limit, timeout):
    request = urllib.request.Request(url, headers={
        "User-Agent": "DCVlog-Auto-Update", "Accept": "application/vnd.github+json",
        "Cache-Control": "no-cache", "Pragma": "no-cache",
    })
    chunks, size, deadline = [], 0, time.monotonic() + 45
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.hostname not in {
            "api.github.com", "codeload.github.com", "github.com",
        }:
            raise UpdateError("invalid_release", "Unexpected download destination")
        while True:
            if time.monotonic() > deadline:
                raise TimeoutError("Update download timed out")
            chunk = response.read(min(65536, limit + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > limit:
                raise UpdateError("invalid_release", "Download exceeds size limit")
    return b"".join(chunks)


def remote_revision():
    # Public Atom avoids coupling every learner launch to the REST API quota.
    try:
        raw = get_bytes(FEED + "?check=" + str(time.time_ns()), 1024 * 1024, 3)
        namespace = {"a": "http://www.w3.org/2005/Atom"}
        entry = ElementTree.fromstring(raw).find("a:entry", namespace)
        if entry is not None:
            identity = entry.findtext("a:id", default="", namespaces=namespace)
            match = re.fullmatch(r"tag:github.com,2008:Grit::Commit/([0-9a-f]{40})", identity)
            if match:
                revision = match.group(1)
                expected = "https://github.com/" + REPOSITORY + "/commit/" + revision
                if any(link.get("href") == expected and link.get("rel") == "alternate"
                       for link in entry.findall("a:link", namespace)):
                    return revision
    except NETWORK_ERRORS + (ElementTree.ParseError, UpdateError):
        pass
    data = json.loads(get_bytes(API + "/git/ref/heads/main?check=" + str(time.time_ns()), 65536, 3))
    if not isinstance(data, dict) or not isinstance(data.get("object"), dict):
        raise UpdateError("unavailable", "Invalid official revision response")
    revision = data.get("object", {}).get("sha", "")
    if data.get("ref") != "refs/heads/main" or not SHA.fullmatch(revision):
        raise UpdateError("unavailable", "Cannot verify the official main revision")
    return revision


def download_archive(revision):
    if not SHA.fullmatch(revision):
        raise UpdateError("invalid_release", "Invalid commit revision")
    try:
        return get_bytes(ARCHIVE + revision, MAX_ARCHIVE, 8)
    except NETWORK_ERRORS:
        raw = get_bytes(ZIP_ARCHIVE + revision, MAX_ARCHIVE, 12)
        if archive_revision(raw) != revision:
            raise UpdateError("invalid_release", "Archive commit does not match the requested commit")
        return raw


def archive_revision(raw):
    """GitHub's official Git ZIP carries the full commit SHA in its comment."""
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            revision = archive.comment.decode("ascii").strip()
    except (zipfile.BadZipFile, UnicodeError) as error:
        raise UpdateError("invalid_release", "Invalid official ZIP archive") from error
    if not SHA.fullmatch(revision):
        raise UpdateError("invalid_release", "Official ZIP is missing its commit identity")
    return revision


def latest_release():
    try:
        return remote_revision(), None
    except UpdateError as error:
        if error.status != "unavailable":
            raise
    except NETWORK_ERRORS + (json.JSONDecodeError,):
        pass
    # github.com/API can be unavailable while codeload still works. Resolve
    # the commit from the official main ZIP itself, not a third-party mirror.
    raw = get_bytes(MAIN_ARCHIVE + "?check=" + str(time.time_ns()), MAX_ARCHIVE, 12)
    return archive_revision(raw), raw


def unpack_package(raw, destination):
    """Extract only the standard Skill, never repository-root compatibility files."""
    if zipfile.is_zipfile(io.BytesIO(raw)):
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            if len(archive.infolist()) > 5000:
                raise UpdateError("invalid_release", "Archive contains too many entries")
            entries = ((item.filename, item.is_dir(),
                        not item.is_dir() and ((item.external_attr >> 16) & 0o170000) in (0, 0o100000),
                        item.file_size, lambda item=item: archive.open(item))
                       for item in archive.infolist())
            return unpack_entries(entries, destination)
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        entries = ((item.name, item.isdir(), item.isfile(), item.size,
                    lambda item=item: archive.extractfile(item)) for item in archive)
        return unpack_entries(entries, destination)


def unpack_entries(entries, destination):
    total, seen, archive_roots = 0, set(), set()
    for name, is_dir, is_file, size, open_stream in entries:
        path = relative_path(name)
        parts = path.parts
        if len(parts) < 3 or parts[1:3] != ("skills", "dcvlog"):
            continue
        archive_roots.add(parts[0])
        if len(archive_roots) != 1:
            raise UpdateError("invalid_release", "Multiple package roots")
        if is_dir:
            continue
        if not is_file or size > 8 * 1024 * 1024:
            raise UpdateError("invalid_release", "Unsupported archive entry")
        relative = PurePosixPath(*parts[3:]).as_posix()
        if "__pycache__" in parts or relative.endswith((".pyc", ".pyo")):
            continue
        if relative == STATE_FILE or relative in seen:
            raise UpdateError("invalid_release", "Duplicate or reserved package path")
        seen.add(relative)
        total += size
        if total > MAX_UNPACKED or len(seen) > 1000:
            raise UpdateError("invalid_release", "Package exceeds size limit")
        target = safe_path(destination, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open_stream() as stream, target.open("wb") as output:
            shutil.copyfileobj(stream, output)
    if not seen:
        raise UpdateError("invalid_release", "Standard DCVlog package is missing")
    return {name: file_hash(safe_path(destination, name)) for name in sorted(seen)}


def validate_package(root, hashes):
    for name in REQUIRED:
        if name not in hashes or not safe_path(root, name).is_file():
            raise UpdateError("invalid_release", "Incomplete package: " + name)
    try:
        version = installed_version(root)
    except UpdateError as error:
        raise UpdateError("invalid_release", "Invalid release identity or version") from error
    # Compatibility fallback is only for installed legacy targets; official
    # release candidates must still carry matching frontmatter and VERSION.
    body = safe_path(root, "SKILL.md").read_text(encoding="utf-8")
    if not VERSION.search(body.split("---", 2)[1]):
        raise UpdateError("invalid_release", "Release is missing its frontmatter version")
    if safe_path(root, "VERSION").read_text(encoding="utf-8").strip() != version:
        raise UpdateError("invalid_release", "Package versions disagree")
    if hashes[RAW_CASE] != RAW_SHA256:
        raise UpdateError("invalid_release", "Locked original cases have changed")
    return version


def load_state(root):
    path = safe_path(root, STATE_FILE)
    if not path.is_file():
        return None
    try:
        if path.stat().st_size > 512 * 1024:
            return None
        state = json.loads(path.read_text(encoding="utf-8"))
        files = state.get("files", {})
        if (state.get("repository") != REPOSITORY or
                not SHA.fullmatch(state.get("revision", "")) or
                not isinstance(files, dict) or not set(REQUIRED).issubset(files) or
                not re.fullmatch(r"\d+\.\d+\.\d+", str(state.get("version", "")))):
            return None
        for name, digest in files.items():
            relative_path(name)
            if not isinstance(digest, str) or not HASH.fullmatch(digest):
                return None
        return state
    except (ValueError, TypeError, AttributeError, UpdateError):
        return None


def files_match(root, hashes):
    for name, digest in hashes.items():
        path = safe_path(root, name)
        if not path.is_file() or file_hash(path) != digest:
            return False
    return True


def save_state(root, revision, version, hashes):
    target = safe_path(root, STATE_FILE)
    state = {"repository": REPOSITORY, "revision": revision, "version": version, "files": hashes}
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=root,
                                     prefix=".dcvlog-state-", delete=False) as output:
        temp = Path(output.name)
        json.dump(state, output, ensure_ascii=False, sort_keys=True, indent=2)
        output.write("\n")
    try:
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)


@contextlib.contextmanager
def update_lock(target):
    path = target.parent / ("." + target.name + ".dcvlog-update.lock")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise UpdateError("busy", "Another update or a retained lock needs attention", lock_path=str(path))
    try:
        with os.fdopen(fd, "w") as output:
            json.dump({"pid": os.getpid(), "target": str(target)}, output)
        yield
    finally:
        path.unlink(missing_ok=True)


def install_package(target, candidate, revision, version, hashes, previous):
    stage = Path(tempfile.mkdtemp(prefix="." + target.name + ".update-", dir=target.parent))
    backup = None
    try:
        # Preserve local additions; never touch ~/.dcvlog or another installation.
        shutil.copytree(target, stage, dirs_exist_ok=True, symlinks=True)
        for name in (previous or {}).get("files", {}):
            path = safe_path(stage, name)
            if name not in hashes and path.is_file() and file_hash(path) == previous["files"][name]:
                path.unlink()
        for name in hashes:
            path = safe_path(stage, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe_path(candidate, name), path)
        save_state(stage, revision, version, hashes)
        if not files_match(stage, hashes):
            raise UpdateError("invalid_release", "Staged package verification failed")
        backups = target.parent / ("." + target.name + ".dcvlog-backups")
        if backups.is_symlink():
            raise UpdateError("unsafe_path", "Backup directory is a symbolic link")
        backups.mkdir(exist_ok=True)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = backups / (stamp + "-" + uuid.uuid4().hex[:8])
        os.replace(target, backup)
        try:
            os.replace(stage, target)
            if not files_match(target, hashes) or installed_version(target) != version:
                raise UpdateError("verification_failed", "Installed package verification failed")
        except BaseException as error:
            failed = None
            try:
                if target.exists():
                    failed = backups / ("failed-" + uuid.uuid4().hex)
                    os.replace(target, failed)
                os.replace(backup, target)
            except OSError:
                raise UpdateError("recovery_required", "Restore the retained backup before continuing",
                                  backup_path=str(backup), target=str(target)) from error
            raise UpdateError("rolled_back", "Update failed; previous installation restored",
                              failed_path=str(failed) if failed else None) from error
        return str(backup)
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def _sync(target, check_only):
    version = installed_version(target)
    revision, cached_archive = latest_release()
    state = load_state(target)
    common = {"skill_dir": str(target), "installed_version": version, "revision": revision}
    if state and state["revision"] == revision and files_match(target, state["files"]):
        return dict(common, status="up_to_date", verified=True, latest_version=version)
    with tempfile.TemporaryDirectory(prefix=".dcvlog-download-", dir=target.parent) as directory:
        candidate = Path(directory)
        hashes = unpack_package(cached_archive if cached_archive is not None else download_archive(revision), candidate)
        latest = validate_package(candidate, hashes)
        obsolete = set((state or {}).get("files", {})) - set(hashes)
        matches = files_match(target, hashes) and not any(safe_path(target, name).exists() for name in obsolete)
        if check_only:
            return dict(common, status="up_to_date" if matches else "update_available",
                        verified=matches, latest_version=latest)
        if matches:
            save_state(target, revision, latest, hashes)
            return dict(common, status="up_to_date", verified=True, latest_version=latest)
        backup = install_package(target, candidate, revision, latest, hashes, state)
        return dict(common, status="updated", verified=True, latest_version=latest,
                    backup_path=backup, reread_required=True)


def ensure_latest(skill_dir=None, check_only=False):
    requested = Path(skill_dir) if skill_dir is not None else Path(__file__).resolve().parents[1]
    try:
        target = requested.expanduser().resolve(strict=True)
        if not target.is_dir():
            raise UpdateError("invalid_target", "Loaded Skill directory does not exist")
        if not check_only and any((p / ".git").exists() for p in (target, *target.parents)):
            raise UpdateError("developer_checkout", "Do not replace a Git working directory")
        if check_only:
            return _sync(target, True)
        with update_lock(target):
            return _sync(target, False)
    except UpdateError as error:
        return dict(status=error.status, reason=str(error), verified=False, **error.details)
    except PermissionError:
        return {"status": "permission_denied", "verified": False, "reason": "Loaded directory is not writable"}
    except NETWORK_ERRORS + (json.JSONDecodeError,):
        return {"status": "unavailable", "verified": False, "reason": "Cannot verify or download the official release"}
    except (OSError, ValueError, EOFError, tarfile.TarError, zipfile.BadZipFile):
        return {"status": "failed", "verified": False, "reason": "Update could not complete; inspect the installation and backups"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", help="Absolute directory of the SKILL.md actually loaded by the host")
    parser.add_argument("--check", action="store_true", help="Read-only revision check; never installs")
    arguments = parser.parse_args()
    result = ensure_latest(arguments.skill_dir, arguments.check)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"up_to_date", "updated", "update_available"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
