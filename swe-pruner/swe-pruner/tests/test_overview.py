import asyncio
import tempfile
import unittest
from pathlib import Path

from swe_pruner.goal_compiler import GoalCompiler, is_repository_overview
from swe_pruner.repository.repository_index import RepositoryIndex
from swe_pruner.retrieval.workspace_context import WorkspaceContextBuilder
from test_antigravity import ReferenceModel


class OverviewTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.builder = WorkspaceContextBuilder()
        self.model = ReferenceModel()

    def write(self, name, content):
        filename = self.root / name
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(content, encoding="utf-8")

    def build(self, query="GIVE ME THE FULL OVERVIEW OF MY PROJECT", budget=4096, candidates=6):
        index = RepositoryIndex(str(self.root))
        index.build_index()
        goal = GoalCompiler(None).deterministic_fallback(query, None, [])
        return self.builder.build(index, goal, self.model, None, query, .45, budget, candidates)

    def test_overview_intent_is_case_insensitive_and_not_fake_identifiers(self):
        for query in ("GIVE ME THE FULL OVERVIEW OF MY PROJECT", "Explain this codebase",
                      "How does the repository work?", "project architecture"):
            self.assertTrue(is_repository_overview(query))
            goal = asyncio.run(GoalCompiler(None).compile(query, "", None, None, []))
            self.assertEqual(goal.task_type, "repository_overview")
            self.assertEqual(goal.identifiers, [])
        self.assertFalse(is_repository_overview("Explain account lockout and its related tests"))
        self.assertFalse(is_repository_overview("Give an overview of AuthService login errors"))
        self.assertFalse(is_repository_overview("Explain my project's authentication flow"))
        self.assertFalse(is_repository_overview("Describe the project authentication model"))

    def test_overview_includes_disconnected_implementation_tests_and_documents(self):
        self.write("src/demo1/__init__.py", '__version__ = "0.1.0"\n')
        self.write("src/demo1/cli.py", "def main():\n    return 'run application'\n")
        self.write("src/demo1/services/auth.py", "class AuthService:\n    def login(self): return True\n")
        self.write("src/demo1/models/user.py", "class User:\n    active = True\n")
        self.write("tests/test_auth.py", "def test_login():\n    assert True\n")
        self.write("README.md", "# Demo1\nA login demo with a CLI and account models.\n")
        self.write("pyproject.toml", '[project]\nname = "demo1"\n[project.scripts]\ndemo1 = "demo1.cli:main"\n')
        result = self.build()
        names = {file["file_path"] for file in result["files"]}
        self.assertEqual(names, {"README.md", "pyproject.toml", "src/demo1/cli.py",
                                 "src/demo1/services/auth.py", "src/demo1/models/user.py", "tests/test_auth.py"})
        self.assertEqual(result["context_mode"], "repository_overview")
        self.assertEqual(result["indexed_files"], 5)
        self.assertEqual(self.model.calls, 0)
        self.assertIn("read originals", result["unified_prompt"].lower())
        self.assertIn("Bounded overview", " ".join(result["warnings"]))

    def test_initializer_only_is_reported_as_sparse_and_has_honest_token_metrics(self):
        self.write("src/demo1/__init__.py", '__version__ = "0.1.0"\n')
        result = self.build()
        self.assertEqual(result["retained_source_tokens"], result["original_tokens"])
        self.assertEqual(result["raw_context_tokens"], result["pruned_tokens"])
        self.assertGreater(result["context_overhead_tokens"], 0)
        self.assertIn("Only Python package initializers", " ".join(result["warnings"]))
        self.assertEqual(self.model.calls, 0)

    def test_large_readme_does_not_crowd_out_other_components(self):
        self.write("README.md", "# Demo1\n" + "Overview description. " * 6000)
        self.write("pyproject.toml", '[project]\nname = "demo1"\n')
        self.write("main.py", "def main(): return True\n")
        self.write("services/auth.py", "class AuthService: pass\n")
        self.write("models/user.py", "class User: pass\n")
        self.write("tests/test_auth.py", "def test_login(): pass\n")
        result = self.build(budget=2048)
        self.assertEqual(len(result["files"]), 6)
        self.assertLessEqual(result["pruned_tokens"], 2048)
        self.assertIn("tests/test_auth.py", result["unified_prompt"])
        self.assertTrue(any("65536" in warning for warning in result["warnings"]))

    def test_initializer_with_real_implementation_is_not_called_a_metadata_scaffold(self):
        self.write("src/demo1/__init__.py", "def authenticate(password):\n    return password == 'valid'\n")
        result = self.build()
        self.assertFalse(any("scaffold" in warning for warning in result["warnings"]))
        self.assertIn("def authenticate", result["unified_prompt"])

    def test_overview_respects_small_budgets_and_candidate_limits(self):
        self.write("README.md", "# Overview\n" + "documentation " * 100)
        self.write("main.py", "def main(): return True\n")
        self.write("tests/test_main.py", "def test_main(): pass\n")
        for budget in (256, 512, 2048):
            for candidates in (1, 2, 3):
                result = self.build(budget=budget, candidates=candidates)
                self.assertTrue(result["files"])
                self.assertLessEqual(len(result["files"]), candidates)
                self.assertLessEqual(result["pruned_tokens"], budget)

    def test_readme_edit_addition_and_removal_invalidate_exact_overview_cache(self):
        self.write("main.py", "def main(): return True\n")
        first = self.build()
        self.assertFalse(first["context_cache_hit"])
        self.assertTrue(self.build()["context_cache_hit"])
        self.write("README.md", "# Purpose\nCURRENT_PURPOSE\n")
        added = self.build()
        self.assertFalse(added["context_cache_hit"])
        self.assertIn("CURRENT_PURPOSE", added["unified_prompt"])
        self.write("README.md", "# Purpose\nUPDATED_PURPOSE\n")
        edited = self.build()
        self.assertFalse(edited["context_cache_hit"])
        self.assertIn("UPDATED_PURPOSE", edited["unified_prompt"])
        (self.root / "README.md").unlink()
        self.assertNotIn("UPDATED_PURPOSE", self.build()["unified_prompt"])

    def test_readme_nested_fences_do_not_break_the_outer_context_block(self):
        self.write("main.py", "def main(): pass\n")
        self.write("README.md", "# Demo1\n```python\nprint('example')\n```\n")
        result = self.build()
        self.assertIn("````markdown", result["unified_prompt"])
        self.assertEqual(result["raw_context_tokens"], result["pruned_tokens"])

    def test_document_line_endings_are_normalized_for_windows_tool_output(self):
        self.write("main.py", "def main(): pass\n")
        (self.root / "README.md").write_bytes(b"# Demo1\r\nCurrent project purpose.\r\n")
        result = self.build()
        self.assertNotIn("\r", result["unified_prompt"])
        self.assertIn("# Demo1\nCurrent project purpose.", result["unified_prompt"])
        self.assertEqual(result["raw_context_tokens"], result["pruned_tokens"])

    def test_focused_fallback_prefers_nested_entry_point_over_initializer(self):
        self.write("src/demo1/__init__.py", '__version__ = "0.1.0"\n')
        self.write("src/demo1/cli.py", "def main(): return True\n")
        result = self.build(query="Investigate missing startup behavior")
        self.assertEqual(result["selected_file"], "src/demo1/cli.py")
        self.assertEqual(result["context_mode"], "focused")
        self.assertGreater(self.model.calls, 0)


if __name__ == "__main__":
    unittest.main()
