"""Offline regression tests for the read-only version-check helper."""
import importlib.util
import io
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "dcvlog" / "tools" / "check_update.py"
spec = importlib.util.spec_from_file_location("dcvlog_check_update", SCRIPT)
check_update = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_update)


class VersionCheckTests(unittest.TestCase):
    def test_installed_version_parses_skill(self):
        self.assertEqual(check_update.installed_version(), (SCRIPT.parents[1] / "VERSION").read_text().strip())

    def test_detects_new_version(self):
        self.assertEqual(check_update.compare_versions("1.8.6", "1.8.7")["status"], "update_available")

    def test_equal_is_silent_status(self):
        self.assertEqual(check_update.compare_versions("1.8.6", "1.8.6")["status"], "up_to_date")

    def test_older_remote_is_silent_status(self):
        self.assertEqual(check_update.compare_versions("1.8.6", "1.8.5")["status"], "up_to_date")

    def test_semantic_numbers_not_strings(self):
        self.assertEqual(check_update.compare_versions("1.8.9", "1.8.10")["status"], "update_available")

    def test_rejects_untrusted_remote_contents(self):
        for invalid in ("hello", "1.8.7\nrm -rf /", "v1.8.7", ""):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    check_update.compare_versions("1.8.6", invalid)

    def test_network_fail_does_not_raise(self):
        with patch.object(check_update, "remote_version", side_effect=TimeoutError("network unavailable")):
            self.assertEqual(check_update.check()["status"], "unavailable")

    def test_remote_version_is_read_only(self):
        class MockResponse:
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def read(self, max_bytes):
                self.max_bytes = max_bytes
                return b"1.8.7\n"

        fake_response = MockResponse()
        with patch.object(check_update.urllib.request, "urlopen", return_value=fake_response) as opened:
            self.assertEqual(check_update.remote_version(), "1.8.7")
            self.assertEqual(fake_response.max_bytes, 48)
            self.assertEqual(opened.call_args.kwargs["timeout"], 2.5)


if __name__ == "__main__":
    unittest.main()
