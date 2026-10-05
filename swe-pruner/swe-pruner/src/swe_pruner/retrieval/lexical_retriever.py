import logging
import math
import re
from collections import Counter
from typing import List, Set, TYPE_CHECKING
if TYPE_CHECKING:
    from ..repository.repository_index import RepositoryIndex

logger = logging.getLogger(__name__)


def terms(text: str) -> list[str]:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    words = re.findall(r"[a-z][a-z0-9]*", text.lower().replace("_", " "))
    return [
        word[:-3] + "y" if len(word) > 4 and word.endswith("ies") else
        word[:-1] if len(word) > 4 and word.endswith("s") and not word.endswith("ss") else word
        for word in words
    ]


def document_features(path: str, metadata: dict) -> dict:
    symbols = " ".join(metadata.get("classes", {})) + " " + " ".join(metadata.get("functions", {}))
    symbols += " " + " ".join(method for cls in metadata.get("classes", {}).values() for method in cls.get("methods", []))
    return {"content": Counter(terms(metadata.get("content", ""))),
            "path": frozenset(terms(path)), "symbols": frozenset(terms(symbols))}

class LexicalRetriever:
    def __init__(self, index: "RepositoryIndex"):
        self.index = index
        self.postings: dict[str, dict[str, int]] = {}
        self.frequency: Counter = Counter()
        self.symbol_files: dict[str, set[str]] = {}
        for path, metadata in index.index.items():
            feature = metadata.get("_lexical") or document_features(path, metadata)
            self.frequency.update(feature["content"].keys())
            for term in feature["content"].keys() | feature["path"] | feature["symbols"]:
                self.postings.setdefault(term, {})[path] = (5 * (term in feature["path"])
                    + 3 * (term in feature["symbols"]) + min(feature["content"][term], 4))
            for symbol in set(metadata.get("classes", {})) | set(metadata.get("functions", {})):
                self.symbol_files.setdefault(symbol, set()).add(path)

    def search_identifiers(self, identifiers: List[str]) -> Set[str]:
        """
        Scans class and function names in the AST index to find exact matches 
        with the specified list of identifiers.
        """
        return set().union(*(self.symbol_files.get(ident, set()) for ident in identifiers))

    @staticmethod
    def _terms(text: str) -> list[str]:
        return terms(text)

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
        scores: dict[str, float] = {}
        for term in sorted(terms):
            weight = math.log(1 + len(self.index.index) / (1 + self.frequency[term]))
            for path, relevance in self.postings.get(term, {}).items():
                scores[path] = scores.get(path, 0.0) + weight * relevance
        return sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:limit]
