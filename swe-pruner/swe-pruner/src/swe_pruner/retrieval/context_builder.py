import logging
import ast
import re
from collections import OrderedDict
from typing import Any, Dict, List, Tuple

from ..prune_wrapper import PruneRequest, estimate_token_count
from ..repository.python_indexer import build_interface

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Build a bounded, tiered repository context for downstream coding agents."""

    def __init__(self, token_budget: int = 8192):
        if token_budget < 256:
            raise ValueError("token_budget must be at least 256 tokens")
        self.token_budget = token_budget

    @staticmethod
    def _signatures_only(file_meta: Dict[str, Any], rel_path: str) -> str:
        if isinstance(file_meta.get("_signature"), str):
            return file_meta["_signature"]
        content = "" if "_signature" in file_meta else file_meta.get("content", "")
        if content:
            try:
                reference = build_interface(ast.parse(content))
                if reference:
                    return reference
            except (SyntaxError, ValueError):
                pass
        signatures: list[str] = []
        for class_name, cls_info in file_meta.get("classes", {}).items():
            signatures.append(f"class {class_name}:")
            for method in cls_info.get("methods", []):
                signatures.append(f"    def {method}(self, ...): ...")
        for func_name in file_meta.get("functions", {}):
            signatures.append(f"def {func_name}(...): ...")
        return "\n".join(signatures) if signatures else f"# Module {rel_path} interface reference"

    @staticmethod
    def _count(text: str, tokenizer: Any) -> int:
        if tokenizer is not None:
            return estimate_token_count(text, tokenizer)
        return len(text.split())

    @classmethod
    def _file_count(cls, metadata: dict, text: str, tokenizer: Any) -> int:
        cache = metadata.setdefault("_token_counts", OrderedDict())
        key = (id(tokenizer), text)
        cached = cache.get(key)
        if cached is not None and cached[0] is tokenizer:
            cache.move_to_end(key)
            return cached[1]
        count = cls._count(text, tokenizer)
        cache[key] = (tokenizer, count)
        while len(cache) > 8:
            cache.popitem(last=False)
        return count

    @staticmethod
    def _truncate(text: str, token_limit: int, tokenizer: Any) -> str:
        if token_limit <= 0:
            return ""
        marker = "\n# [TokenWise truncated to repository token budget]"
        if tokenizer is None:
            words = text.split()
            if len(words) <= token_limit:
                return text
            if token_limit <= len(marker.split()):
                return " ".join(words[:token_limit])
            clipped = " ".join(words[: max(0, token_limit - 8)])
            return clipped + marker

        ids = tokenizer.encode(text, add_special_tokens=False)
        if len(ids) <= token_limit:
            return text
        marker_ids = tokenizer.encode(marker, add_special_tokens=False)
        if token_limit <= len(marker_ids):
            return tokenizer.decode(ids[:token_limit], skip_special_tokens=False)
        keep = max(0, token_limit - len(marker_ids))
        return tokenizer.decode(ids[:keep], skip_special_tokens=False) + marker

    @staticmethod
    def block_parts(rel_path: str, metadata: dict, relation: str, tier: int) -> tuple[str, str]:
        runs = re.findall(r"`{3,}", metadata.get("content", ""))
        fence = "`" * max(3, max((len(run) + 1 for run in runs), default=3))
        language = metadata.get("_language", "python")
        return (f"### {rel_path}\n# Relation: {relation}\n# Tier: {tier}\n{fence}{language}\n",
                f"\n{fence}")

    def pack_context(
        self,
        query: str,
        files_metadata: Dict[str, Dict[str, Any]],
        graph_distances: Dict[str, int],
        ranked_scores: List[Tuple[str, float]],
        pruner_model: Any,
        threshold: float = 0.45,
        active_file: str | None = None,
        preamble: str = "",
        prepruned: Dict[str, Any] | None = None,
        prune_uncached: bool = True,
        overview: bool = False,
        anchor_relation: str | None = None,
        preserve_source: set[str] | None = None,
    ) -> Tuple[str, List[Dict[str, Any]], int]:
        """
        Build the final repository context within ``self.token_budget``.

        Tier 1: active file, lightly pruned.
        Tier 2: direct graph dependency or high-relevance candidate, more aggressively pruned.
        Tier 3: transitive/low-relevance candidate, signatures only.
        """
        tokenizer = getattr(pruner_model, "tokenizer", None)
        score_map = {path: max(0.0, min(1.0, float(score))) for path, score in ranked_scores}

        ordered_paths: list[str] = []
        if active_file and active_file in files_metadata and active_file in score_map:
            ordered_paths.append(active_file)
        ordered_paths.extend(
            path
            for path, _ in sorted(ranked_scores, key=lambda item: item[1], reverse=True)
            if path in files_metadata and path not in ordered_paths
        )

        output_blocks: list[str] = []
        summaries: list[dict[str, Any]] = []
        used_tokens = self._count(preamble, tokenizer)

        for position, rel_path in enumerate(ordered_paths):
            file_meta = files_metadata[rel_path]
            content = file_meta.get("content", "")
            if not content:
                continue

            score = score_map.get(rel_path, 0.0)
            distance = graph_distances.get(rel_path)
            if rel_path == active_file:
                tier = 1
                relation = anchor_relation or "active file"
            elif (prepruned and rel_path in prepruned) or distance == 1 or score >= 0.35:
                tier = 2
                relation = "direct/relevant dependency"
            else:
                tier = 3
                relation = "transitive reference"

            if preserve_source and rel_path in preserve_source and rel_path not in (prepruned or {}):
                tier = 2
                relation = "small task-matched source"
            elif not prune_uncached and rel_path not in (prepruned or {}):
                tier = 3
                relation = "dependency interface"

            if "test" in rel_path.lower():
                relation = "related test"
            if overview:
                relation = file_meta.get("_overview_relation", "project module")

            original_tokens = (prepruned[rel_path].origin_token_cnt if prepruned and rel_path in prepruned
                               else self._file_count(file_meta, content, tokenizer))
            pruning_method = "signature_interface"
            effective_threshold = None
            if overview:
                pruning_method = "overview_excerpt"
                pruned_content = file_meta.get("_overview_content") or self._signatures_only(file_meta, rel_path)
            elif prepruned and rel_path in prepruned:
                pruning_method = "neural_lines"
                effective_threshold = max(0.10, threshold - 0.15) if rel_path == active_file else min(0.85, threshold + 0.15)
                result = prepruned[rel_path]
                pruned_content = result.pruned_code
                original_tokens = result.origin_token_cnt
            elif preserve_source and rel_path in preserve_source:
                pruning_method = "short_source_retained"
                pruned_content = content
            elif tier == 1:
                pruning_method = "neural_lines"
                effective_threshold = max(0.10, threshold - 0.15)
                try:
                    result = pruner_model.prune(
                        PruneRequest(
                            query=query,
                            code=content,
                            threshold=max(0.10, threshold - 0.15),
                            always_keep_first_frags=True,
                        )
                    )
                    pruned_content = result.pruned_code
                    original_tokens = result.origin_token_cnt
                except Exception as exc:
                    pruning_method = "original_source_fallback"
                    effective_threshold = None
                    logger.warning("Tier-1 pruning failed for %s: %s", rel_path, exc)
                    pruned_content = content
            elif tier == 2:
                pruning_method = "neural_lines"
                effective_threshold = min(0.85, threshold + 0.15)
                try:
                    result = pruner_model.prune(
                        PruneRequest(
                            query=query,
                            code=content,
                            threshold=min(0.85, threshold + 0.15),
                            always_keep_first_frags=True,
                        )
                    )
                    pruned_content = result.pruned_code
                    original_tokens = result.origin_token_cnt
                except Exception as exc:
                    pruning_method = "signature_fallback"
                    effective_threshold = None
                    logger.warning("Tier-2 pruning failed for %s: %s", rel_path, exc)
                    pruned_content = self._signatures_only(file_meta, rel_path)
            else:
                pruned_content = self._signatures_only(file_meta, rel_path)

            header, footer = self.block_parts(rel_path, file_meta, relation, tier)
            prefix = "\n\n".join(([preamble] if preamble else []) + output_blocks)
            remaining = self.token_budget - self._count(prefix + ("\n\n" if prefix else ""), tokenizer)
            if remaining <= 0:
                break

            overhead = self._count(header + footer, tokenizer)
            if overhead >= remaining:
                break

            content_budget = remaining - overhead
            if overview:
                # Reserve a fair share for later components rather than filling the budget with README.
                remaining_files = len(ordered_paths) - position
                content_budget = min(content_budget, max(1, remaining // remaining_files - overhead))
            pruned_content = self._truncate(pruned_content, content_budget, tokenizer)
            block = f"{header}{pruned_content}{footer}"
            block_tokens = self._count(block, tokenizer)

            # Tokenizer decode can introduce a tiny discrepancy; tighten once if necessary.
            if block_tokens > remaining:
                delta = block_tokens - remaining
                pruned_content = self._truncate(
                    pruned_content,
                    max(1, self._count(pruned_content, tokenizer) - delta - 4),
                    tokenizer,
                )
                block = f"{header}{pruned_content}{footer}"
                block_tokens = self._count(block, tokenizer)

            combined = "\n\n".join(([preamble] if preamble else []) + output_blocks + [block])
            if self._count(combined, tokenizer) > self.token_budget:
                break

            pruned_tokens = self._file_count(file_meta, pruned_content, tokenizer)
            output_blocks.append(block)
            used_tokens = self._count(combined, tokenizer)
            summaries.append(
                {
                    "file_path": rel_path,
                    "relation": relation,
                    "tier": tier,
                    "original_tokens": original_tokens,
                    "pruned_tokens": pruned_tokens,
                    "score": score,
                    "pruning_method": pruning_method,
                    "effective_threshold": effective_threshold,
                }
            )

            if used_tokens >= self.token_budget:
                break

        packed = "\n\n".join(([preamble] if preamble else []) + output_blocks)
        return packed, summaries, self._count(packed, tokenizer)
