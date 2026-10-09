import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from swe_pruner.conversation_context import conversation_hint, is_follow_up, next_user_turns, bound_user_turns, HINT_LIMIT
from swe_pruner.goal_compiler import GoalCompiler
from swe_pruner.repository.repository_index import RepositoryIndex
from swe_pruner.repository.repository_index import RepositoryIndexCache
from swe_pruner.retrieval.context_comparison import ComparisonTooLarge, build_comparison
from swe_pruner.retrieval.workspace_context import WorkspaceContextBuilder
from test_antigravity import ReferenceModel


class DemonstrationFixtureTests(unittest.TestCase):
    def setUp(self):
        self.demo = Path(__file__).resolve().parents[3] / "demonstration"
        self.cases = json.loads((self.demo / "cases.json").read_text(encoding="utf-8"))["cases"]
        self.root = self.demo / self.cases[0]["project"]

    def test_one_runnable_project_and_valid_presentation_scopes(self):
        self.assertEqual(len(self.cases), 1)
        self.assertEqual([path.parent.name for path in self.demo.glob("*/app.py")], ["tokenwise_demo"])
        for key in ("selection_file", "mixed_selection_file", "class_selection_file"):
            path = (self.root / self.cases[0][key]).resolve()
            self.assertTrue(path.is_relative_to(self.root.resolve()))
            self.assertTrue(path.is_file())

    def test_one_project_covers_unpruned_baselines_and_budgeted_retrieval(self):
        case = self.cases[0]
        index = RepositoryIndex(str(self.root))
        index.build_index()
        self.assertEqual(len(index.index), 11)
        query = case["query"]
        model = ReferenceModel()
        goal = GoalCompiler(None).deterministic_fallback(query, None, [])
        result = WorkspaceContextBuilder().build(index, goal, model, None, query, .45, 8192, 8)
        comparison = build_comparison(index, model, result, case["selection_file"], None)
        all_code, selected, automatic = comparison["methods"]
        self.assertEqual(len(all_code["files"]), 11)
        for marker in case["evidence_markers"]:
            self.assertIn(marker, all_code["context"])
        self.assertNotIn("LOCKOUT_THRESHOLD = 3", selected["context"])
        self.assertEqual(automatic["context"], result["unified_prompt"])
        self.assertLessEqual(result["pruned_tokens"], 8192)


class ConversationTests(unittest.TestCase):
    def test_current_topic_and_recent_constraints_are_bounded_and_reset_on_new_topic(self):
        state = {"topic_query": "Explain account lockout"}
        for query in ("What about its expiry?", "What about its reset?", "Which tests cover that behavior?"):
            state = {"user_turns": next_user_turns(query, state, True)}
        self.assertEqual(state["user_turns"], ["Explain account lockout", "What about its expiry?", "What about its reset?", "Which tests cover that behavior?"])
        self.assertEqual(next_user_turns("Explain shipping", state, True), ["Explain shipping"])
        self.assertEqual(next_user_turns("What about its tests?", state, False), [])
        self.assertEqual(next_user_turns("What about its tests?", {}, True), [])
        self.assertLessEqual(len("\n\n".join(bound_user_turns(["x" * 5000] * 10))), HINT_LIMIT)

    def test_prune_response_exposes_actual_mean_line_scores(self):
        from types import SimpleNamespace
        from swe_pruner.prune_wrapper import SwePrunerForCodePruning, PruneRequest
        from test_antigravity import CharacterTokenizer
        code = "noise=1\nuseful=2"
        scores = [(character, .2 if position < 8 else .9) for position, character in enumerate(code)]
        offsets = [(position, position + 1) for position in range(len(code))]
        model = SimpleNamespace(tokenizer=CharacterTokenizer(), instruction="Task relevance",
                                _process_single_chunk=lambda *args, **kwargs: (.8, scores, offsets))
        result = SwePrunerForCodePruning.prune(model, PruneRequest(query="Explain useful", code=code, threshold=.5))
        self.assertAlmostEqual(result.line_scores[1], .2)
        self.assertAlmostEqual(result.line_scores[2], .9)
        self.assertEqual(result.kept_frags, [2])

    def test_only_recognized_followups_use_a_bounded_scoped_user_topic(self):
        for query in ("Which tests cover that behavior?", "What about its expiry tests?", "Why does it fail?"):
            self.assertTrue(is_follow_up(query))
            self.assertEqual(len(conversation_hint(query, {"topic_query": "x" * 3000}, True)), 2000)
            self.assertEqual(conversation_hint(query, {"topic_query": "Auth lockout"}, False), "")
        for query in ("Explain session expiry", "What about inventory reservations?", "And explain coupons"):
            self.assertFalse(is_follow_up(query))
            self.assertEqual(conversation_hint(query, {"topic_query": "Auth lockout"}, True), "")
        self.assertEqual(conversation_hint("Why does it fail?", {"topic_query": 12}, True), "")

    def test_new_chat_asks_for_clarification_instead_of_guessing_topic(self):
        compiler = GoalCompiler(None)
        blank = asyncio.run(compiler.compile("Which tests cover that behavior?", "", None, None, []))
        self.assertTrue(blank.clarification_required)
        scoped = asyncio.run(compiler.compile("Which tests cover that behavior?", "", None, None, [], context_hint="Explain account lockout"))
        self.assertFalse(scoped.clarification_required)
        self.assertIn("account lockout", scoped.objective)


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        for name, source in {"auth.py": "def authenticate():\n    return 'account lockout'\n",
                             "settings.py": "LOCKOUT_THRESHOLD = 3\n",
                             "test_auth.py": "def test_lockout():\n    assert True\n",
                             "shipping.py": "def deliver():\n    return 'delivery'\n"}.items():
            (self.root / name).write_text(source, encoding="utf-8")
        self.index = RepositoryIndex(str(self.root))
        self.index.build_index()
        self.model = ReferenceModel()
        query = "Explain account lockout"
        goal = GoalCompiler(None).deterministic_fallback(query, None, [])
        self.automatic = WorkspaceContextBuilder().build(self.index, goal, self.model, None, query, .45, 4096, 8)

    def test_packets_use_same_snapshot_and_exact_tokenizer_counts(self):
        result = build_comparison(self.index, self.model, self.automatic, "auth.py", None)
        all_code, selected, automatic = result["methods"]
        self.assertEqual(all_code["files"], sorted(self.index.index))
        self.assertIn("LOCKOUT_THRESHOLD = 3", all_code["context"])
        self.assertIn("def test_lockout", all_code["context"])
        self.assertNotIn("LOCKOUT_THRESHOLD", selected["context"])
        self.assertNotIn("def test_lockout", selected["context"])
        self.assertEqual(automatic["context"], self.automatic["unified_prompt"])
        for method in result["methods"]:
            self.assertEqual(method["input_tokens"], len(self.model.tokenizer.encode(method["context"])))

    def test_excerpt_normalizes_windows_lines_and_is_not_neurally_pruned(self):
        result = build_comparison(self.index, self.model, self.automatic, "auth.py", "def authenticate():\r\n    return 'account lockout'\r\n")
        self.assertEqual(result["selection_scope"], "selected excerpt")
        self.assertNotIn("\r", result["methods"][1]["context"])

    def test_automatic_comparison_needs_no_selection_and_reuses_prepared_context(self):
        calls = self.model.calls
        result = build_comparison(self.index, self.model, {**self.automatic, "comparison_query": "Explain account lockout"})
        self.assertEqual([item["id"] for item in result["methods"]], ["all_python", "tokenwise"])
        self.assertEqual(result["measurement_scope"], "prepared_packets")
        self.assertEqual(result["methods"][1]["context"], self.automatic["unified_prompt"])
        self.assertEqual(self.model.calls, calls)
        for method in result["methods"]:
            self.assertEqual(method["prompt_tokens"], len(self.model.tokenizer.encode(result["query"] + "\n\n" + method["context"])))
        self.assertTrue(any("hypothetical" in note for note in result["notes"]))

    def test_wrong_packet_counts_and_outside_files_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "token count"):
            build_comparison(self.index, self.model, {**self.automatic, "pruned_tokens": 1})
        with self.assertRaisesRegex(ValueError, "outside"):
            build_comparison(self.index, self.model, {**self.automatic, "files": [{"file_path": "../outside.md"}]})

    def test_invalid_selection_and_changed_snapshot_fail_closed(self):
        for filename, text in (("../outside.py", None), ("README.md", None), ("auth.py", "invented source"), ("auth.py", " ")):
            with self.assertRaises(ValueError):
                build_comparison(self.index, self.model, self.automatic, filename, text)
        with self.assertRaisesRegex(ValueError, "changed"):
            build_comparison(self.index, self.model, {**self.automatic, "repository_fingerprint": "old"}, "auth.py", None)

    def test_baseline_size_guard_does_not_truncate_all_code(self):
        with patch("swe_pruner.retrieval.context_comparison.MAX_BASELINE_FILES", 1):
            with self.assertRaises(ComparisonTooLarge):
                build_comparison(self.index, self.model, self.automatic, "auth.py", None)

    def test_different_conversation_topics_do_not_share_answer_cache(self):
        builder = WorkspaceContextBuilder()
        compiler = GoalCompiler(None)
        query = "Which tests cover that behavior?"
        for hint in ("Explain account lockout", "Explain delivery"):
            goal = asyncio.run(compiler.compile(query, "", None, None, [], context_hint=hint))
            first = builder.build(self.index, goal, self.model, None, query, .45, 4096, 8, hint)
            self.assertFalse(first["context_cache_hit"])
            self.assertTrue(first["context_hint_used"])
            second = builder.build(self.index, goal, self.model, None, query, .45, 4096, 8, hint)
            self.assertTrue(second["context_cache_hit"])

    def test_small_lexically_matched_implementation_keeps_body_and_configuration(self):
        for name, source in {
            "test_checkout.py": "from orders import checkout\nfrom coupons import coupon\nfrom pricing import tax\ndef test_coupon_checkout(): assert checkout()\n",
            "orders.py": "from coupons import coupon\nfrom pricing import tax\ndef checkout(): return coupon() + tax()\n",
            "coupons.py": "def coupon():\n    return 0 if 'expired' else 10\n",
            "pricing.py": "from config import TAX_PERCENT\ndef tax(): return TAX_PERCENT\n",
            "config.py": "TAX_PERCENT = 15\n",
        }.items():
            (self.root / name).write_text(source, encoding="utf-8")
        self.index.build_index()
        query = "Explain coupon checkout expiry pricing tax tests"
        goal = GoalCompiler(None).deterministic_fallback(query, None, [])
        result = WorkspaceContextBuilder().build(self.index, goal, self.model, None, query, .45, 4096, 6)
        self.assertIn("TAX_PERCENT = 15", result["unified_prompt"])
        self.assertIn("return 0 if 'expired' else 10", result["unified_prompt"])
        self.assertLessEqual(self.model.calls, 6)  # setUp already used at most three passes.

    def test_http_comparison_has_no_editor_or_history_bias_and_validates_before_inference(self):
        from fastapi.testclient import TestClient
        from swe_pruner import online_serving as serving
        with patch.object(serving, "repository_cache", RepositoryIndexCache()), \
                patch.object(serving, "workspace_builder", WorkspaceContextBuilder()), \
                patch.object(serving, "check_model_path", return_value=False), \
                patch.object(serving, "model", None), TestClient(serving.app) as client:
            serving.model = ReferenceModel()
            payload = {"workspace_root": str(self.root), "query": "Explain account lockout", "token_budget": 4096,
                       "selection_file": "shipping.py", "active_file": str(self.root / "shipping.py"),
                       "selected_code": "delivery", "current_symbol": "deliver", "diagnostics": ["shipping error"],
                       "context_hint": "Other conversation topic"}
            result = client.post("/compare-workspace", json=payload)
            self.assertEqual(result.status_code, 200, result.text)
            self.assertNotEqual(result.json()["selected_file"], "shipping.py")
            self.assertEqual(result.json()["comparison"]["methods"][1]["files"], ["shipping.py"])
            self.assertFalse(result.json()["context_hint_used"])
            with patch.object(serving, "prune_workspace", side_effect=AssertionError("Invalid baseline ran retrieval")):
                self.assertEqual(client.post("/compare-workspace", json={**payload, "selection_file": "../outside.py"}).status_code, 400)
                with patch("swe_pruner.retrieval.context_comparison.MAX_BASELINE_FILES", 1):
                    self.assertEqual(client.post("/compare-workspace", json=payload).status_code, 413)

    def test_http_prepared_comparison_has_no_inference_and_reconciles_missed_file_changes(self):
        from fastapi.testclient import TestClient
        from swe_pruner import online_serving as serving
        cache = RepositoryIndexCache()
        cache.synchronize(str(self.root), "live-watcher", "start")
        with patch.object(serving, "repository_cache", cache), \
                patch.object(serving, "workspace_builder", WorkspaceContextBuilder()), \
                patch.object(serving, "check_model_path", return_value=False), \
                patch.object(serving, "model", None), TestClient(serving.app) as client:
            serving.model = ReferenceModel()
            original = client.post("/prune-workspace", json={"workspace_root": str(self.root), "query": "Explain account lockout"}).json()
            calls = serving.model.calls
            payload = {"workspace_root": str(self.root), "query": "Explain account lockout", "prepared_context": original}
            response = client.post("/compare-prepared-workspace", json=payload)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["methods"][1]["context"], original["unified_prompt"])
            self.assertEqual(serving.model.calls, calls)
            with patch("swe_pruner.retrieval.context_comparison.MAX_BASELINE_FILES", 1):
                self.assertEqual(client.post("/compare-prepared-workspace", json=payload).status_code, 413)
            self.assertEqual(client.post("/compare-prepared-workspace", json={**payload, "query": "  "}).status_code, 400)
            (self.root / "settings.py").write_text("LOCKOUT_THRESHOLD = 4\n", encoding="utf-8")
            self.assertEqual(client.post("/compare-prepared-workspace", json=payload).status_code, 409)
            self.assertEqual(serving.model.calls, calls)


if __name__ == "__main__":
    unittest.main()
