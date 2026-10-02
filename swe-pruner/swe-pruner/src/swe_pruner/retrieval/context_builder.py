import logging
import ast
import copy
from typing import Any, Dict, List, Tuple

from ..prune_wrapper import PruneRequest, estimate_token_count

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Build a bounded, tiered repository context for downstream coding agents."""

    def __init__(self, token_budget: int = 8192):
        if token_budget < 256:
            raise ValueError("token_budget must be at least 256 tokens")
        self.token_budget = token_budget

    @staticmethod
    def _signatures_only(file_meta: Dict[str, Any], rel_path: str) -> str:
        content = file_meta.get("content", "")
        if content:
            try:
                tree = ast.parse(content)
                interface = []
                for node in tree.body:
                    if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign)):
                        interface.append(node)
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        stub = copy.copy(node)
                        stub.body = [ast.Expr(value=ast.Constant(value=Ellipsis))]
                        interface.append(stub)
                    elif isinstance(node, ast.ClassDef):
                        stub = copy.copy(node)
                        stub.body = []
                        for child in node.body:
                            if isinstance(child, (ast.Assign, ast.AnnAssign)):
                                stub.body.append(child)
                            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                method = copy.copy(child)
                                method.body = [ast.Expr(value=ast.Constant(value=Ellipsis))]
                                stub.body.append(method)
                        if not stub.body:
                            stub.body = [ast.Expr(value=ast.Constant(value=Ellipsis))]
                        interface.append(stub)
                if interface:
                    return ast.unparse(ast.Module(body=interface, type_ignores=[]))
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

        for rel_path in ordered_paths:
            file_meta = files_metadata[rel_path]
            content = file_meta.get("content", "")
            if not content:
                continue

            score = score_map.get(rel_path, 0.0)
            distance = graph_distances.get(rel_path)
            if rel_path == active_file:
                tier = 1
                relation = "active file"
            elif (prepruned and rel_path in prepruned) or distance == 1 or score >= 0.35:
                tier = 2
                relation = "direct/relevant dependency"
            else:
                tier = 3
                relation = "transitive reference"

            if not prune_uncached and rel_path not in (prepruned or {}):
                tier = 3
                relation = "dependency interface"

            if "test" in rel_path.lower():
                relation = "related test"

            original_tokens = self._count(content, tokenizer)
            if prepruned and rel_path in prepruned:
                result = prepruned[rel_path]
                pruned_content = result.pruned_code
                original_tokens = result.origin_token_cnt
            elif tier == 1:
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
                    logger.warning("Tier-1 pruning failed for %s: %s", rel_path, exc)
                    pruned_content = content
            elif tier == 2:
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
                    logger.warning("Tier-2 pruning failed for %s: %s", rel_path, exc)
                    pruned_content = self._signatures_only(file_meta, rel_path)
            else:
                pruned_content = self._signatures_only(file_meta, rel_path)

            header = (
                f"### {rel_path}\n"
                f"# Relation: {relation}\n"
                f"# Tier: {tier}\n"
                "```python\n"
            )
            footer = "\n```"
            prefix = "\n\n".join(([preamble] if preamble else []) + output_blocks)
            remaining = self.token_budget - self._count(prefix + ("\n\n" if prefix else ""), tokenizer)
            if remaining <= 0:
                break

            overhead = self._count(header + footer, tokenizer)
            if overhead >= remaining:
                break

            content_budget = remaining - overhead
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

            pruned_tokens = self._count(pruned_content, tokenizer)
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
                }
            )

            if used_tokens >= self.token_budget:
                break

        packed = "\n\n".join(([preamble] if preamble else []) + output_blocks)
        return packed, summaries, self._count(packed, tokenizer)
