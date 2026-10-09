"""Tests of the research harness, separate from TokenWise's release test suites."""

import ast
import importlib.util
import io
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("study_protocol", ROOT / "scripts/run_comparative_study.py")
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


class ProtocolTests(unittest.TestCase):
    oracle = [{"kind": "implementation", "file": "api.py", "symbol": "API.run",
               "definition": "def run(", "anchor": "return self.value"}]

    def packet(self, name="api.py", code="def run(self):\n    return self.value\n"):
        return f"### {name}\n# Relation: baseline source\n# Tier: 1\n```python\n{code}```\n"

    def test_source_definition_and_body_are_required(self):
        self.assertEqual(study.score_evidence(self.packet(), self.oracle)["retained"], 1)
        self.assertEqual(study.score_evidence(self.packet(code="def run(self):\n    ...\n"), self.oracle)["retained"], 0)

    def test_preamble_and_history_are_not_source_evidence(self):
        self.assertEqual(study.score_evidence("def run(self): return self.value", self.oracle)["retained"], 0)

    def test_same_symbol_in_another_file_is_not_evidence(self):
        self.assertEqual(study.score_evidence(self.packet("other.py"), self.oracle)["retained"], 0)

    def test_whitespace_differences_do_not_change_evidence(self):
        self.assertEqual(study.score_evidence(self.packet(code="def run(self):\r\n\treturn  self.value\r\n"), self.oracle)["retained"], 1)

    def test_markdown_heading_inside_source_does_not_split_block(self):
        code = '"""Documentation\n### embedded heading\n"""\ndef run(self):\n    return self.value\n'
        self.assertEqual(study.score_evidence(self.packet(code=code), self.oracle)["retained"], 1)

    def test_longer_fences_can_contain_shorter_fences(self):
        packet = '### api.py\n# Relation: baseline source\n# Tier: 1\n````python\n"""\n```\n"""\ndef run(self):\n    return self.value\n````\n'
        self.assertEqual(study.score_evidence(packet, self.oracle)["retained"], 1)

    def test_qualified_class_methods_are_discovered_without_imports(self):
        names = dict(study.definitions(ast.parse("class API:\n    def run(self):\n        return 1\n")))
        self.assertIn("API.run", names)

    def test_last_definition_is_implementation_after_overloads(self):
        names = dict(study.definitions(ast.parse("def run(x): ...\ndef run(x):\n    return x + 1\n")))
        self.assertIsInstance(names["run"].body[0], ast.Return)

    def test_unsafe_archive_paths_are_rejected(self):
        content = io.BytesIO()
        with zipfile.ZipFile(content, "w") as archive:
            archive.writestr("project/../../escape.py", "print('not executed')")
        with self.assertRaisesRegex(ValueError, "Unsafe archive"):
            study.extract_snapshot(content.getvalue(), study.SCRATCH / "unsafe-fixture")

    def test_destinations_outside_scratch_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "scratch"):
            study.extract_snapshot(b"", ROOT / "not-study-scratch")


if __name__ == "__main__":
    unittest.main()
