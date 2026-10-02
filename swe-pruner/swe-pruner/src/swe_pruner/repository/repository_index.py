import logging
import os
import hashlib
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict

from .python_indexer import PythonASTIndexer

logger = logging.getLogger(__name__)


class RepositoryIndex:
    """Python repository index used by TokenWise repository-context mode."""

    SUPPORTED_SUFFIXES = {".py"}

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root).resolve()
        self.indexer = PythonASTIndexer()
        self.index: Dict[str, Any] = {}
        self.file_versions: dict[str, tuple[int, int]] = {}
        self.fingerprint = ""

    def build_index(self) -> None:
        if not self.workspace_root.is_dir():
            raise ValueError(f"Workspace does not exist: {self.workspace_root}")

        updated_index: Dict[str, Any] = {}
        updated_versions: dict[str, tuple[int, int]] = {}
        exclude_dirs = {
            '.git', '.venv', 'venv', 'node_modules', '__pycache__', '.vscode', '.idea',
            'build', 'dist', 'carbon_artifacts', '.pytest_cache', '.mypy_cache',
            '.agents', '.agent', '.tokenwise',
        }

        for root, dirs, files in os.walk(self.workspace_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for filename in files:
                full_path = Path(root) / filename
                if full_path.suffix.lower() not in self.SUPPORTED_SUFFIXES:
                    continue
                try:
                    full_path.resolve().relative_to(self.workspace_root)
                    rel_path = full_path.relative_to(self.workspace_root).as_posix()
                    stat = full_path.stat()
                    version = (stat.st_mtime_ns, stat.st_size)
                    if self.file_versions.get(rel_path) == version and rel_path in self.index:
                        updated_index[rel_path] = self.index[rel_path]
                        updated_versions[rel_path] = version
                        continue
                    content = full_path.read_text(encoding='utf-8', errors='replace')
                    file_meta = self.indexer.index_file(full_path)
                    file_meta['content'] = content
                    updated_index[rel_path] = file_meta
                    updated_versions[rel_path] = version
                except Exception as exc:
                    logger.warning('Unable to index %s: %s', full_path, exc)

        self.index = updated_index
        self.file_versions = updated_versions
        version_text = repr(sorted(updated_versions.items())).encode("utf-8")
        self.fingerprint = hashlib.sha256(version_text).hexdigest()


class RepositoryIndexCache:
    """Reuse unchanged ASTs while checking additions, edits and deletions each request."""

    def __init__(self, capacity: int = 8):
        self.capacity = capacity
        self.entries: OrderedDict[str, RepositoryIndex] = OrderedDict()
        self.lock = threading.Lock()

    def get(self, workspace_root: str) -> tuple[RepositoryIndex, bool]:
        key = str(Path(workspace_root).resolve())
        with self.lock:
            index = self.entries.pop(key, None) or RepositoryIndex(key)
            previous = index.fingerprint
            index.build_index()
            self.entries[key] = index
            while len(self.entries) > self.capacity:
                self.entries.popitem(last=False)
            # A snapshot keeps an in-flight request independent of subsequent refreshes.
            snapshot = RepositoryIndex(key)
            snapshot.index = index.index.copy()
            snapshot.fingerprint = index.fingerprint
            return snapshot, bool(previous and previous == index.fingerprint)
