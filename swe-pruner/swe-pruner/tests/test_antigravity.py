import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from swe_pruner.antigravity_hook import MARKER, latest_prompt, run_hook
from swe_pruner.antigravity_context import run_context
from swe_pruner.repository.repository_index import RepositoryIndex, RepositoryIndexCache
from swe_pruner.retrieval.context_builder import ContextBuilder
from swe_pruner.retrieval.lexical_retriever import LexicalRetriever


class CharacterTokenizer:
    def encode(self, text, **kwargs):
        return list(text)

    def decode(self, tokens, **kwargs):
        return "".join(tokens)

    def __call__(self, text, **kwargs):
        return {"input_ids": self.encode(text)}


class ReferenceModel:
    tokenizer = CharacterTokenizer()

    def __init__(self):
        self.calls = 0

    def prune(self, request):
        self.calls += 1
        from types import SimpleNamespace
        return SimpleNamespace(pruned_code=request.code, origin_token_cnt=len(request.code), score=0.7)


class AntigravityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.workspace = Path(self.directory.name).resolve()
        self.transcript = self.workspace / "transcript.jsonl"
        self.payload = {
            "conversationId": "test-conversation", "workspacePaths": [str(self.workspace)],
            "transcriptPath": str(self.transcript), "invocationNum": 0,
        }
        self.write_prompt("Explain payment retries", 1)

    def tearDown(self):
        self.directory.cleanup()

    def write_prompt(self, query, step):
        record = {"type": "USER_INPUT", "source": "USER_EXPLICIT", "step_index": step, "content": query}
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record) + "\n")

    def test_latest_prompt_ignores_model_tools_and_injected_context(self):
        self.write_prompt(MARKER + "\nInjected code", 2)
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"type": "PLANNER_RESPONSE", "source": "MODEL", "content": "Fake user task"}) + "\n")
            stream.write('{"type": "unfinished')
        self.assertEqual(latest_prompt(self.payload)[0], "Explain payment retries")

    def test_reverse_reader_crosses_blocks_and_handles_unicode(self):
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"type": "VIEW_FILE", "source": "MODEL", "content": "x" * 150000}) + "\n")
        self.assertEqual(latest_prompt(self.payload)[0], "Explain payment retries")
        self.write_prompt("Explain payment retries \u2713", 10)
        self.assertTrue(latest_prompt(self.payload)[0].endswith("\u2713"))

    def test_one_injection_per_user_turn_but_repeated_prompt_is_new_turn(self):
        result = {"unified_prompt": MARKER + "\nUseful code", "files": [{"file_path": "payment.py"}], "pruned_tokens": 100}
        with patch("swe_pruner.antigravity_hook.ensure_backend", return_value="http://127.0.0.1:8000"), \
                patch("swe_pruner.antigravity_hook.request_json", return_value=result) as request:
            first = run_hook(self.payload, self.workspace, self.workspace)
            self.assertEqual(first["injectSteps"][0]["userMessage"], result["unified_prompt"])
            self.assertNotIn("active_file", request.call_args.args[1])
            self.assertEqual(run_hook({**self.payload, "invocationNum": 2}, self.workspace, self.workspace), {})
            self.assertEqual(request.call_count, 1)
            self.write_prompt("Explain payment retries", 9)
            self.assertIn("injectSteps", run_hook(self.payload, self.workspace, self.workspace))
            self.assertEqual(request.call_count, 2)

    def test_backend_failure_does_not_block_agent_and_is_visible(self):
        with patch("swe_pruner.antigravity_hook.ensure_backend", side_effect=RuntimeError("backend offline")):
            self.assertEqual(run_hook(self.payload, self.workspace, self.workspace), {})
        activity = json.loads((self.workspace / ".tokenwise/latest.json").read_text())
        self.assertEqual(activity["status"], "error")
        self.assertIn("backend offline", activity["error"])

    def test_out_of_budget_context_is_never_injected(self):
        result = {"unified_prompt": MARKER, "files": [{"file_path": "payment.py"}], "pruned_tokens": 99999}
        with patch("swe_pruner.antigravity_hook.ensure_backend", return_value="http://127.0.0.1:8000"), \
                patch("swe_pruner.antigravity_hook.request_json", return_value=result):
            self.assertEqual(run_hook(self.payload, self.workspace, self.workspace), {})

    def test_agent_command_returns_context_and_records_current_query(self):
        result = {"unified_prompt": MARKER + "\nAuth code", "files": [{"file_path": "auth.py"}], "pruned_tokens": 100}
        with patch("swe_pruner.antigravity_hook.ensure_backend", return_value="http://127.0.0.1:8000"), \
                patch("swe_pruner.antigravity_hook.request_json", return_value=result) as request:
            context = run_context(" Explain user's account lockout ", self.workspace, self.workspace)
        self.assertEqual(context, result["unified_prompt"])
        self.assertNotIn("active_file", request.call_args.args[1])
        activity = json.loads((self.workspace / ".tokenwise/latest.json").read_text())
        self.assertEqual(activity["transport"], "antigravity-agent-command")
        self.assertEqual(activity["query"], "Explain user's account lockout")
        self.assertEqual(activity["status"], "ready")
        self.assertFalse(activity["verification"])

    def test_agent_command_rejects_blank_query_without_backend_startup(self):
        with patch("swe_pruner.antigravity_hook.ensure_backend") as backend:
            self.assertIsNone(run_context("  ", self.workspace, self.workspace))
            backend.assert_not_called()
        activity = json.loads((self.workspace / ".tokenwise/latest.json").read_text())
        self.assertEqual(activity["status"], "error")

    def test_agent_command_rejects_disabled_configuration(self):
        settings = self.workspace / ".agents/tokenwise.json"
        settings.parent.mkdir()
        settings.write_text('{"enabled": false}', encoding="utf-8")
        with patch("swe_pruner.antigravity_hook.ensure_backend") as backend:
            self.assertIsNone(run_context("Explain auth", self.workspace, self.workspace))
            backend.assert_not_called()

    def test_agent_command_never_returns_oversized_or_invalid_context(self):
        for tokens in (99999, "100", True, -1):
            result = {"unified_prompt": MARKER, "files": [{"file_path": "auth.py"}], "pruned_tokens": tokens}
            with patch("swe_pruner.antigravity_hook.ensure_backend", return_value="http://127.0.0.1:8000"), \
                    patch("swe_pruner.antigravity_hook.request_json", return_value=result):
                self.assertIsNone(run_context("Explain auth", self.workspace, self.workspace))
            self.assertEqual(json.loads((self.workspace / ".tokenwise/latest.json").read_text())["status"], "error")

    def test_verification_reports_are_explicitly_marked(self):
        result = {"unified_prompt": MARKER, "files": [{"file_path": "auth.py"}], "pruned_tokens": 100}
        with patch("swe_pruner.antigravity_hook.ensure_backend", return_value="http://127.0.0.1:8000"), \
                patch("swe_pruner.antigravity_hook.request_json", return_value=result):
            run_context("Explain auth", self.workspace, self.workspace, verification=True)
            self.assertTrue(json.loads((self.workspace / ".tokenwise/latest.json").read_text())["verification"])
            run_hook({**self.payload, "tokenwiseVerification": True}, self.workspace, self.workspace)
            self.assertTrue(json.loads((self.workspace / ".tokenwise/latest.json").read_text())["verification"])

    def test_index_cache_refreshes_edits_additions_and_deletions(self):
        source = self.workspace / "payment.py"
        source.write_text("def charge(): pass\n", encoding="utf-8")
        cache = RepositoryIndexCache()
        first, hit = cache.get(str(self.workspace))
        self.assertFalse(hit)
        second, hit = cache.get(str(self.workspace))
        self.assertTrue(hit)
        self.assertEqual(first.fingerprint, second.fingerprint)
        source.write_text("def charge():\n    return 123\n", encoding="utf-8")
        third, hit = cache.get(str(self.workspace))
        self.assertFalse(hit)
        self.assertIn("123", third.index["payment.py"]["content"])
        self.assertNotIn("123", first.index["payment.py"]["content"])
        extra = self.workspace / "extra.py"
        extra.write_text("x = 1\n", encoding="utf-8")
        self.assertIn("extra.py", cache.get(str(self.workspace))[0].index)
        extra.unlink()
        self.assertNotIn("extra.py", cache.get(str(self.workspace))[0].index)

    def test_query_finds_services_and_tests_without_exact_symbol_names(self):
        (self.workspace / "payment_service.py").write_text("class PaymentService:\n    def process_payment(self):\n        retry_count = 3\n", encoding="utf-8")
        (self.workspace / "test_payment.py").write_text("def test_payment_retry(): pass\n", encoding="utf-8")
        (self.workspace / "auth.py").write_text("class AuthService: pass\n", encoding="utf-8")
        index = RepositoryIndex(str(self.workspace))
        index.build_index()
        matches = dict(LexicalRetriever(index).search_query("Explain payment retry logic"))
        self.assertIn("payment_service.py", matches)
        self.assertIn("test_payment.py", matches)
        self.assertNotIn("auth.py", matches)
        plural_matches = dict(LexicalRetriever(index).search_query("Explain payments and retries"))
        self.assertIn("payment_service.py", plural_matches)

    def test_malformed_settings_fail_visibly_without_starting_backend(self):
        settings = self.workspace / ".agents/tokenwise.json"
        settings.parent.mkdir()
        settings.write_text('{"enabled": broken}', encoding="utf-8")
        with patch("swe_pruner.antigravity_hook.ensure_backend") as backend:
            self.assertEqual(run_hook(self.payload, self.workspace, self.workspace), {})
            backend.assert_not_called()
        self.assertEqual(json.loads((self.workspace / ".tokenwise/latest.json").read_text())["status"], "error")

    def test_total_injection_budget_counts_preamble_and_separators(self):
        metadata = {f"file{i}.py": {"content": "def charge():\n    return 123\n" * 50} for i in range(3)}
        model = ReferenceModel()
        for budget in (256, 512, 4096):
            context, files, count = ContextBuilder(budget).pack_context(
                "payment", metadata, {}, [(path, 0.5) for path in metadata], model,
                active_file="file0.py", preamble=MARKER + "\nReference data.",
            )
            self.assertTrue(files)
            self.assertEqual(count, len(model.tokenizer.encode(context)))
            self.assertLessEqual(count, budget)

    def test_automatic_mode_reuses_neural_passes_and_cached_context(self):
        from swe_pruner.goal_compiler import GoalCompiler
        from swe_pruner.retrieval.workspace_context import WorkspaceContextBuilder
        for number in range(6):
            (self.workspace / f"payment{number}.py").write_text(
                f"def payment{number}():\n    return 'payment retry'\n", encoding="utf-8",
            )
        index = RepositoryIndex(str(self.workspace))
        index.build_index()
        model = ReferenceModel()
        builder = WorkspaceContextBuilder()
        query = "Explain payment retries"
        goal = GoalCompiler(None).deterministic_fallback(query, None, [])
        first = builder.build(index, goal, model, None, query, 0.45, 4096, 6)
        self.assertGreater(model.calls, 0)
        self.assertLessEqual(model.calls, 3)
        calls = model.calls
        second = builder.build(index, goal, model, None, query, 0.45, 4096, 6)
        self.assertEqual(model.calls, calls)
        self.assertTrue(second["context_cache_hit"])
        self.assertEqual(first["unified_prompt"], second["unified_prompt"])

    def test_dependency_interfaces_keep_actual_signatures_and_configuration(self):
        metadata = {"content": "import os\nclass Config:\n    MAX_PAYMENT_RETRIES = 3\n    async def retry(self, count: int = 3) -> bool:\n        raise RuntimeError('implementation')\n"}
        reference = ContextBuilder._signatures_only(metadata, "config.py")
        self.assertIn("MAX_PAYMENT_RETRIES = 3", reference)
        self.assertIn("async def retry(self, count: int=3) -> bool:", reference)
        self.assertNotIn("raise RuntimeError", reference)


if __name__ == "__main__":
    unittest.main()
