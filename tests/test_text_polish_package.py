"""Exercise the shipped polish module through a complete, isolated update."""
import hashlib
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from test_update_skill import archive, updater, write_files


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/dcvlog'
MODULE = SKILL / 'references/text-polish'
SOURCE_HASHES = {
    'index.md': '4cf382d9fc7ebf2a6e71c30e2b54aa23f815e223c2c69be757dde16eaead92ba',
    'references/generation-workbench.md': 'a8f9b2a58e80fde3b06bc6bf76ce62689d3199a0610032335190386537bf45ab',
    'references/language-methods.md': '03be9dbcd9d629df2149b07ff5105b5381d24dd18b5c00ed62357fa74a959e2d',
    'references/language-profile.md': 'f78a27a15e31f53ece0774e4e54bac40a797b435f5ce26587ae1be541925eb71',
    'references/source-index.md': '5891cbd9bc6fb4415435b1aa758036df0ece00315a7bfed7e34b3d941befa744',
}


def payload():
    return {p.relative_to(SKILL).as_posix(): p.read_bytes()
            for p in SKILL.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts}


class TextPolishPackageTests(unittest.TestCase):
    def test_full_v2_content_and_resolvable_relative_links(self):
        pending, visited = [MODULE / 'index.md'], set()
        while pending:
            p = pending.pop().resolve()
            if p in visited:
                continue
            visited.add(p)
            self.assertTrue(p.is_file(), str(p))
            for url in re.findall(r'\]\(([^)]+)\)', p.read_text()):
                if not url.startswith(('https://', 'http://', '#')):
                    linked = (p.parent / url.split('#')[0]).resolve()
                    self.assertTrue(MODULE.resolve() in linked.parents, str(linked))
                    pending.append(linked)
        self.assertEqual(visited, {(MODULE / name).resolve() for name in SOURCE_HASHES})
        for name, expected in SOURCE_HASHES.items():
            self.assertEqual(hashlib.sha256((MODULE / name).read_bytes()).hexdigest(), expected)
        # Hosts recursively discover SKILL.md. Nested runtime references must not
        # turn into a second independently installed skill.
        self.assertEqual(list(SKILL.rglob('SKILL.md')), [SKILL / 'SKILL.md'])

    def test_real_payload_updates_old_install_with_all_references(self):
        files = payload()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'host/skills/dcvlog'
            write_files(target, {'SKILL.md': b'---\nname: dcvlog\nversion: "2.3.0"\n---\n',
                                 'VERSION': b'2.3.0\n', 'private-note.txt': b'keep my note'})
            with patch.object(updater, 'remote_revision', return_value='e' * 40), \
                    patch.object(updater, 'download_archive', return_value=archive(files)):
                result = updater.ensure_latest(target)
                self.assertEqual(result['status'], 'updated')
                self.assertTrue(result['verified'])
                for name, data in files.items():
                    self.assertEqual((target / name).read_bytes(), data)
                self.assertEqual((target / 'private-note.txt').read_bytes(), b'keep my note')
                self.assertEqual(updater.ensure_latest(target)['status'], 'up_to_date')

    def test_missing_each_polish_file_rejects_update_without_touching_old_install(self):
        for name in SOURCE_HASHES:
            with self.subTest(missing=name), tempfile.TemporaryDirectory() as directory:
                target = Path(directory) / 'host/skills/dcvlog'
                before = {'SKILL.md': b'---\nname: dcvlog\nversion: "2.3.0"\n---\n',
                          'VERSION': b'2.3.0\n', 'private-note.txt': b'keep my note'}
                write_files(target, before)
                files = payload()
                del files['references/text-polish/' + name]
                with patch.object(updater, 'remote_revision', return_value='e' * 40), \
                        patch.object(updater, 'download_archive', return_value=archive(files)):
                    result = updater.ensure_latest(target)
                self.assertEqual(result['status'], 'invalid_release')
                self.assertFalse(result['verified'])
                self.assertEqual({p.relative_to(target).as_posix(): p.read_bytes()
                                  for p in target.rglob('*') if p.is_file()}, before)


if __name__ == '__main__':
    unittest.main()
