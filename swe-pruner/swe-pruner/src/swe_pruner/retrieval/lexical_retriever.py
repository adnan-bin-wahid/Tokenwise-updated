import logging
import math
import re
from collections import Counter
from typing import List, Set
from ..repository.repository_index import RepositoryIndex

logger = logging.getLogger(__name__)

class LexicalRetriever:
    def __init__(self, index: RepositoryIndex):
        self.index = index

    def search_identifiers(self, identifiers: List[str]) -> Set[str]:
        """
        Scans class and function names in the AST index to find exact matches 
        with the specified list of identifiers.
        """
        matched_files = set()
        for rel_path, file_meta in self.index.index.items():
            for ident in identifiers:
                # Direct check on class definitions
                if ident in file_meta.get("classes", {}):
                    matched_files.add(rel_path)
                    logger.debug(f"Lexical match for class '{ident}' in {rel_path}")
                
                # Direct check on function definitions
                elif ident in file_meta.get("functions", {}):
                    matched_files.add(rel_path)
                    logger.debug(f"Lexical match for function '{ident}' in {rel_path}")
                    
        return matched_files

    @staticmethod
    def _terms(text: str) -> list[str]:
        text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
        words = re.findall(r"[a-z][a-z0-9]*", text.lower().replace("_", " "))
        return [
            word[:-3] + "y" if len(word) > 4 and word.endswith("ies") else
            word[:-1] if len(word) > 4 and word.endswith("s") and not word.endswith("ss") else word
            for word in words
        ]

    def search_query(self, query: str, limit: int = 8) -> list[tuple[str, float]]:
        """Discover files from ordinary task words as well as exact symbol names."""
        stop_words = {
            "a", "an", "the", "this", "that", "and", "or", "to", "of", "in", "on",
            "for", "with", "from", "my", "me", "please", "can", "could", "would",
            "how", "why", "what", "is", "are", "it", "be", "do", "does", "explain",
            "fix", "add", "change", "understand", "show", "code", "project", "logic",
            "its", "their", "we", "you", "your", "test", "tests", "testing",
        }
        terms = set(self._terms(query)) - stop_words
        if not terms:
            return []
        documents = {
            path: Counter(self._terms(meta.get("content", "")))
            for path, meta in self.index.index.items()
        }
        frequency = {term: sum(term in doc for doc in documents.values()) for term in terms}
        ranked = []
        for path, meta in self.index.index.items():
            path_terms = set(self._terms(path))
            symbols = " ".join(meta.get("classes", {})) + " " + " ".join(meta.get("functions", {}))
            symbols += " " + " ".join(
                method for cls in meta.get("classes", {}).values() for method in cls.get("methods", [])
            )
            symbol_terms = set(self._terms(symbols))
            score = 0.0
            for term in terms:
                weight = math.log(1 + len(documents) / (1 + frequency[term]))
                score += weight * (
                    5 * (term in path_terms) + 3 * (term in symbol_terms)
                    + min(documents[path][term], 4)
                )
            if score > 0:
                ranked.append((path, score))
        return sorted(ranked, key=lambda item: (-item[1], item[0]))[:limit]
