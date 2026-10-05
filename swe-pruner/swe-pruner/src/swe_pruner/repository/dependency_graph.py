import logging
from typing import Dict, Set, List
from .repository_index import RepositoryIndex

logger = logging.getLogger(__name__)

class DependencyGraph:
    def __init__(self, repo_index: RepositoryIndex):
        self.repo_index = repo_index
        # Adjacency list: maps file_path to set of imported/dependent file_paths
        self.dependencies: Dict[str, Set[str]] = {}
        # Reverse mapping: maps file_path to set of files that import/depend on it
        self.dependents: Dict[str, Set[str]] = {}
        # Maps symbol name to list of file paths defining it
        self.symbol_definitions: Dict[str, List[str]] = {}

    def build_graph(self):
        """
        Builds the import/call dependency graph using the RepositoryIndex.
        """
        logger.info("Building dependency graph...")
        self.dependencies.clear()
        self.dependents.clear()
        self.symbol_definitions.clear()
        modules: Dict[str, Set[str]] = {}

        # Initialize collections
        for rel_path in self.repo_index.index:
            self.dependencies[rel_path] = set()
            self.dependents[rel_path] = set()
            parts = rel_path.replace('.py', '').split('/')
            for offset in range(len(parts)):
                modules.setdefault('.'.join(parts[offset:]), set()).add(rel_path)
            
            # Map symbol definitions
            file_meta = self.repo_index.index[rel_path]
            for class_name in file_meta.get("classes", {}):
                self.symbol_definitions.setdefault(class_name, []).append(rel_path)
            for func_name in file_meta.get("functions", {}):
                self.symbol_definitions.setdefault(func_name, []).append(rel_path)

        # Resolve dependency edges (imports and function/method calls)
        for rel_path, file_meta in self.repo_index.index.items():
            # 1. Resolve direct imports
            for imp in file_meta.get("imports", []):
                # Try matching import name to repository files
                # e.g., if import is 'auth.service', matching path might be 'auth/service.py'
                for target_path in modules.get(imp, ()):
                    self._add_edge(rel_path, target_path)

            # 2. Resolve calls to global/class symbols defined elsewhere in the repo
            for call_symbol in file_meta.get("calls", []):
                if call_symbol in self.symbol_definitions:
                    for target_path in self.symbol_definitions[call_symbol]:
                        if target_path != rel_path:
                            self._add_edge(rel_path, target_path)

        logger.info("Dependency graph built successfully.")

    def _add_edge(self, source: str, target: str):
        if source in self.dependencies:
            self.dependencies[source].add(target)
        if target in self.dependents:
            self.dependents[target].add(source)
