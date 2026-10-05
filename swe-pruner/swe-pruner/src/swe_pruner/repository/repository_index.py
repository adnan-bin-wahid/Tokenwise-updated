import hashlib
import logging
import os
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Callable, Dict, Iterable

from .python_indexer import PythonASTIndexer
from ..retrieval.lexical_retriever import document_features

logger = logging.getLogger(__name__)


class RepositoryIndex:
    """Copy-on-write Python metadata; unchanged files retain their derived caches."""

    SUPPORTED_SUFFIXES = {".py"}
    EXCLUDE_DIRS = frozenset({
        '.git', '.venv', 'venv', 'node_modules', '__pycache__', '.vscode', '.idea',
        'build', 'dist', 'carbon_artifacts', '.pytest_cache', '.mypy_cache',
        '.agents', '.agent', '.tokenwise',
    })

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root).resolve()
        self.indexer = PythonASTIndexer()
        self.index: Dict[str, Any] = {}
        self.file_versions: dict[str, tuple] = {}
        self.fingerprint = ""
        self.lock = threading.RLock()
        self.last_reconciled = 0.0
        self.watchers: dict[str, float] = {}
        self.watcher_versions: dict[str, tuple[int, float]] = {}

    def _relative(self, filename: Path) -> str:
        filename.resolve().relative_to(self.workspace_root)
        relative = filename.relative_to(self.workspace_root)
        if any(part in self.EXCLUDE_DIRS for part in relative.parts[:-1]):
            raise ValueError("Excluded repository path")
        return relative.as_posix()

    @staticmethod
    def _version(filename: Path) -> tuple:
        stat = filename.stat()
        return stat.st_mtime_ns, stat.st_size, stat.st_ctime_ns, stat.st_ino

    def _read(self, filename: Path, force: bool = False) -> tuple[str, dict, tuple]:
        relative = self._relative(filename)
        version = self._version(filename)
        previous = self.index.get(relative)
        if not force and previous is not None and self.file_versions.get(relative) == version:
            return relative, previous, version
        for _ in range(3):
            content = filename.read_text(encoding="utf-8", errors="replace")
            after = self._version(filename)
            if version == after:
                break
            version = after
        else:
            raise OSError("File kept changing while being indexed")
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if previous is not None and previous.get("_content_hash") == digest:
            return relative, previous, version
        metadata = self.indexer.index_file(filename, content=content)
        metadata.update(content=content, _content_hash=digest)
        metadata["_lexical"] = document_features(relative, metadata)
        return relative, metadata, version

    def _files(self, directory: Path) -> Iterable[Path]:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [name for name in dirs if name not in self.EXCLUDE_DIRS]
            for name in files:
                filename = Path(root) / name
                if filename.suffix.lower() in self.SUPPORTED_SUFFIXES:
                    yield filename

    def _commit(self, metadata: dict, versions: dict) -> None:
        self.index, self.file_versions = metadata, versions
        contents = repr(sorted((name, item["_content_hash"]) for name, item in metadata.items()))
        self.fingerprint = hashlib.sha256(contents.encode("utf-8")).hexdigest()

    def build_index(self, verify_contents: bool = False) -> None:
        if not self.workspace_root.is_dir():
            raise ValueError(f"Workspace does not exist: {self.workspace_root}")
        metadata, versions = {}, {}
        for filename in self._files(self.workspace_root):
            try:
                relative, item, version = self._read(filename, force=verify_contents)
                metadata[relative], versions[relative] = item, version
            except (OSError, ValueError) as exc:
                logger.warning("Unable to index %s: %s", filename, exc)
        self._commit(metadata, versions)

    def apply_changes(self, paths: Iterable[str]) -> None:
        metadata, versions = self.index.copy(), self.file_versions.copy()
        for relative in paths:
            candidate = Path(relative)
            if not candidate.parts or candidate.is_absolute() or ".." in candidate.parts:
                raise ValueError("Changed paths must be relative and stay inside the workspace")
            filename = self.workspace_root / candidate
            try:
                normalized = self._relative(filename)
            except ValueError:
                prefix = candidate.as_posix().rstrip("/")
                for name in list(metadata):
                    if name == prefix or name.startswith(prefix + "/"):
                        metadata.pop(name, None)
                        versions.pop(name, None)
                continue
            # Directory events refresh only that subtree, including removals/renames.
            prefix = normalized.rstrip("/") + "/"
            directory = filename.is_dir() or filename.suffix.lower() not in self.SUPPORTED_SUFFIXES
            if not directory and not filename.is_file():
                directory = any(name.startswith(prefix) for name in metadata)
            if directory:
                for name in list(metadata):
                    if name.startswith(prefix):
                        metadata.pop(name, None)
                        versions.pop(name, None)
                if not filename.is_dir() or candidate.name in self.EXCLUDE_DIRS:
                    continue
                files = self._files(filename)
            else:
                metadata.pop(normalized, None)
                versions.pop(normalized, None)
                files = [filename] if filename.is_file() else []
            for source in files:
                try:
                    name, item, version = self._read(source, force=True)
                    metadata[name], versions[name] = item, version
                except (OSError, ValueError) as exc:
                    logger.warning("Unable to update %s: %s", source, exc)
        self._commit(metadata, versions)

    def snapshot(self) -> "RepositoryIndex":
        snapshot = RepositoryIndex(str(self.workspace_root))
        snapshot.index = self.index.copy()
        snapshot.file_versions = self.file_versions.copy()
        snapshot.fingerprint = self.fingerprint
        return snapshot


class RepositoryIndexCache:
    """Watch-leased incremental indexes, with conservative fallback for other clients."""

    def __init__(self, capacity: int = 8, reconcile_seconds: float = 120,
                 lease_seconds: float = 90, clock: Callable[[], float] = time.monotonic):
        self.capacity = capacity
        self.reconcile_seconds, self.lease_seconds, self.clock = reconcile_seconds, lease_seconds, clock
        self.entries: OrderedDict[str, RepositoryIndex] = OrderedDict()
        self.lock = threading.Lock()

    def _entry(self, workspace_root: str) -> RepositoryIndex:
        key = str(Path(workspace_root).resolve())
        with self.lock:
            index = self.entries.pop(key, None) or RepositoryIndex(key)
            self.entries[key] = index
            while len(self.entries) > self.capacity:
                self.entries.popitem(last=False)
            return index

    def _watching(self, index: RepositoryIndex) -> bool:
        now = self.clock()
        index.watchers = {key: expiry for key, expiry in index.watchers.items() if expiry > now}
        index.watcher_versions = {key: item for key, item in index.watcher_versions.items() if item[1] > now}
        return bool(index.watchers)

    def _scan(self, index: RepositoryIndex) -> None:
        # Reconciliation checks bytes too: missed events can preserve file timestamps.
        index.build_index(verify_contents=True)
        index.last_reconciled = self.clock()

    def get(self, workspace_root: str) -> tuple[RepositoryIndex, bool]:
        index = self._entry(workspace_root)
        with index.lock:
            previous = index.fingerprint
            if not previous or not self._watching(index) or self.clock() - index.last_reconciled >= self.reconcile_seconds:
                self._scan(index)
            return index.snapshot(), bool(previous and previous == index.fingerprint)

    def synchronize(self, workspace_root: str, watcher: str, action: str,
                    paths: Iterable[str] = (), sequence: int | None = None) -> RepositoryIndex:
        if action not in {"start", "update", "reconcile", "stop"}:
            raise ValueError("Unknown index synchronization action")
        index = self._entry(workspace_root)
        with index.lock:
            watching = self._watching(index)
            previous = index.watcher_versions.get(watcher)
            if sequence is not None and previous and sequence <= previous[0]:
                return index.snapshot()
            if action == "stop":
                index.watchers.pop(watcher, None)
                if sequence is not None:
                    index.watcher_versions[watcher] = (sequence, self.clock() + self.lease_seconds)
                return index.snapshot()
            # Commit the lease only after a successful scan/update.
            if action == "start" or not index.fingerprint or not watching or self.clock() - index.last_reconciled >= self.reconcile_seconds:
                self._scan(index)
            if action == "update":
                index.apply_changes(paths)
            index.watchers[watcher] = self.clock() + self.lease_seconds
            if sequence is not None:
                index.watcher_versions[watcher] = (sequence, self.clock() + self.lease_seconds)
            return index.snapshot()

    def reconcile_watched(self) -> list[RepositoryIndex]:
        with self.lock:
            entries = list(self.entries.values())
        refreshed = []
        for index in entries:
            with index.lock:
                if self._watching(index) and self.clock() - index.last_reconciled >= self.reconcile_seconds:
                    try:
                        self._scan(index)
                        refreshed.append(index.snapshot())
                    except (OSError, ValueError) as exc:
                        logger.warning("Unable to reconcile %s: %s", index.workspace_root, exc)
        return refreshed
