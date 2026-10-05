import math
import os
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from swe_pruner.goal_compiler import GoalCompiler
from swe_pruner.repository.repository_index import RepositoryIndexCache
from swe_pruner.retrieval.context_builder import ContextBuilder
from swe_pruner.retrieval.lexical_retriever import LexicalRetriever, terms
from swe_pruner.retrieval.workspace_context import WorkspaceContextBuilder
from test_antigravity import CharacterTokenizer, ReferenceModel


class RepositoryCacheTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.time = 100.0
        self.cache = RepositoryIndexCache(clock=lambda: self.time)
        self.put("auth.py", "def authenticate():\n    return 'login lockout'\n")
        self.put("tests/test_auth.py", "from auth import authenticate\ndef test_lockout():\n    assert authenticate()\n")

    def put(self, relative, text):
        filename = self.root / relative
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(text, encoding="utf-8")
        return filename

    def start(self, watcher="editor"):
        return self.cache.synchronize(str(self.root), watcher, "start")

    def update(self, *paths):
        return self.cache.synchronize(str(self.root), "editor", "update", paths)

    def test_watched_requests_do_not_walk_the_repository(self):
        first = self.start()
        with patch("swe_pruner.repository.repository_index.os.walk", side_effect=AssertionError("Unexpected scan")):
            for _ in range(10):
                index, hit = self.cache.get(str(self.root))
                self.assertTrue(hit)
                self.assertEqual(index.fingerprint, first.fingerprint)

    def test_file_events_reparse_only_changed_content(self):
        first = self.start()
        entry = self.cache.entries[str(self.root)]
        with patch.object(entry.indexer, "index_file", wraps=entry.indexer.index_file) as parse:
            self.put("auth.py", "def authenticate():\n    return 'new password policy'\n")
            second = self.update("auth.py")
            self.assertEqual(parse.call_count, 1)
            self.assertEqual(parse.call_args.args[0].name, "auth.py")
            self.assertIs(first.index["tests/test_auth.py"], second.index["tests/test_auth.py"])
            self.assertIsNot(first.index["auth.py"], second.index["auth.py"])
            self.assertNotIn("new password", first.index["auth.py"]["content"])

    def test_same_size_edit_with_preserved_mtime_invalidates_content(self):
        first = self.start()
        filename = self.root / "auth.py"
        stat = filename.stat()
        filename.write_text(first.index["auth.py"]["content"].replace("login", "hello"), encoding="utf-8")
        os.utime(filename, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        second = self.update("auth.py")
        self.assertNotEqual(first.fingerprint, second.fingerprint)
        self.assertIn("hello", second.index["auth.py"]["content"])

    def test_touching_unchanged_content_keeps_derived_caches(self):
        first = self.start()
        entry = self.cache.entries[str(self.root)]
        with patch.object(entry.indexer, "index_file", side_effect=AssertionError("Unnecessary parse")):
            second = self.update("auth.py")
        self.assertEqual(first.fingerprint, second.fingerprint)
        self.assertIs(first.index["auth.py"], second.index["auth.py"])

    def test_additions_and_deletions_preserve_old_snapshots(self):
        first = self.start()
        self.put("payment.py", "def charge(): return 42\n")
        second = self.update("payment.py")
        (self.root / "auth.py").unlink()
        third = self.update("auth.py")
        self.assertNotIn("payment.py", first.index)
        self.assertIn("auth.py", second.index)
        self.assertNotIn("auth.py", third.index)
        self.assertIn("payment.py", third.index)

    def test_directory_rename_updates_only_affected_subtrees(self):
        self.start()
        (self.root / "tests").rename(self.root / "checks")
        updated = self.update("tests", "checks")
        self.assertNotIn("tests/test_auth.py", updated.index)
        self.assertIn("checks/test_auth.py", updated.index)

    def test_directories_named_like_python_files_are_still_subtrees(self):
        self.put("package.py/child.py", "x = 1\n")
        self.start()
        (self.root / "package.py").rename(self.root / "renamed.py")
        updated = self.update("package.py", "renamed.py")
        self.assertNotIn("package.py/child.py", updated.index)
        self.assertIn("renamed.py/child.py", updated.index)

    def test_events_cannot_read_traversal_or_excluded_files(self):
        self.start()
        self.put(".venv/private.py", "secret = 'never index'\n")
        updated = self.update(".venv/private.py", ".venv")
        self.assertNotIn(".venv/private.py", updated.index)
        for name in ("", ".", "../outside.py", str(self.root / "auth.py")):
            with self.assertRaises(ValueError):
                self.update(name)

    def test_retargeted_symlink_removes_previous_cached_content(self):
        self.start()
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / "outside.py"
        target.write_text("secret = 'outside'\n", encoding="utf-8")
        filename = self.root / "auth.py"
        filename.unlink()
        try:
            filename.symlink_to(target)
        except OSError:
            self.skipTest("This Windows account cannot create file symlinks")
        updated = self.update("auth.py")
        self.assertNotIn("auth.py", updated.index)

    def test_background_reconciliation_recovers_a_missed_event(self):
        first = self.start()
        self.time += 60
        self.cache.synchronize(str(self.root), "editor", "reconcile")
        self.put("missed.py", "def missed_event(): pass\n")
        self.time += 61
        refreshed = self.cache.reconcile_watched()
        self.assertEqual(len(refreshed), 1)
        self.assertIn("missed.py", refreshed[0].index)
        self.assertNotEqual(first.fingerprint, refreshed[0].fingerprint)

    def test_reconciliation_detects_missed_edits_even_if_stat_values_match(self):
        first = self.start()
        self.time += 60
        self.cache.synchronize(str(self.root), "editor", "reconcile")
        self.put("auth.py", first.index["auth.py"]["content"].replace("login", "hello"))
        entry = self.cache.entries[str(self.root)]
        self.time += 61
        with patch.object(entry, "_version", side_effect=lambda filename: entry.file_versions[entry._relative(filename)]):
            refreshed = self.cache.reconcile_watched()
        self.assertNotEqual(first.fingerprint, refreshed[0].fingerprint)
        self.assertIn("hello", refreshed[0].index["auth.py"]["content"])

    def test_renewing_an_expired_lease_scans_before_trusting_events_again(self):
        self.start()
        self.time += 91
        self.put("missed.py", "x = 1\n")
        renewed = self.cache.synchronize(str(self.root), "editor", "reconcile")
        self.assertIn("missed.py", renewed.index)

    def test_missing_or_expired_watchers_keep_scan_before_request_behavior(self):
        self.start()
        self.put("missed.py", "x = 1\n")
        self.time += 91
        index, hit = self.cache.get(str(self.root))
        self.assertFalse(hit)
        self.assertIn("missed.py", index.index)
        self.put("later.py", "x = 2\n")
        self.assertIn("later.py", self.cache.get(str(self.root))[0].index)

    def test_stopping_one_window_does_not_disable_another(self):
        self.start("first")
        self.start("second")
        self.cache.synchronize(str(self.root), "first", "stop")
        with patch("swe_pruner.repository.repository_index.os.walk", side_effect=AssertionError("Unexpected scan")):
            self.cache.get(str(self.root))
        self.cache.synchronize(str(self.root), "second", "stop")
        self.put("new.py", "x = 3\n")
        self.assertIn("new.py", self.cache.get(str(self.root))[0].index)

    def test_delayed_updates_cannot_reactivate_a_stopped_watcher(self):
        self.cache.synchronize(str(self.root), "editor", "start", sequence=1)
        self.cache.synchronize(str(self.root), "editor", "stop", sequence=3)
        self.cache.synchronize(str(self.root), "editor", "update", ["auth.py"], sequence=2)
        self.assertEqual(self.cache.entries[str(self.root)].watchers, {})
        self.put("new.py", "x = 4\n")
        self.assertIn("new.py", self.cache.get(str(self.root))[0].index)
        self.cache.synchronize(str(self.root), "editor", "start", sequence=4)
        self.assertIn("editor", self.cache.entries[str(self.root)].watchers)

    def test_long_scan_in_one_repository_does_not_lock_other_repositories(self):
        other = self.root / "other"
        other.mkdir()
        (other / "other.py").write_text("x = 1\n", encoding="utf-8")
        self.cache.synchronize(str(other), "second", "start")
        self.start()
        entry = self.cache.entries[str(self.root)]
        entered, release = threading.Event(), threading.Event()
        original = entry.build_index
        def slow_scan(**kwargs):
            entered.set()
            if not release.wait(5):
                raise TimeoutError("Test scan was not released")
            original(**kwargs)
        with ThreadPoolExecutor(max_workers=2) as pool, patch.object(entry, "build_index", side_effect=slow_scan):
            future = pool.submit(self.cache.synchronize, str(self.root), "editor", "start")
            self.assertTrue(entered.wait(2))
            try:
                fast = pool.submit(self.cache.get, str(other)).result(timeout=1)
                self.assertIn("other.py", fast[0].index)
            finally:
                release.set()
            future.result(timeout=2)

    def test_lru_eviction_rebuilds_instead_of_returning_stale_metadata(self):
        cache = RepositoryIndexCache(capacity=1)
        cache.synchronize(str(self.root), "editor", "start")
        other = self.root / "other"
        other.mkdir()
        cache.get(str(other))
        self.put("new.py", "x = 5\n")
        self.assertIn("new.py", cache.get(str(self.root))[0].index)

    def test_query_independent_search_and_graph_are_reused(self):
        first = self.start()
        builder = WorkspaceContextBuilder()
        lexical, graph, reused = builder.prepare(first)
        self.assertFalse(reused)
        with patch("swe_pruner.retrieval.workspace_context.DependencyGraph.build_graph", side_effect=AssertionError("Unnecessary graph rebuild")), \
             patch("swe_pruner.retrieval.lexical_retriever.document_features", side_effect=AssertionError("Unnecessary term extraction")):
            second_lexical, second_graph, reused = builder.prepare(self.cache.get(str(self.root))[0])
            self.assertIs(lexical, second_lexical)
            self.assertIs(graph, second_graph)
            self.assertTrue(reused)
            self.assertIn("auth.py", dict(lexical.search_query("Explain login lockout")))
            self.assertIn("tests/test_auth.py", lexical.search_identifiers(["test_lockout"]))

    def test_changed_symbols_and_imports_invalidate_search_and_graph(self):
        builder = WorkspaceContextBuilder()
        lexical, graph, _ = builder.prepare(self.start())
        self.assertIn("auth.py", graph.dependencies["tests/test_auth.py"])
        self.put("tests/test_auth.py", "def test_payment(): pass\n")
        changed = self.update("tests/test_auth.py")
        next_lexical, next_graph, reused = builder.prepare(changed)
        self.assertFalse(reused)
        self.assertEqual(next_graph.dependencies["tests/test_auth.py"], set())
        self.assertEqual(next_lexical.search_identifiers(["test_lockout"]), set())
        self.assertEqual(lexical.search_identifiers(["test_lockout"]), {"tests/test_auth.py"})
        self.assertIn("auth.py", graph.dependencies["tests/test_auth.py"])

    def test_token_counts_are_reused_but_not_across_tokenizers_or_edits(self):
        class CountingTokenizer(CharacterTokenizer):
            def __init__(self):
                self.calls = 0
            def encode(self, text, **kwargs):
                self.calls += 1
                return super().encode(text, **kwargs)
        first = self.start()
        metadata = first.index["auth.py"]
        tokenizer = CountingTokenizer()
        for _ in range(5):
            self.assertEqual(ContextBuilder._file_count(metadata, metadata["content"], tokenizer), len(metadata["content"]))
        self.assertEqual(tokenizer.calls, 1)
        other = CountingTokenizer()
        ContextBuilder._file_count(metadata, metadata["content"], other)
        self.assertEqual(other.calls, 1)
        self.put("auth.py", "def authenticate(): return False\n")
        updated = self.update("auth.py").index["auth.py"]
        self.assertNotIn("_token_counts", updated)
        ContextBuilder._file_count(updated, updated["content"], tokenizer)
        self.assertEqual(tokenizer.calls, 2)

    def test_cached_signatures_do_not_reparse_and_refresh_after_edits(self):
        first = self.start()
        with patch("swe_pruner.retrieval.context_builder.ast.parse", side_effect=AssertionError("Unnecessary AST parse")):
            self.assertIn("def authenticate():", ContextBuilder._signatures_only(first.index["auth.py"], "auth.py"))
        self.put("auth.py", "def authenticate(limit: int = 5): return limit\n")
        updated = self.update("auth.py")
        self.assertIn("limit: int=5", ContextBuilder._signatures_only(updated.index["auth.py"], "auth.py"))

    def test_similar_queries_and_changed_fingerprints_do_not_share_context_results(self):
        index = self.start()
        builder, model = WorkspaceContextBuilder(), ReferenceModel()
        def build(query, snapshot):
            goal = GoalCompiler(None).deterministic_fallback(query, None, [])
            return builder.build(snapshot, goal, model, None, query, 0.45, 4096, 6)
        first = build("Explain login lockout", index)
        second = build("Explain login lockout for admins", index)
        self.assertFalse(first["context_cache_hit"])
        self.assertFalse(second["context_cache_hit"])
        self.assertTrue(second["retrieval_cache_hit"])
        self.assertTrue(build("Explain login lockout", index)["context_cache_hit"])
        self.put("auth.py", "def authenticate(): return 'new login lockout policy'\n")
        changed = build("Explain login lockout", self.update("auth.py"))
        self.assertFalse(changed["context_cache_hit"])
        self.assertIn("new login lockout policy", changed["unified_prompt"])

    def test_cached_postings_preserve_legacy_lexical_scores(self):
        index = self.start()
        retriever = LexicalRetriever(index)
        query_terms = set(terms("login lockout authenticate"))
        expected = {}
        for term in sorted(query_terms):
            frequency = sum(term in metadata["_lexical"]["content"] for metadata in index.index.values())
            weight = math.log(1 + len(index.index) / (1 + frequency))
            for name, metadata in index.index.items():
                feature = metadata["_lexical"]
                score = weight * (5 * (term in feature["path"]) + 3 * (term in feature["symbols"]) + min(feature["content"][term], 4))
                if score:
                    expected[name] = expected.get(name, 0) + score
        self.assertEqual(dict(retriever.search_query("login lockout authenticate")), expected)


class IndexApiTests(unittest.TestCase):
    def test_native_http_warm_index_edit_and_exact_query_caches(self):
        import json
        import socket
        import time
        from urllib.request import Request, urlopen
        import uvicorn
        from swe_pruner import online_serving as serving

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            filename = root / "auth.py"
            filename.write_text("def authenticate(): return 'login lockout'\n", encoding="utf-8")
            with patch.object(serving, "repository_cache", RepositoryIndexCache()), \
                 patch.object(serving, "workspace_builder", WorkspaceContextBuilder()), \
                 patch.object(serving, "check_model_path", return_value=False), \
                 patch.object(serving, "model", None), socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                url = f"http://127.0.0.1:{listener.getsockname()[1]}"
                server = uvicorn.Server(uvicorn.Config(serving.app, log_level="warning"))
                worker = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
                worker.start()
                try:
                    for _ in range(500):
                        if server.started:
                            break
                        time.sleep(0.01)
                    self.assertTrue(server.started, "Temporary HTTP service did not start")
                    def post(endpoint, payload):
                        request = Request(url + endpoint, data=json.dumps(payload).encode("utf-8"),
                                          headers={"Content-Type": "application/json"}, method="POST")
                        with urlopen(request, timeout=5) as response:
                            return json.load(response)
                    payload = {"workspace_root": str(root), "watcher_id": "http-editor", "action": "start", "sequence": 1}
                    self.assertEqual(post("/index-workspace", payload)["indexed_files"], 1)
                    serving.model = ReferenceModel()
                    request = {"workspace_root": str(root), "query": "Explain login lockout", "token_budget": 4096}
                    with patch("swe_pruner.repository.repository_index.os.walk", side_effect=AssertionError("Warm HTTP request scanned source")):
                        first = post("/prune-workspace", request)
                        repeated = post("/prune-workspace", request)
                        similar = post("/prune-workspace", {**request, "query": "Explain login lockout for admins"})
                    self.assertTrue(first["index_cache_hit"])
                    self.assertTrue(first["retrieval_cache_hit"])
                    self.assertTrue(repeated["context_cache_hit"])
                    self.assertFalse(similar["context_cache_hit"])
                    filename.write_text("def authenticate(): return 'fresh login lockout policy'\n", encoding="utf-8")
                    post("/index-workspace", {**payload, "action": "update", "paths": ["auth.py"], "sequence": 2})
                    fresh = post("/prune-workspace", request)
                    self.assertFalse(fresh["context_cache_hit"])
                    self.assertIn("fresh login lockout policy", fresh["unified_prompt"])
                    self.assertLessEqual(fresh["pruned_tokens"], request["token_budget"])
                    post("/index-workspace", {**payload, "action": "stop", "sequence": 3})
                    self.assertEqual(serving.repository_cache.entries[str(root)].watchers, {})
                finally:
                    server.should_exit = True
                    worker.join(timeout=5)
                    self.assertFalse(worker.is_alive(), "Temporary HTTP service did not stop")
            self.assertIsNone(serving.reconciliation_task)

    def test_index_api_works_without_model_and_context_observes_updates(self):
        from fastapi.testclient import TestClient
        from swe_pruner import online_serving as serving
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            filename = root / "auth.py"
            filename.write_text("def authenticate(): return 'login lockout'\n", encoding="utf-8")
            with patch.object(serving, "repository_cache", RepositoryIndexCache()), \
                 patch.object(serving, "workspace_builder", WorkspaceContextBuilder()), \
                 patch.object(serving, "check_model_path", return_value=False), \
                 patch.object(serving, "model", None), TestClient(serving.app) as client:
                payload = {"workspace_root": str(root), "watcher_id": "editor", "action": "start", "sequence": 1}
                self.assertEqual(client.post("/index-workspace", json=payload).status_code, 200)
                self.assertIsNone(serving.model)
                serving.model = ReferenceModel()
                request = {"workspace_root": str(root), "query": "Explain login lockout", "token_budget": 4096}
                first = client.post("/prune-workspace", json=request)
                self.assertEqual(first.status_code, 200)
                self.assertTrue(first.json()["retrieval_cache_hit"])
                filename.write_text("def authenticate(): return 'updated login lockout policy'\n", encoding="utf-8")
                updated = client.post("/index-workspace", json={**payload, "action": "update", "paths": ["auth.py"], "sequence": 2})
                self.assertEqual(updated.status_code, 200)
                result = client.post("/prune-workspace", json=request).json()
                self.assertFalse(result["context_cache_hit"])
                self.assertIn("updated login lockout policy", result["unified_prompt"])
                self.assertEqual(client.post("/index-workspace", json={**payload, "paths": ["../outside.py"], "action": "update", "sequence": 3}).status_code, 400)
                self.assertEqual(client.post("/index-workspace", json={**payload, "paths": ["auth.py"] * 513}).status_code, 422)
            self.assertIsNone(serving.reconciliation_task)


if __name__ == "__main__":
    unittest.main()
