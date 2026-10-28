"""Behavioral tests for automatic updates; all writes stay in isolated fixtures."""
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import urllib.error
import zipfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("dcvlog_auto_update", ROOT / "skills/dcvlog/tools/update_skill.py")
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)
A, B = "a" * 40, "b" * 40


def package(version="1.9.4", extra=None):
    files = {name: b"reference or tool\n" for name in updater.REQUIRED}
    files["SKILL.md"] = ('---\nname: dcvlog\nversion: "' + version + '"\n---\n').encode()
    files["VERSION"] = (version + "\n").encode()
    files[updater.RAW_CASE] = (ROOT / "skills/dcvlog" / updater.RAW_CASE).read_bytes()
    files.update(extra or {})
    return files


def archive(files, special=None):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w:gz") as output:
        for name, content in files.items():
            info = tarfile.TarInfo("official-commit/skills/dcvlog/" + name)
            info.size = len(content)
            output.addfile(info, io.BytesIO(content))
        if special:
            output.addfile(special)
    return data.getvalue()


def write_files(root, files):
    root.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def zip_archive(files, revision=A):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w", compression=zipfile.ZIP_DEFLATED) as output:
        output.comment = revision.encode("ascii")
        for name, content in files.items():
            output.writestr("dcvlog-main/skills/dcvlog/" + name, content)
    return data.getvalue()


class AutoUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.target = self.root / "installed"
        write_files(self.target, package("1.8.3"))

    def sync(self, files=None, revision=A, target=None, check_only=False):
        with patch.object(updater, "remote_revision", return_value=revision), \
                patch.object(updater, "download_archive", return_value=archive(files or package())) as downloaded:
            result = updater.ensure_latest(target or self.target, check_only)
            return result, downloaded.call_count

    def test_old_version_is_replaced_and_backed_up(self):
        result, calls = self.sync()
        self.assertEqual(result["status"], "updated")
        self.assertTrue(result["verified"])
        self.assertTrue(result["reread_required"])
        self.assertEqual(updater.installed_version(self.target), "1.9.4")
        self.assertEqual(updater.installed_version(Path(result["backup_path"])), "1.8.3")
        self.assertEqual(calls, 1)

    def test_next_launch_checks_revision_without_redownloading(self):
        self.sync()
        result, calls = self.sync()
        self.assertEqual(result["status"], "up_to_date")
        self.assertTrue(result["verified"])
        self.assertEqual(calls, 0)

    def test_same_version_new_case_is_updated(self):
        self.sync()
        name = "references/corpus/batch-002-new/B002-004.md"
        result, _ = self.sync(package(extra={name: "新的创作范本。\n".encode()}), revision=B)
        self.assertEqual(result["status"], "updated")
        self.assertEqual(result["latest_version"], "1.9.4")
        self.assertEqual((self.target / name).read_text(), "新的创作范本。\n")
        self.assertEqual(updater.load_state(self.target)["revision"], B)

    def test_unrelated_commit_only_refreshes_revision_marker(self):
        self.sync()
        result, _ = self.sync(revision=B)
        self.assertEqual(result["status"], "up_to_date")
        self.assertEqual(updater.load_state(self.target)["revision"], B)
        self.assertEqual(len(list((self.root / ".installed.dcvlog-backups").iterdir())), 1)

    def test_resolves_actual_loaded_symlink_without_changing_global_copy(self):
        other = self.root / "global-copy"
        write_files(other, package("1.8.3"))
        alias = self.root / "user-skills-link"
        alias.symlink_to(self.target, target_is_directory=True)
        result, _ = self.sync(target=alias)
        self.assertEqual(result["status"], "updated")
        self.assertTrue(alias.is_symlink())
        self.assertEqual(result["skill_dir"], str(self.target))
        self.assertEqual(updater.installed_version(other), "1.8.3")

    def test_preserves_local_additions_and_external_consent(self):
        local = self.target / "references/corpus/batch-002-new/B002-999.md"
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_text("本地新增，不可丢失。")
        consent = self.root / "home/.dcvlog/consent.json"
        consent.parent.mkdir(parents=True)
        consent.write_text('{"status":"declined","id":"keep-this-id"}')
        before = consent.read_bytes()
        result, _ = self.sync()
        self.assertEqual(result["status"], "updated")
        self.assertEqual(local.read_text(), "本地新增，不可丢失。")
        self.assertEqual(consent.read_bytes(), before)

    def test_network_failure_keeps_original_installation(self):
        original = (self.target / "SKILL.md").read_bytes()
        with patch.object(updater, "remote_revision", side_effect=TimeoutError), \
                patch.object(updater, "get_bytes", side_effect=TimeoutError):
            result = updater.ensure_latest(self.target)
        self.assertEqual(result["status"], "unavailable")
        self.assertFalse(result["verified"])
        self.assertEqual((self.target / "SKILL.md").read_bytes(), original)
        self.assertFalse((self.root / ".installed.dcvlog-update.lock").exists())

    def test_read_only_check_verifies_release_without_changing_installation(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result, calls = self.sync(check_only=True)
        self.assertEqual(result["status"], "update_available")
        self.assertFalse(result["verified"])
        self.assertEqual(calls, 1)
        self.assertEqual(result["latest_version"], package()["VERSION"].decode().strip())
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_legacy_doubao_header_uses_VERSION_and_can_upgrade(self):
        old = b'---\nname: dcvlog\ndescription: "legacy Doubao package"\n---\n# V1.9.0\n'
        write_files(self.target, package("1.9.0", {"SKILL.md": old}))
        self.assertEqual(updater.installed_version(self.target), "1.9.0")
        result, _ = self.sync()
        self.assertEqual(result["status"], "updated")
        self.assertEqual((Path(result["backup_path"]) / "SKILL.md").read_bytes(), old)

    def test_conflicting_installed_versions_are_rejected(self):
        (self.target / "VERSION").write_text("9.9.9\n")
        result, calls = self.sync()
        self.assertEqual(result["status"], "invalid_target")
        self.assertEqual(calls, 0)

    def test_VERSION_fallback_still_requires_dcvlog_identity(self):
        (self.target / "SKILL.md").write_text('---\nname: another-skill\n---\n')
        result, calls = self.sync()
        self.assertEqual(result["status"], "invalid_target")
        self.assertEqual(calls, 0)

    def test_legacy_fallback_does_not_accept_invalid_release_metadata(self):
        files = package(extra={"SKILL.md": b'---\nname: dcvlog\n---\n'})
        result, _ = self.sync(files)
        self.assertEqual(result["status"], "invalid_release")

    def test_same_files_without_state_are_not_falsely_reported_as_new(self):
        write_files(self.target, package())
        result, calls = self.sync(check_only=True)
        self.assertEqual(result["status"], "up_to_date")
        self.assertTrue(result["verified"])
        self.assertEqual(calls, 1)
        self.assertFalse((self.target / updater.STATE_FILE).exists())

    def test_official_main_zip_works_when_github_and_api_are_unavailable(self):
        raw = zip_archive(package(extra={"references/中文说明.md": "中文文件名。\n".encode()}))
        requested = []
        def transport(url, limit, timeout):
            requested.append(url)
            if url.startswith(updater.MAIN_ARCHIVE + "?check="):
                return raw
            raise urllib.error.URLError("metadata endpoint unavailable")
        with patch.object(updater, "get_bytes", side_effect=transport):
            result = updater.ensure_latest(self.target)
        self.assertEqual(result["status"], "updated")
        self.assertTrue(result["verified"])
        self.assertEqual(result["revision"], A)
        self.assertEqual((self.target / "references/中文说明.md").read_text(), "中文文件名。\n")
        self.assertEqual(len(requested), 3)
        self.assertTrue(requested[-1].startswith(updater.MAIN_ARCHIVE))

    def test_official_zip_missing_commit_identity_is_rejected(self):
        raw = zip_archive(package(), revision="not-a-commit")
        with patch.object(updater, "remote_revision", side_effect=TimeoutError), \
                patch.object(updater, "get_bytes", return_value=raw):
            result = updater.ensure_latest(self.target)
        self.assertEqual(result["status"], "invalid_release")
        self.assertEqual(updater.installed_version(self.target), "1.8.3")

    def test_tar_transport_failure_uses_zip_pinned_to_same_commit(self):
        raw = zip_archive(package())
        with patch.object(updater, "get_bytes", side_effect=[TimeoutError(), raw]) as transport:
            self.assertEqual(updater.download_archive(A), raw)
        self.assertEqual([c.args[0] for c in transport.call_args_list],
                         [updater.ARCHIVE + A, updater.ZIP_ARCHIVE + A])

    def test_pinned_zip_cannot_return_another_commit(self):
        with patch.object(updater, "get_bytes", side_effect=[TimeoutError(), zip_archive(package(), B)]):
            with self.assertRaises(updater.UpdateError):
                updater.download_archive(A)

    def test_zip_path_traversal_is_rejected(self):
        raw = zip_archive(package(extra={"../../outside": b"bad"}))
        with patch.object(updater, "remote_revision", return_value=A), \
                patch.object(updater, "download_archive", return_value=raw):
            result = updater.ensure_latest(self.target)
        self.assertEqual(result["status"], "invalid_release")
        self.assertFalse((self.root / "outside").exists())

    def test_zip_symbolic_link_is_rejected(self):
        raw = io.BytesIO(zip_archive(package()))
        with zipfile.ZipFile(raw, "a") as archive:
            item = zipfile.ZipInfo("dcvlog-main/skills/dcvlog/references/escape")
            item.create_system = 3
            item.external_attr = 0o120777 << 16
            archive.writestr(item, "/outside")
        with patch.object(updater, "remote_revision", return_value=A), \
                patch.object(updater, "download_archive", return_value=raw.getvalue()):
            result = updater.ensure_latest(self.target)
        self.assertEqual(result["status"], "invalid_release")

    def test_permission_failure_is_not_success(self):
        with patch.object(updater.os, "open", side_effect=PermissionError):
            result = updater.ensure_latest(self.target)
        self.assertEqual(result["status"], "permission_denied")
        self.assertEqual(updater.installed_version(self.target), "1.8.3")

    def test_existing_lock_is_not_deleted(self):
        lock = self.root / ".installed.dcvlog-update.lock"
        lock.write_text("existing lock")
        result, calls = self.sync()
        self.assertEqual(result["status"], "busy")
        self.assertEqual(calls, 0)
        self.assertEqual(lock.read_text(), "existing lock")

    def test_incomplete_package_is_rejected(self):
        files = package()
        del files["tools/review_upload.py"]
        result, _ = self.sync(files)
        self.assertEqual(result["status"], "invalid_release")
        self.assertEqual(updater.installed_version(self.target), "1.8.3")

    def test_package_without_approved_case_library_is_not_installed(self):
        files = package()
        del files["references/corpus/batch-002-new/B002-001.md"]
        result, _ = self.sync(files)
        self.assertEqual(result["status"], "invalid_release")
        self.assertEqual(updater.installed_version(self.target), "1.8.3")

    def test_mismatched_versions_are_rejected(self):
        result, _ = self.sync(package(extra={"VERSION": b"9.9.9\n"}))
        self.assertEqual(result["status"], "invalid_release")

    def test_changed_locked_raw_cases_are_rejected(self):
        result, _ = self.sync(package(extra={updater.RAW_CASE: b"changed original"}))
        self.assertEqual(result["status"], "invalid_release")

    def test_path_traversal_cannot_escape(self):
        result, _ = self.sync(package(extra={"../../outside": b"bad"}))
        self.assertEqual(result["status"], "invalid_release")
        self.assertFalse((self.root / "outside").exists())

    def test_archive_symlink_is_rejected(self):
        entry = tarfile.TarInfo("official-commit/skills/dcvlog/references/escape")
        entry.type = tarfile.SYMTYPE
        entry.linkname = str(self.root)
        with patch.object(updater, "remote_revision", return_value=A), \
                patch.object(updater, "download_archive", return_value=archive(package(), entry)):
            result = updater.ensure_latest(self.target)
        self.assertEqual(result["status"], "invalid_release")

    def test_existing_managed_symlink_never_writes_outside_target(self):
        outside = self.root / "outside.md"
        outside.write_text("keep")
        path = self.target / "references/version-check.md"
        path.unlink()
        path.symlink_to(outside)
        result, _ = self.sync()
        self.assertEqual(result["status"], "unsafe_path")
        self.assertEqual(outside.read_text(), "keep")
        self.assertEqual(updater.installed_version(self.target), "1.8.3")

    def test_replace_failure_restores_old_directory(self):
        original_replace = updater.os.replace
        def fail_stage(source, dest):
            if Path(source).name.startswith(".installed.update-") and Path(dest) == self.target:
                raise OSError("simulated replacement failure")
            return original_replace(source, dest)
        with patch.object(updater.os, "replace", side_effect=fail_stage):
            result, _ = self.sync()
        self.assertEqual(result["status"], "rolled_back")
        self.assertEqual(updater.installed_version(self.target), "1.8.3")

    def test_readback_failure_restores_old_and_retains_failed_copy(self):
        original_match = updater.files_match
        def fail_new_target(root, hashes):
            if root == self.target and updater.installed_version(root) == "1.9.4":
                return False
            return original_match(root, hashes)
        with patch.object(updater, "files_match", side_effect=fail_new_target):
            result, _ = self.sync()
        self.assertEqual(result["status"], "rolled_back")
        self.assertEqual(updater.installed_version(self.target), "1.8.3")
        self.assertTrue(Path(result["failed_path"]).is_dir())

    def test_damaged_managed_file_is_repaired(self):
        self.sync()
        path = self.target / "references/version-check.md"
        path.write_text("locally modified")
        result, _ = self.sync()
        self.assertEqual(result["status"], "updated")
        self.assertEqual(path.read_bytes(), package()["references/version-check.md"])
        self.assertEqual((Path(result["backup_path"]) / "references/version-check.md").read_text(), "locally modified")

    def test_developer_checkout_is_not_overwritten(self):
        (self.root / ".git").mkdir()
        result, calls = self.sync()
        self.assertEqual(result["status"], "developer_checkout")
        self.assertEqual(calls, 0)

    def test_invalid_state_is_rechecked_safely(self):
        (self.target / updater.STATE_FILE).write_text("[]")
        result, _ = self.sync()
        self.assertEqual(result["status"], "updated")

    def test_invalid_revision_response_is_not_latest(self):
        with patch.object(updater, "get_bytes", return_value=b'[]'):
            with self.assertRaises(updater.UpdateError):
                updater.remote_revision()

    def test_revision_request_is_read_only_and_contains_no_credentials(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def geturl(self): return updater.FEED
            def read(self, size):
                if getattr(self, "done", False): return b""
                self.done = True
                return ('<feed xmlns="http://www.w3.org/2005/Atom"><entry>'
                        '<id>tag:github.com,2008:Grit::Commit/' + A + '</id>'
                        '<link rel="alternate" href="https://github.com/' + updater.REPOSITORY +
                        '/commit/' + A + '"/></entry></feed>').encode()
        with patch.object(updater.urllib.request, "urlopen", return_value=Response()) as network:
            self.assertEqual(updater.remote_revision(), A)
        request = network.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.data)
        self.assertIsNone(request.get_header("Authorization"))
        self.assertTrue(request.full_url.startswith(updater.FEED + "?check="))
        self.assertEqual(network.call_count, 1)

    def test_archive_download_is_pinned_to_verified_commit(self):
        with patch.object(updater, "get_bytes", return_value=b"archive") as network:
            self.assertEqual(updater.download_archive(A), b"archive")
        self.assertEqual(network.call_args.args[0], updater.ARCHIVE + A)

    def test_api_fallback_after_feed_is_unavailable(self):
        response = json.dumps({"ref": "refs/heads/main", "object": {"sha": A}}).encode()
        with patch.object(updater, "get_bytes", side_effect=[TimeoutError(), response]) as network:
            self.assertEqual(updater.remote_revision(), A)
        self.assertTrue(network.call_args.args[0].startswith(updater.API + "/git/ref/heads/main"))

    def test_download_does_not_follow_an_unexpected_destination(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def geturl(self): return "https://example.test/untrusted"
        with patch.object(updater.urllib.request, "urlopen", return_value=Response()):
            with self.assertRaises(updater.UpdateError):
                updater.get_bytes(updater.API, 100, 3)

    def test_truncated_archive_is_not_installed(self):
        with patch.object(updater, "remote_revision", return_value=A), \
                patch.object(updater, "download_archive", return_value=b"not a gzip"):
            result = updater.ensure_latest(self.target)
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["verified"])
        self.assertEqual(updater.installed_version(self.target), "1.8.3")


if __name__ == "__main__":
    unittest.main()
