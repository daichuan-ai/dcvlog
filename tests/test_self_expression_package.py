"""Check the actual install payload and its discoverable third-branch resources."""
import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/dcvlog'
MODULES = {'references/self-expression/index.md'}

SPEC = importlib.util.spec_from_file_location(
    'self_expression_updater', SKILL / 'tools/update_skill.py')
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)


class SelfExpressionPackageTests(unittest.TestCase):
    def test_real_install_payload_passes_update_validation(self):
        self.assertTrue(MODULES.issubset(updater.REQUIRED))
        hashes = {
            path.relative_to(SKILL).as_posix(): updater.file_hash(path)
            for path in SKILL.rglob('*')
            if path.is_file() and '__pycache__' not in path.parts
        }
        self.assertEqual(updater.validate_package(SKILL, hashes),
                         (ROOT / 'VERSION').read_text().strip())

    def test_all_third_branch_references_are_reachable_from_main_entry(self):
        pending, visited = ['SKILL.md'], set()
        while pending:
            name = pending.pop()
            if name in visited:
                continue
            visited.add(name)
            path = SKILL / name
            self.assertTrue(path.is_file(), name)
            self.assertTrue(path.read_text().strip(), name)
            pending.extend(re.findall(
                r'references/self-expression/[a-z-]+\.md', path.read_text()))
        self.assertTrue(MODULES.issubset(visited))
        self.assertEqual(list((SKILL / 'references/self-expression').rglob('SKILL.md')), [])

    def test_release_versions_agree_across_install_channels(self):
        version = (ROOT / 'VERSION').read_text().strip()
        self.assertEqual((SKILL / 'VERSION').read_text().strip(), version)
        self.assertEqual(updater.installed_version(SKILL), version)
        plugin = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
        market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        self.assertEqual(plugin['version'], version)
        self.assertEqual(plugin['skills'], ['./skills/dcvlog'])
        self.assertEqual(market['metadata']['version'], version)
        self.assertEqual(market['plugins'][0]['version'], version)
        for path in (ROOT / 'telemetry-config.json', SKILL / 'telemetry-config.json'):
            self.assertEqual(json.loads(path.read_text())['skill_version'], version)


if __name__ == '__main__':
    unittest.main()
