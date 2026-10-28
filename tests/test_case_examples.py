import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('catalog_examples', ROOT / 'tools/case_catalog.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CreativeExampleTests(unittest.TestCase):
    def test_default_returns_approved_before_and_after_text_without_openings(self):
        body = catalog.examples()
        expected = '\n\n'.join((catalog.ROOT / catalog.EXAMPLE_FILES[part]).read_text().rstrip()
                               for part in ('before', 'after')) + '\n'
        self.assertEqual(body, expected)
        self.assertNotIn('B002-001-', body)
        self.assertEqual(body.count('### B002-002-'), 60)
        self.assertEqual(body.count('### B002-003-'), 50)

    def test_opening_is_separate_and_contains_all_60_approved_examples(self):
        body = catalog.examples(('opening',))
        self.assertEqual(body, (catalog.ROOT / catalog.EXAMPLE_FILES['opening']).read_text().rstrip() + '\n')
        self.assertEqual(body.count('### B002-001-'), 60)
        self.assertNotIn('B002-002-', body)
        self.assertNotIn('B002-003-', body)

    def test_only_requested_parts_are_read_and_no_other_sources_are_mixed_in(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / catalog.EXAMPLE_FILES['after']
            path.parent.mkdir(parents=True)
            path.write_text('已审核的妆后创作版本。\n')
            (path.parent / 'source-excerpt.md').write_text('不可收录的来源短摘与开头。')
            self.assertEqual(catalog.examples(('after',), root), path.read_text())

    def test_missing_or_empty_examples_are_reported_instead_of_silently_omitted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError):
                catalog.examples(('before',), root)
            path = root / catalog.EXAMPLE_FILES['before']
            path.parent.mkdir(parents=True)
            path.write_text('  ')
            with self.assertRaises(ValueError):
                catalog.examples(('before',), root)

    def test_cli_provides_text_and_rejects_unknown_parts(self):
        result = subprocess.run([sys.executable, str(ROOT / 'tools/case_catalog.py'),
                                 'examples', '--part', 'opening'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, catalog.examples(('opening',)))
        invalid = subprocess.run([sys.executable, str(ROOT / 'tools/case_catalog.py'),
                                  'examples', '--part', 'source-openings'], capture_output=True)
        self.assertNotEqual(invalid.returncode, 0)


if __name__ == '__main__':
    unittest.main()
