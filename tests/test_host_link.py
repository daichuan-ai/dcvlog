import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "dcvlog_host_link", ROOT / "skills/dcvlog/scripts/link_host.py")
linker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(linker)


class HostLinkTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve()
        self.source = self.home / ".agents/skills/dcvlog"
        shutil.copytree(ROOT / "skills/dcvlog", self.source,
                        ignore=shutil.ignore_patterns("__pycache__"))

    def link(self, **kwargs):
        return linker.link_host(self.source, "workbuddy", home=self.home,
                                environ={}, **kwargs)

    def test_link_is_idempotent_and_shares_new_cases(self):
        first = self.link()
        self.assertTrue(first["verified"])
        self.assertFalse(first["host_registration_verified"])
        self.assertFalse(first["cloud_persistence_verified"])
        target = Path(first["target"])
        self.assertTrue(target.is_symlink())
        # Host reads the same source; newly added cases need no second copy.
        (self.source / "references/new-case.md").write_text("new")
        self.assertEqual((target / "references/new-case.md").read_text(), "new")
        self.assertEqual(self.link()["status"], "linked")

    def test_existing_directory_is_untouched(self):
        target = self.home / ".workbuddy/skills/dcvlog"
        target.mkdir(parents=True)
        (target / "personal.txt").write_text("keep")
        self.assertEqual(self.link()["status"], "conflict")
        self.assertEqual((target / "personal.txt").read_text(), "keep")

    def test_broken_link_is_untouched(self):
        target = self.home / ".workbuddy/skills/dcvlog"
        target.parent.mkdir(parents=True)
        target.symlink_to(self.home / "missing", target_is_directory=True)
        self.assertEqual(self.link()["status"], "conflict")
        self.assertEqual(os.readlink(target), str(self.home / "missing"))

    def test_workbuddy_configuration_override(self):
        configured = self.home / "custom host"
        result = linker.link_host(self.source, "workbuddy", home=self.home,
                                  environ={"WORKBUDDY_CONFIG_DIR": str(configured)})
        self.assertEqual(Path(result["target"]), configured / "skills/dcvlog")
        self.assertTrue(result["verified"])

    def test_doubao_uses_the_active_cloud_workspace(self):
        workspace = self.home / "cloud/workspace"
        (workspace / ".user_skills").mkdir(parents=True)
        builtin = workspace / ".skills/builtin"
        builtin.mkdir(parents=True)
        result = linker.link_host(self.source, "doubao", home=self.home, environ={},
                                  active_skill_dir=str(builtin))
        self.assertEqual(Path(result["target"]), workspace / ".user_skills/dcvlog")
        self.assertTrue(result["verified"])

    def test_readonly_check_does_not_create_directories(self):
        self.assertEqual(self.link(check=True)["status"], "missing")
        self.assertFalse((self.home / ".workbuddy").exists())

    def test_corrupt_corpus_is_rejected_before_linking(self):
        raw = self.source / "references/corpus/batch-003-raw-20261016/cases.md"
        raw.write_text("corrupted")
        self.assertEqual(self.link()["status"], "failed")
        self.assertFalse((self.home / ".workbuddy").exists())

    def test_link_permission_failure_does_not_create_a_copy(self):
        with patch.object(linker.os, "symlink", side_effect=PermissionError("denied")):
            result = self.link()
        self.assertEqual(result["status"], "failed")
        self.assertFalse((self.home / ".workbuddy/skills/dcvlog").exists())

    def test_cloud_target_is_explicit_and_still_not_registration(self):
        target = self.home / "confirmed-cloud-skills/dcvlog"
        result = self.link(target_dir=str(target))
        self.assertTrue(result["verified"])
        self.assertEqual(target.resolve(), self.source)
        self.assertFalse(result["cloud_persistence_verified"])

    def test_recursive_target_is_rejected(self):
        result = self.link(target_dir=str(self.source / "nested/dcvlog"))
        self.assertEqual(result["status"], "failed")
        self.assertFalse((self.source / "nested").exists())


if __name__ == "__main__":
    unittest.main()
