"""Exercise DB source preparation and retired-file cleanup without model claims."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'skills/dcvlog/tools' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


db = load('prepare_bridal_db')
retired = load('retire_features')


class DBPreparationTests(unittest.TestCase):
    def test_installed_modules_do_not_access_network_or_claim_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in db.DEFAULT:
                p = root / name
                p.mkdir()
                (p / 'SKILL.md').write_text('---\nname: ' + name + '\n---\nOriginal procedure')
                (p / 'references').mkdir()
                (p / 'references/detail.md').write_text('Original resource')
            with patch.object(db, 'get', side_effect=AssertionError('Unexpected network')):
                result = db.prepare(installed_root=root, offline=True)
            self.assertEqual(result['status'], 'prepared_not_executed')
            self.assertFalse(result['executed'])
            self.assertEqual(len(result['modules']), 2)
            for item in result['modules']:
                self.assertEqual(item['origin'], 'installed')
                self.assertEqual(len(item['resources']), 2)

    def test_official_download_pins_commit_and_checks_blob_bytes(self):
        revision = 'a' * 40
        files = {}
        for name in db.DEFAULT:
            files['skills/' + name + '/SKILL.md'] = ('---\nname: ' + name + '\n---\nOriginal').encode()
            files['skills/' + name + '/references/detail.md'] = b'Read me'
        tree = {'sha': revision, 'truncated': False, 'tree': [
            {'path': name, 'type': 'blob', 'mode': '100644', 'size': len(data),
             'sha': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()}
            for name, data in files.items()]}
        calls = []

        def get(url, limit=db.LIMIT):
            calls.append(url)
            if '/git/trees/' in url:
                return json.dumps(tree).encode()
            self.assertIn('/' + revision + '/', url)
            return files[url.split('/' + revision + '/', 1)[1]]

        with patch.object(db, 'get', side_effect=get), tempfile.TemporaryDirectory() as temp:
            with patch.object(db.tempfile, 'mkdtemp', return_value=temp):
                modules = db.fetch_modules(db.DEFAULT)
            self.assertEqual({x['revision'] for x in modules}, {revision})
            self.assertTrue(all(Path(x['entrypoint']).is_file() for x in modules))
            self.assertEqual(len(calls), 5)

    def test_missing_installed_dependency_stops_instead_of_faking_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                db.prepare(installed_root=directory, offline=True)

    def test_corrupt_official_file_is_rejected(self):
        tree = {'sha': 'a' * 40, 'truncated': False, 'tree': [
            {'path': 'skills/dbs-script-flow/SKILL.md', 'type': 'blob',
             'mode': '100644', 'size': 3, 'sha': '0' * 40}]}
        with patch.object(db, 'get', side_effect=[json.dumps(tree).encode(), b'bad']):
            with self.assertRaisesRegex(ValueError, 'verification failed'):
                db.fetch_modules(['dbs-script-flow'])


class RetirementTests(unittest.TestCase):
    def make_install(self, root):
        (root / 'references').mkdir()
        (root / 'SKILL.md').write_text('---\nname: dcvlog\nversion: "2.0.0"\n---\n')
        (root / 'VERSION').write_text('2.0.0\n')

    def test_first_hop_removes_old_file_retains_backup_and_user_material(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'installed'
            root.mkdir()
            self.make_install(root)
            old = root / retired.RETIRED[0]
            old.write_text('legacy feature')
            (root / 'my-draft.txt').write_text('private draft')
            result = retired.retire(root)
            self.assertFalse(old.exists())
            self.assertEqual((Path(result['backup_path']) / retired.RETIRED[0]).read_text(), 'legacy feature')
            self.assertEqual((root / 'my-draft.txt').read_text(), 'private draft')
            self.assertEqual(retired.retire(root)['status'], 'clean')

    def test_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'installed'
            root.mkdir()
            self.make_install(root)
            other = Path(directory) / 'external.txt'
            other.write_text('keep')
            (root / retired.RETIRED[0]).symlink_to(other)
            with self.assertRaisesRegex(ValueError, 'symbolic link'):
                retired.retire(root)
            self.assertEqual(other.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
