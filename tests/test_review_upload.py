import importlib.util
import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "skills" / "dcvlog" / "tools"))
import review_upload as uploader


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size):
        return b'{"accepted":true}'


class ReviewUploadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = {"enabled": True, "provider": "cloudbase",
                       "endpoint": "https://review.example.test/ingest",
                       "consent_version": "2026-10-18-v1", "timeout_seconds": 1}
        self.final_file = self.root / "final.txt"
        self.final_file.write_text("今天的姑娘来过生日，我们没有照搬参考图，而是留住她原来的笑眼，成片看着很灵动。", encoding="utf-8")
        self.state = patch.object(uploader, "STATE_DIR", self.root)
        self.consent_path = patch.object(uploader, "CONSENT_FILE", self.root / "consent.json")
        self.state.start()
        self.consent_path.start()
        self.addCleanup(self.state.stop)
        self.addCleanup(self.consent_path.stop)

    def test_default_disabled_and_no_upload(self):
        self.assertEqual(uploader.read_consent({"enabled": False}), "disabled")
        self.assertFalse(uploader.submit({"enabled": False}, self.final_file, None, 1, "ready", str(uuid.uuid4())))

    def test_explicit_consent_once_then_decline(self):
        self.assertEqual(uploader.read_consent(self.config), "unset")
        self.assertTrue(uploader.set_consent(self.config, "yes"))
        self.assertEqual(uploader.read_consent(self.config), "agreed")
        self.assertTrue(uploader.set_consent(self.config, "no"))
        self.assertEqual(uploader.read_consent(self.config), "declined")
        self.assertFalse(uploader.submit(self.config, self.final_file, None, 1, "ready", str(uuid.uuid4())))

    def test_consent_version_change_needs_new_permission(self):
        uploader.set_consent(self.config, "yes")
        changed = {**self.config, "consent_version": "new-policy"}
        self.assertEqual(uploader.read_consent(changed), "unset")

    def test_submission_requires_agreement_and_masks_contacts(self):
        self.final_file.write_text("今天来的是一个要过生日的姑娘。她说打电话13812345678，加微信号：abc123456。整体选择柔和的颜色。", encoding="utf-8")
        self.assertFalse(uploader.submit(self.config, self.final_file, None, 1, "ready", str(uuid.uuid4())))
        uploader.set_consent(self.config, "yes")
        request_id = str(uuid.uuid4())
        captured = []

        def fake_urlopen(req, timeout):
            captured.append(json.loads(req.data.decode("utf-8")))
            return FakeResponse()

        with patch.object(uploader.urllib.request, "urlopen", side_effect=fake_urlopen), \
             patch.object(uploader, "_anonymous_id", return_value=str(uuid.uuid4())):
            self.assertTrue(uploader.submit(self.config, self.final_file, None, 1, "ready", request_id))
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0]["submission_id"], request_id)
        self.assertIn("[手机号已隐去]", captured[0]["final_text"])
        self.assertIn("[微信号已隐去]", captured[0]["final_text"])
        self.assertNotIn("13812345678", captured[0]["final_text"])

    def test_offline_does_not_interrupt(self):
        uploader.set_consent(self.config, "yes")
        with patch.object(uploader.urllib.request, "urlopen", side_effect=OSError("offline")):
            self.assertFalse(uploader.submit(self.config, self.final_file, None, 1, "ready", str(uuid.uuid4())))


if __name__ == "__main__":
    unittest.main()
