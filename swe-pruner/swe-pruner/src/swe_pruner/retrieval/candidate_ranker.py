import logging
from typing import List, Tuple

import torch

from ..swepruner import SwePrunerForCodeCompression

logger = logging.getLogger(__name__)


class CandidateRanker:
    def __init__(self, pruner_model: SwePrunerForCodeCompression):
        self.model = pruner_model

    def rank_candidates(
        self, query: str, candidates: List[Tuple[str, str]]
    ) -> List[Tuple[str, float]]:
        """Return document-level relevance probabilities in the [0, 1] range."""
        if not self.model:
            return [(path, 0.0) for path, _ in candidates]

        self.model.eval()
        device = next(self.model.parameters()).device
        ranked: list[tuple[str, float]] = []

        prefix = (
            '<|im_start|>system\nJudge whether the Document meets the requirements based on '
            'the Query and the Instruct provided. Note that the answer can only be "yes" or "no".'
            '<|im_end|>\n<|im_start|>user\n'
        )
        suffix = '<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'

        for path, content in candidates:
            document = content[:12000]
            instruction = (
                '<Instruct>: Given a coding task, judge whether the code document is relevant\n'
                f'<Query>: {query}\n<Document>: {document}'
            )
            try:
                inputs = self.model.tokenizer(
                    prefix + instruction + suffix,
                    return_tensors='pt',
                    truncation=True,
                    max_length=4096,
                )
                with torch.no_grad():
                    outputs = self.model(
                        input_ids=inputs['input_ids'].to(device),
                        attention_mask=inputs['attention_mask'].to(device),
                    )
                    raw = outputs.score_logits[0].float().cpu()
                    if self.model.model.is_llm:
                        score = float(torch.exp(raw).item())
                    else:
                        score = float(torch.sigmoid(raw).item())
                ranked.append((path, max(0.0, min(1.0, score))))
            except Exception as exc:
                logger.exception('Failed to rank candidate %s: %s', path, exc)
                ranked.append((path, 0.0))

        return sorted(ranked, key=lambda item: item[1], reverse=True)
