"""Corpus preparation checks, separate from extension/backend release tests."""
import ast
import importlib.util
import io
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('prepare_corpus', ROOT / 'scripts/prepare_comparative_repositories.py')
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


def archive(entries):
    stream = io.BytesIO()
    with ZipFile(stream, 'w') as zipped:
        for name, content in entries:
            zipped.writestr(name, content)
    return stream.getvalue()


class PreparationTests(unittest.TestCase):
    def test_source_metadata_docs_and_license_are_preserved(self):
        data = archive([('project/src/api.py', 'def run(): pass'),
                        ('project/docs/guide.rst', 'documentation'),
                        ('project/LICENCE', 'license'), ('project/pyproject.toml', '[project]')])
        files, skipped = prepare.archive_files(data)
        self.assertEqual(len(files), 4)
        self.assertEqual(skipped, [])
        self.assertIn(Path('docs/guide.rst'), dict(files))

    def test_path_traversal_and_windows_paths_are_rejected(self):
        for name in ['project/../../escape.py', '/absolute/file.py', 'project/C:/file.py', 'project\\escape.py']:
            member = ZipInfo('placeholder')
            member.filename = name
            with self.subTest(name=name), self.assertRaises(ValueError):
                prepare.archive_files(archive([(member, 'unsafe')]))

    def test_multiple_archive_roots_are_rejected(self):
        with self.assertRaises(ValueError):
            prepare.archive_files(archive([('first/a.py', ''), ('second/b.py', '')]))

    def test_case_collisions_are_rejected_on_windows(self):
        with self.assertRaises(ValueError):
            prepare.archive_files(archive([('project/API.py', ''), ('project/api.py', '')]))

    def test_symlink_members_are_not_materialized(self):
        link = ZipInfo('project/link.py')
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        files, skipped = prepare.archive_files(archive([('project/api.py', ''), (link, '../elsewhere')]))
        self.assertEqual([str(path) for path, _ in files], ['api.py'])
        self.assertEqual(skipped, ['link.py'])

    def test_retry_verifies_files_and_restores_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = [(Path('src/a.py'), b'first'), (Path('b.py'), b'second')]
            self.assertEqual(prepare.prepare_files(root, files), (2, 0))
            self.assertEqual(prepare.prepare_files(root, files), (0, 2))
            (root / 'b.py').unlink()
            self.assertEqual(prepare.prepare_files(root, files), (1, 1))

    def test_changed_source_is_preserved_before_any_new_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'changed.py').write_bytes(b'user content')
            with self.assertRaises(ValueError):
                prepare.prepare_files(root, [(Path('new.py'), b'new'), (Path('changed.py'), b'upstream')])
            self.assertFalse((root / 'new.py').exists())
            self.assertEqual((root / 'changed.py').read_bytes(), b'user content')

    def test_target_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            prepare.checked_target(Path(directory), Path('../outside.py'))

    def test_corrupt_archive_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(prepare, 'ARCHIVES', Path(directory)):
            commit = 'a' * 40
            (Path(directory) / f'owner--project-{commit}.zip').write_bytes(b'changed')
            with self.assertRaises(ValueError):
                prepare.load_archive('owner/project', {'commit': commit, 'archive_sha256': '0' * 64}, False)

    def test_symbols_are_checked_without_executing_source(self):
        source = 'raise RuntimeError("must not execute")\nclass API:\n    def run(self): pass\n'
        self.assertIn('API.run', set(prepare.symbol_names(ast.parse(source))))


if __name__ == '__main__':
    unittest.main()
