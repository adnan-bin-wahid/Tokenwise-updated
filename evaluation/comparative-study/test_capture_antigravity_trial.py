"""Offline tests only; no model calls, account access or command retries."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("trial", ROOT / "scripts/capture_antigravity_trial.py")
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)


class TraceTests(unittest.TestCase):
    def events(self):
        return [
            {"event": "init", "conversation_id": "c1", "init": {"model": "m"}},
            {"event": "result", "result": {"conversation_id": "c1", "status": "SUCCESS",
             "num_turns": 1, "response": "An answer", "duration_seconds": 2,
             "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120}}},
        ]

    def parse(self, events):
        return trial.summarize_trace("\n".join(json.dumps(e) for e in events), "m")

    def test_success_is_not_automatically_graded(self):
        result = self.parse(self.events())
        self.assertEqual(result["status"], "captured_ungraded")
        self.assertNotIn("correct_supported_facts", result)

    def test_empty_success_is_not_valid_answer(self):
        events = self.events()
        events[-1]["result"]["response"] = ""
        self.assertEqual(self.parse(events)["status"], "empty_answer")

    def test_denial_retains_actual_usage_not_quality(self):
        events = self.events()
        events[-1]["result"].update(response="", denied_actions=[{"action": "command"}])
        result = self.parse(events)
        self.assertEqual(result["status"], "permission_denied")
        self.assertEqual(result["reported_usage"]["input_tokens"], 100)
        self.assertFalse(result["answer_present"])

    def test_terminal_usage_is_not_added_to_step_usage(self):
        events = self.events()
        events.insert(1, {"event": "step_update", "step_update": {"conversation_id": "c1", "usage": {"input_tokens": 100}}})
        self.assertEqual(self.parse(events)["reported_usage"]["input_tokens"], 100)

    def test_tools_are_deduplicated_and_errors_are_separate(self):
        events = self.events()
        step = {"conversation_id": "c1", "step_type": "tool", "step_index": 2, "state": "DONE"}
        events[1:1] = [{"event": "step_update", "step_update": step}] * 2
        events.insert(1, {"event": "step_update", "step_update": {**step, "step_index": 3, "state": "ERROR"}})
        result = self.parse(events)
        self.assertEqual(result["observed_completed_tool_calls"], 1)
        self.assertEqual(result["observed_failed_tool_calls"], 1)

    def test_mixed_conversations_rejected(self):
        events = self.events()
        events[0]["conversation_id"] = "other"
        self.assertEqual(self.parse(events)["status"], "invalid_trace")

    def test_model_mismatch_rejected(self):
        events = self.events()
        events[0]["init"]["model"] = "other"
        self.assertEqual(self.parse(events)["status"], "invalid_trace")

    def test_two_terminal_results_rejected(self):
        events = self.events()
        events.append(events[-1])
        self.assertEqual(self.parse(events)["status"], "invalid_trace")

    def test_missing_or_invalid_usage_is_not_zero(self):
        events = self.events()
        events[-1]["result"]["usage"] = {"input_tokens": True}
        result = self.parse(events)
        self.assertEqual(result["status"], "usage_unavailable")
        self.assertIsNone(result["reported_usage"]["input_tokens"])

    def test_fingerprint_detects_changed_bytes(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            file = folder / "code.py"
            file.write_bytes(b"x=1")
            before = trial.fingerprint(folder)
            file.write_bytes(b"x=2")
            self.assertNotEqual(before, trial.fingerprint(folder))


if __name__ == "__main__":
    unittest.main()
