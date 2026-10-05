import ast
import asyncio
import tempfile
import unittest
from pathlib import Path

from swe_pruner.goal_compiler import GoalCompiler
from swe_pruner.query_focus import query_focus
from swe_pruner.repository.repository_index import RepositoryIndex
from swe_pruner.retrieval.context_builder import ContextBuilder
from swe_pruner.retrieval.lexical_retriever import LexicalRetriever
from swe_pruner.retrieval.source_focus import focus_sources
from swe_pruner.retrieval.workspace_context import WorkspaceContextBuilder
from test_antigravity import ReferenceModel


class QueryFocusTests(unittest.TestCase):
    def test_explicit_contrasts_keep_the_positive_task(self):
        for marker in (", not", " but not", " rather than", " excluding"):
            focus = query_focus("Explain session expiry" + marker + " invoice pricing. Do not modify files.")
            self.assertEqual(focus.excluded_topics, ("invoice pricing",))
            self.assertIn("Explain session expiry", focus.positive_query)
            self.assertIn("Do not modify files", focus.positive_query)
            self.assertNotIn("invoice", focus.positive_query)

    def test_ordinary_negation_and_operational_instructions_are_not_exclusions(self):
        for query in ("Explain sessions that are not revoked", "Why does login not work?",
                      "Explain session expiry, not only revocation", "Explain sessions, but not when they are revoked",
                      "Explain session expiry, but not modify any files", "Do not modify files"):
            self.assertEqual(query_focus(query).excluded_topics, (), query)

    def test_goals_and_lexical_search_do_not_promote_the_excluded_topic(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "sessions.py").write_text("def session_expiry(): return 300\n", encoding="utf-8")
        (root / "invoices.py").write_text("def invoice_pricing(): return 100\n", encoding="utf-8")
        index = RepositoryIndex(str(root))
        index.build_index()
        query = "Explain session expiry, not invoice pricing"
        goal = asyncio.run(GoalCompiler(None).compile(query, "", None, None, []))
        self.assertEqual(goal.excluded_topics, ["invoice pricing"])
        self.assertNotIn("invoice", goal.identifiers)
        self.assertNotIn("pricing", goal.identifiers)
        self.assertNotIn("not", goal.identifiers)
        self.assertEqual([path for path, _ in LexicalRetriever(index).search_query(query)], ["sessions.py"])


class SourceFocusTests(unittest.TestCase):
    def view(self, sources, query="Explain session expiry and revocation, not invoice pricing"):
        return focus_sources({path: {"content": source} for path, source in sources.items()}, query_focus(query))

    def test_mixed_demo_omits_invoice_units_not_session_negation_or_decorators(self):
        root = Path(__file__).resolve().parents[3] / "demonstration/tokenwise_demo"
        sources = {str(path.relative_to(root)).replace("\\", "/"): path.read_text(encoding="utf-8")
                   for path in root.rglob("*.py")}
        views, warnings = self.view(sources)
        self.assertEqual(warnings, [])
        combined = "\n".join(item["content"] for item in views.values())
        self.assertNotIn("invoice_total", combined)
        self.assertNotIn("test_invalid_invoice", combined)
        self.assertIn("@dataclass\nclass Session", combined)
        self.assertIn("not session.revoked", combined)
        self.assertIn("test_session_expiry_boundary", combined)
        self.assertIn("test_revocation", combined)
        for item in views.values():
            ast.parse(item["content"])
        self.assertIn("invoice_total", sources["workflows.py"])

    def test_dependency_used_by_requested_topic_is_not_discarded(self):
        views, warnings = self.view({
            "session.py": "from invoices import invoice_cutoff\ndef session_expiry(): return invoice_cutoff()\n",
            "invoices.py": "def invoice_cutoff(): return 300\ndef invoice_pricing(): return 100\n",
        })
        self.assertIn("def invoice_cutoff", views["invoices.py"]["content"])
        self.assertNotIn("invoice_pricing", views["invoices.py"]["content"])
        self.assertTrue(any("invoice_cutoff" in warning for warning in warnings))

    def test_imported_aliases_and_module_configuration_protect_required_helpers(self):
        for use in ("def session_expiry(): return cutoff()\n", "SESSION_EXPIRY = cutoff()\n"):
            views, warnings = self.view({
                "session.py": "from invoices import invoice_cutoff as cutoff\n" + use,
                "invoices.py": "def invoice_cutoff(): return 300\ndef invoice_pricing(): return 100\n",
            })
            self.assertIn("def invoice_cutoff", views["invoices.py"]["content"])
            self.assertNotIn("invoice_pricing", views["invoices.py"]["content"])
            self.assertIn("invoice_cutoff as cutoff", views["session.py"]["content"])
            self.assertTrue(warnings)

    def test_shared_line_statements_are_not_removed_together(self):
        source = ("def session_expiry():\n    print(invoice_total()); return session.expires_at\n"
                  "def invoice_total(): return 100\n")
        views, _ = self.view({"mixed.py": source})
        self.assertIn("return session.expires_at", views["mixed.py"]["content"])
        self.assertIn("def invoice_total", views["mixed.py"]["content"])
        ast.parse(views["mixed.py"]["content"])

    def test_async_decorated_units_and_import_aliases_are_removed_together(self):
        source = ("from other import invoice_total as price, issue_session\n"
                  "@decorator\nasync def invoice_pricing():\n    return price()\n"
                  "def session_expiry():\n    return issue_session()\n")
        views, _ = self.view({"mixed.py": source})
        self.assertNotIn("price", views["mixed.py"]["content"])
        self.assertNotIn("@decorator", views["mixed.py"]["content"])
        self.assertIn("issue_session", views["mixed.py"]["content"])
        ast.parse(views["mixed.py"]["content"])

    def test_required_return_conditions_and_mutating_calls_are_not_line_filtered(self):
        source = ("def invoice_total(): return 1\n"
                  "def session_expiry(session):\n    invoice_total()\n    return not session.revoked\n")
        views, warnings = self.view({"mixed.py": source})
        self.assertIn("def invoice_total", views["mixed.py"]["content"])
        self.assertIn("return not session.revoked", views["mixed.py"]["content"])
        self.assertTrue(warnings)

    def test_entirely_excluded_files_are_omitted_and_invalid_python_is_retained(self):
        views, _ = self.view({"invoices.py": "import math\ndef invoice_pricing(): return 100\n",
                              "broken.py": "def session_expiry(:\n",
                              "sessions.py": "def session_expiry(): return 300\n"})
        self.assertNotIn("invoices.py", views)
        self.assertEqual(views["broken.py"]["content"], "def session_expiry(:\n")

    def test_query_specific_views_and_cache_do_not_mutate_originals_or_other_queries(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        original = "def session_expiry(): return 300\ndef invoice_pricing(): return 100\n"
        (root / "mixed.py").write_text(original, encoding="utf-8")
        index = RepositoryIndex(str(root))
        index.build_index()
        builder, model = WorkspaceContextBuilder(), ReferenceModel()
        compiler = GoalCompiler(None)

        def build(query):
            return builder.build(index, compiler.deterministic_fallback(query, None, []), model, None, query, .45, 4096, 8)

        excluded = build("Explain session expiry, not invoice pricing")
        self.assertNotIn("def invoice_pricing", excluded["unified_prompt"])
        self.assertEqual(excluded["original_tokens"], len(original))
        self.assertLess(excluded["retained_source_tokens"], excluded["original_tokens"])
        self.assertIn("def invoice_pricing", build("Explain invoice pricing")["unified_prompt"])
        self.assertTrue(build("Explain session expiry, not invoice pricing")["context_cache_hit"])
        self.assertEqual(index.index["mixed.py"]["content"], original)
        self.assertEqual((root / "mixed.py").read_text(encoding="utf-8"), original)
        (root / "mixed.py").write_text(original.replace("300", "600"), encoding="utf-8")
        index.build_index()
        fresh = build("Explain session expiry, not invoice pricing")
        self.assertFalse(fresh["context_cache_hit"])
        self.assertIn("600", fresh["unified_prompt"])
        self.assertEqual(fresh["pruned_tokens"], ContextBuilder._count(fresh["unified_prompt"], model.tokenizer))


if __name__ == "__main__":
    unittest.main()
