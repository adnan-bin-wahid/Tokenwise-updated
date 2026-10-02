import logging
import os
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

    def build_index(self) -> None:
        if not self.workspace_root.is_dir():
            raise ValueError(f"Workspace does not exist: {self.workspace_root}")

        self.index.clear()
        exclude_dirs = {
            '.git', '.venv', 'venv', 'node_modules', '__pycache__', '.vscode', '.idea',
            'build', 'dist', 'carbon_artifacts', '.pytest_cache', '.mypy_cache',
        }

        for root, dirs, files in os.walk(self.workspace_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for filename in files:
                full_path = Path(root) / filename
                if full_path.suffix.lower() not in self.SUPPORTED_SUFFIXES:
                    continue
                try:
                    rel_path = full_path.relative_to(self.workspace_root).as_posix()
                    content = full_path.read_text(encoding='utf-8', errors='replace')
                    file_meta = self.indexer.index_file(full_path)
                    file_meta['content'] = content
                    self.index[rel_path] = file_meta
                except Exception as exc:
                    logger.warning('Unable to index %s: %s', full_path, exc)
