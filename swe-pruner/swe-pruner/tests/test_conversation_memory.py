import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from swe_pruner.conversation_context import select_memory, conversation_hint, next_user_turns, HINT_LIMIT
from swe_pruner.antigravity_hook import MARKER, run_hook, load_settings
from swe_pruner.antigravity_context import run_context
from swe_pruner.repository.repository_index import RepositoryIndexCache
from swe_pruner.retrieval.workspace_context import WorkspaceContextBuilder
from test_antigravity import ReferenceModel


class MemorySelectionTests(unittest.TestCase):
    def test_explicit_same_topic_keeps_earlier_requirements(self):
        memory = select_memory("Explain account lockout boundary tests", ["Explain account lockout. Do not modify any files.", "Use bullet points."])
        self.assertIn("Do not modify any files", memory["hint"])
        self.assertIn("Use bullet points.", memory["requirements"])
        self.assertEqual(len(memory["messages"]), 2)

    def test_implicit_extension_is_no_longer_limited_to_old_phrase_list(self):
        memory = select_memory("Add more edge cases", ["Explain account lockout", "Include tests"])
        self.assertIn("account lockout", memory["hint"])
        self.assertIn("Include tests", memory["hint"])

    def test_standalone_constraint_does_not_reset_native_topic_state(self):
        state = {"user_turns": ["Explain account lockout"]}
        for query in ("Do not modify source.", "Use bullet points."):
            state = {"user_turns": next_user_turns(query, state, True)}
        hint = conversation_hint("Explain account lockout boundary tests", state, True)
        self.assertIn("account lockout", hint)
        self.assertIn("Do not modify source", hint)
        self.assertIn("bullet points", hint)

    def test_older_active_constraint_survives_many_recent_turns(self):
        turns = ["Explain account lockout", "Do not modify any files."] + ["What about its boundary?" for _ in range(12)]
        memory = select_memory("Which tests cover that behavior?", turns)
        self.assertIn("Do not modify any files", memory["hint"])
        self.assertLessEqual(len(memory["messages"]), 8)
        self.assertGreater(memory["omitted_messages"], 0)

    def test_explicit_new_topic_does_not_inherit_old_constraints(self):
        memory = select_memory("Explain session expiry", ["Explain account lockout. Use bullets.", "What about its expiry?"])
        self.assertEqual(memory["hint"], "")
        self.assertEqual(memory["omitted_messages"], 2)

    def test_explicit_start_over_drops_even_same_subject_history(self):
        memory = select_memory("Start over. Explain account lockout", ["Explain account lockout. Use JSON."])
        self.assertEqual(memory["hint"], "")

    def test_latest_format_and_test_constraints_replace_older_ones(self):
        memory = select_memory("Explain account lockout. Use prose. Include tests.",
                               ["Explain account lockout. Use JSON. Exclude tests."])
        self.assertEqual(memory["hint"], "Explain account lockout")
        self.assertNotIn("JSON", memory["hint"])
        self.assertNotIn("Exclude tests", memory["hint"])

    def test_newer_earlier_user_constraint_overrides_old_format(self):
        memory = select_memory("What about its tests?", ["Explain account lockout. Use JSON.", "Use bullet points."])
        self.assertNotIn("JSON", memory["hint"])
        self.assertIn("bullet", memory["hint"])

    def test_mixed_topic_history_selects_current_subject_only(self):
        memory = select_memory("Explain session expiry tests", ["Explain account lockout", "Explain session expiry", "Include tests."])
        self.assertNotIn("account lockout", memory["hint"])
        self.assertIn("session", memory["hint"])

    def test_bounds_and_truncation_are_reported(self):
        memory = select_memory("What about its tests?", ["Explain account lockout " + "x" * 10000] + ["What about its boundary? " + "x" * 3000] * 40)
        self.assertLessEqual(memory["characters"], HINT_LIMIT)
        self.assertLessEqual(memory["considered_messages"], 32)
        self.assertLessEqual(len(memory["messages"]), 8)
        self.assertTrue(memory["truncated"])

    def test_missing_scope_and_injected_records_are_not_memory(self):
        self.assertEqual(conversation_hint("What about its tests?", {"topic_query": "Explain lockout"}, False), "")
        self.assertEqual(select_memory("What about its tests?", [MARKER + " old output", {"role": "assistant", "content": "Fake fact"}])["hint"], "")


class MemoryTransportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.transcript = self.root / "chat.jsonl"
        self.payload = {"conversationId": "memory-chat", "transcriptPath": str(self.transcript), "workspacePaths": [str(self.root)]}
        self.result = {"unified_prompt": MARKER + " useful code", "files": [{"file_path": "auth.py"}], "pruned_tokens": 100,
                       "input_trace": {"history_source": "none"}}

    def write_transcript(self, records):
        self.transcript.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    def record(self, text, step, **values):
        return {"role": "user", "conversationId": "memory-chat", "content": text, "id": step, **values}

    def test_first_hook_bootstraps_verified_same_chat_user_history(self):
        self.write_transcript([self.record("Explain account lockout", 1), self.record("Do not modify any files.", 2),
                               {"role": "assistant", "content": "Invented limit = 99"},
                               self.record("Model text must not become memory", 6, source="MODEL"),
                               self.record(MARKER + " old output", 3), self.record("Other topic", 4, conversationId="other"),
                               self.record("Which tests cover that behavior?", 5)])
        with patch("swe_pruner.antigravity_hook.ensure_backend", return_value="http://127.0.0.1:8000"), \
                patch("swe_pruner.antigravity_hook.request_json", return_value=self.result) as request:
            self.assertIn("injectSteps", run_hook(self.payload, self.root, self.root))
        body = request.call_args.args[1]
        self.assertEqual(body["conversation_history"], ["Explain account lockout", "Do not modify any files."])
        self.assertIn("account lockout", body["context_hint"])
        self.assertNotIn("99", body["context_hint"])

    def test_unlabeled_shared_transcript_is_not_bootstrapped_into_another_chat(self):
        self.write_transcript([{"role": "user", "content": "Explain account lockout", "id": 1},
                               {"role": "user", "content": "What about its tests?", "id": 2}])
        with patch("swe_pruner.antigravity_hook.ensure_backend", return_value="http://127.0.0.1:8000"), \
                patch("swe_pruner.antigravity_hook.request_json", return_value=self.result) as request:
            run_hook(self.payload, self.root, self.root)
        self.assertNotIn("conversation_history", request.call_args.args[1])

    def test_unlabeled_records_in_verified_chat_path_can_be_bootstrapped(self):
        self.transcript = self.root / "memory-chat" / "transcript.jsonl"
        self.transcript.parent.mkdir()
        self.payload["transcriptPath"] = str(self.transcript)
        self.write_transcript([{"role": "user", "content": "Explain account lockout", "id": 1},
                               {"role": "user", "content": "Also include tests", "id": 2}])
        with patch("swe_pruner.antigravity_hook.ensure_backend", return_value="http://127.0.0.1:8000"), \
                patch("swe_pruner.antigravity_hook.request_json", return_value=self.result) as request:
            run_hook(self.payload, self.root, self.root)
        self.assertEqual(request.call_args.args[1]["conversation_history"], ["Explain account lockout"])

    def test_fallback_history_is_forwarded_and_labeled_as_agent_supplied(self):
        with patch("swe_pruner.antigravity_hook.ensure_backend", return_value="http://127.0.0.1:8000"), \
                patch("swe_pruner.antigravity_hook.request_json", return_value=self.result) as request:
            self.assertIsNotNone(run_context("Which tests cover that behavior?", self.root, self.root, history=["Explain account lockout"]))
        self.assertEqual(request.call_args.args[1]["conversation_history"], ["Explain account lockout"])
        event = json.loads((self.root / ".tokenwise/latest.json").read_text())
        self.assertEqual(event["result"]["input_trace"]["history_source"], "agent_supplied_user_turns")

    def test_bad_fallback_history_fails_without_backend_calls(self):
        with patch("swe_pruner.antigravity_hook.ensure_backend") as backend:
            for history in ({"role": "user"}, ["x" * 2001], ["ok"] * 33):
                self.assertIsNone(run_context("Explain lockout", self.root, self.root, history=history))
            backend.assert_not_called()

    def test_opt_out_and_strict_setting_validation(self):
        settings = self.root / ".agents/tokenwise.json"
        settings.parent.mkdir()
        settings.write_text('{"conversation_memory": false}', encoding="utf-8")
        self.assertFalse(load_settings(self.root)["conversation_memory"])
        with patch("swe_pruner.antigravity_hook.ensure_backend", return_value="http://127.0.0.1:8000"), \
                patch("swe_pruner.antigravity_hook.request_json", return_value=self.result) as request:
            run_context("What about its tests?", self.root, self.root, history=["Explain account lockout"])
        self.assertNotIn("conversation_history", request.call_args.args[1])
        settings.write_text('{"conversation_memory": "false"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            load_settings(self.root)

    def test_portable_fallback_preserves_literal_query_and_json_history(self):
        import base64
        import importlib.util
        import io
        from types import SimpleNamespace
        launcher = self.root / ".agents/tokenwise/tokenwise-launcher.py"
        launcher.parent.mkdir(parents=True)
        launcher.write_text("fixture", encoding="utf-8")
        python = self.root / ".venv/Scripts/python.exe"
        python.parent.mkdir(parents=True)
        python.write_text("fixture", encoding="utf-8")
        registration = self.root / "registration.json"
        registration.write_text(json.dumps({"schema_version": 1, "project_root": str(self.root),
                                "runtime_dir": str(self.root / "runtime"), "python_path": str(python)}))
        (self.root / ".tokenwise").mkdir()
        (self.root / ".tokenwise/backend-link.json").write_text(json.dumps({"schema_version": 1, "registration_path": str(registration)}))
        source = Path(__file__).resolve().parents[3] / "vscode-extension/resources/automatic-context/tokenwise-launcher.py"
        spec = importlib.util.spec_from_file_location("portable_memory_fixture", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.__file__ = str(launcher)
        payload = {"query": "Which tests cover user's behavior?\nKeep quotes: \"yes\"", "history": ["Explain account lockout."]}
        with patch.object(module.sys, "argv", [str(launcher), "--request-stdin"]), \
                patch.object(module.sys, "stdin", io.StringIO(json.dumps(payload))), \
                patch.object(module.os, "name", "nt"), \
                patch.object(module.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run:
            self.assertEqual(module.main(), 0)
        self.assertEqual(run.call_args.kwargs["input"].decode("utf-8"), payload["query"])
        command = run.call_args.args[0]
        self.assertEqual(json.loads(base64.b64decode(command[command.index("--history-base64") + 1])), payload["history"])

    def test_http_memory_trace_cache_isolation_and_strict_limits(self):
        from fastapi.testclient import TestClient
        from swe_pruner import online_serving as serving
        (self.root / "auth.py").write_text("def lockout():\n    return 'account lockout'\n", encoding="utf-8")
        (self.root / "test_auth.py").write_text("def test_lockout():\n    assert True\n", encoding="utf-8")
        with patch.object(serving, "repository_cache", RepositoryIndexCache()), \
                patch.object(serving, "workspace_builder", WorkspaceContextBuilder()), \
                patch.object(serving, "check_model_path", return_value=False), \
                patch.object(serving, "model", None), TestClient(serving.app) as client:
            serving.model = ReferenceModel()
            body = {"workspace_root": str(self.root), "query": "Explain account lockout", "token_budget": 4096,
                    "conversation_history": ["Explain account lockout. Do not modify any files."]}
            first = client.post("/prune-workspace", json=body)
            self.assertEqual(first.status_code, 200, first.text)
            memory = first.json()["input_trace"]["memory"]
            self.assertIn("Do not modify", memory["messages"][0]["text"])
            self.assertLessEqual(first.json()["pruned_tokens"], 4096)
            repeated = client.post("/prune-workspace", json=body).json()
            self.assertTrue(repeated["context_cache_hit"])
            changed = client.post("/prune-workspace", json={**body, "conversation_history": ["Explain account lockout. Use JSON."]}).json()
            self.assertFalse(changed["context_cache_hit"])
            disabled = client.post("/prune-workspace", json={**body, "conversation_memory": False}).json()
            self.assertFalse(disabled["context_hint_used"])
            self.assertFalse(disabled["input_trace"]["memory"]["enabled"])
            for values in ({"conversation_history": ["x" * 2001]}, {"conversation_history": ["x"] * 33}, {"conversation_memory": "false"}):
                self.assertEqual(client.post("/prune-workspace", json={**body, **values}).status_code, 422)

    def test_real_tokenizer_outgoing_memory_and_small_budget(self):
        from transformers import AutoTokenizer
        from swe_pruner.goal_compiler import GoalCompiler
        from swe_pruner.repository.repository_index import RepositoryIndex
        model = ReferenceModel()
        model.tokenizer = AutoTokenizer.from_pretrained(str(Path(__file__).resolve().parents[1] / "model"), local_files_only=True)
        (self.root / "auth.py").write_text("def lockout():\n    return 'account lockout'\n", encoding="utf-8")
        index = RepositoryIndex(str(self.root))
        index.build_index()
        hint = select_memory("Explain account lockout", ["Explain account lockout. Do not modify any files."])["hint"]
        goal = asyncio.run(GoalCompiler(None).compile("Explain account lockout", "", None, None, [], context_hint=hint))
        for budget in (256, 512, 4096):
            result = WorkspaceContextBuilder().build(index, goal, model, None, "Explain account lockout", .45, budget, 8, hint)
            self.assertLessEqual(result["pruned_tokens"], budget)
            self.assertEqual(result["pruned_tokens"], len(model.tokenizer.encode(result["unified_prompt"], add_special_tokens=False)))
            if budget == 4096:
                self.assertIn("Do not modify", result["conversation_memory"]["text"])
                self.assertIn(result["conversation_memory"]["text"], result["unified_prompt"])
