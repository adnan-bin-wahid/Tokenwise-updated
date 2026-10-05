import re
import logging
from typing import List, Optional, Set
from .goal_models import StructuredGoal
from .goal_generator_client import LocalGoalGeneratorClient
from .conversation_context import is_follow_up

logger = logging.getLogger(__name__)

INTENT_TEMPLATES = {
    "fix":      "Identify error handling paths, exception blocks, incorrect conditional "
                "logic, and off-by-one errors that may cause the reported issue: '{query}'",
    "optimize": "Locate performance-critical loops, redundant computations, unnecessary "
                "allocations, and cacheable operations related to: '{query}'",
    "add":      "Find insertion points, related interfaces, existing patterns, and "
                "dependency imports relevant to adding: '{query}'",
    "remove":   "Identify all references, usages, and dependent code blocks that would "
                "be affected by removing: '{query}'",
    "refactor": "Locate tightly coupled modules, duplicated logic, and abstraction "
                "boundaries relevant to refactoring: '{query}'",
    "test":     "Find testable functions, edge cases, boundary conditions, and mock "
                "points relevant to testing: '{query}'",
    "debug":    "Trace execution flow, variable mutations, state transitions, and "
                "side effects related to debugging: '{query}'",
    "understand": "Identify entry points, control flow, data structures, and key "
                  "abstractions to understand: '{query}'",
}

DEFAULT_TEMPLATE = (
    "Analyze the code to find sections most relevant to the following developer "
    "intent. Focus on function signatures, control flow, data dependencies, and "
    "error handling related to: '{query}'"
)


def is_repository_overview(query: str) -> bool:
    target = r"(?:project|repository|repo|codebase|application)\b"
    qualifiers = r"(?:(?:the|this|my|our|entire|whole|full|complete)\s+)*"
    patterns = (
        rf"\b(?:overview|architecture|structure|tour)\s+(?:of\s+)?{qualifiers}{target}",
        rf"\b{target}\s+(?:overview|architecture|structure)\b",
        rf"\b(?:explain|summari[sz]e|describe|understand)\s+{qualifiers}{target}"
        rf"(?=\s*(?:[.!?]|$|\bin\s+detail\b|\bto\s+me\b))",
        rf"\bhow\s+(?:does|do)\s+{qualifiers}{target}\s+(?:work|run)\b",
    )
    return any(re.search(pattern, query, re.IGNORECASE) for pattern in patterns)


class GoalCompiler:
    def __init__(self, generator_client: LocalGoalGeneratorClient):
        self.generator = generator_client

    def build_prompt(
        self, 
        query: str, 
        active_file: str, 
        current_symbol: Optional[str], 
        selected_code: Optional[str], 
        diagnostics: List[str]
    ) -> str:
        return f"""You are a task-aware context pruning goal compiler. 
Your job is to transform a developer's query and their active editor evidence into a structured Goal JSON object.

Editor Context:
- Active File: {active_file}
- Selected Code Segment:
{selected_code or '(none)'}
- Diagnostics/Errors:
{chr(10).join(diagnostics) if diagnostics else '(none)'}
- Active Symbol under cursor: {current_symbol or '(none)'}

Developer Query: "{query}"

Respond with ONLY a JSON object fitting this schema:
{{
    "task_type": "bug_fix | refactor | feature_addition | test_generation | repository_overview | generic_task",
    "objective": "A precise objective describing what part of the code needs to be inspected or edited, referencing files/symbols strictly from the context.",
    "identifiers": ["list", "of", "exact", "class", "or", "function", "names", "mentioned", "in", "the", "query", "selected_code", "or", "diagnostics"],
    "observed_errors": ["list", "of", "errors", "verbatim", "from", "diagnostics"],
    "required_context": ["imported", "modules", "or", "related", "file", "paths"],
    "retrieval_questions": ["questions", "to", "search", "the", "codebase", "index", "like", "'Where is class X defined?'", "'Which files call method Y?'"],
    "clarification_required": true/false
}}

CRITICAL SAFEGUARDS:
1. Do NOT invent/hallucinate class or function names that are not in the query, selected code, diagnostics, or active symbol.
2. If the user query is vague (e.g., "fix bug", "help", "optimize") and there is absolutely no editor evidence (no diagnostics, no selected code, no current symbol), set "clarification_required" to true.
"""

    async def compile(
        self, 
        query: str, 
        active_file: str, 
        current_symbol: Optional[str], 
        selected_code: Optional[str], 
        diagnostics: List[str],
        local_llm_url: Optional[str] = None,
        local_llm_model: Optional[str] = None,
        context_hint: Optional[str] = None,
    ) -> StructuredGoal:
        if is_repository_overview(query):
            return self.deterministic_fallback(query, current_symbol, diagnostics)
        # Check if query is extremely vague and no context evidence is present
        is_vague = not query or is_follow_up(query) or query.lower().strip() in {"fix bug", "fix", "bug", "help", "debug", "test", "run"}
        has_evidence = bool(current_symbol or selected_code or diagnostics or context_hint)
        
        if is_vague and not has_evidence:
            return StructuredGoal(
                task_type="generic_task",
                objective=f"Analyze repository for: '{query}'",
                identifiers=[],
                observed_errors=[],
                required_context=[],
                retrieval_questions=[],
                clarification_required=True
            )

        goal = None
        # Local goal synthesis is opt-in; otherwise use the deterministic compiler immediately.
        if self.generator and local_llm_url:
            goal = await self.generator.generate_goal(
                prompt=self.build_prompt(query, active_file, current_symbol, selected_code, diagnostics)
                + (f"\nEarlier user topic in this conversation (reference): {context_hint}" if context_hint else ""),
                endpoint_url=local_llm_url,
                model=local_llm_model
            )

        # Fallback if generation failed
        if not goal:
            logger.info("Local goal generation failed or client was disabled. Using deterministic fallback templates.")
            goal = self.deterministic_fallback(query, current_symbol, diagnostics)
        if context_hint:
            goal.objective += f"\nEarlier user topic in this conversation (reference): {context_hint}"

        # Post-process validation: Filter out hallucinated identifiers not in our workspace context
        # We build a vocabulary of valid words in context
        valid_words = set(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', query))
        if context_hint:
            valid_words.update(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', context_hint))
        if current_symbol:
            valid_words.add(current_symbol)
        if selected_code:
            valid_words.update(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', selected_code))
        for diag in diagnostics:
            valid_words.update(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', diag))
            
        goal.identifiers = [ident for ident in goal.identifiers if ident in valid_words]
        return goal

    def deterministic_fallback(self, query: str, current_symbol: Optional[str], diagnostics: List[str]) -> StructuredGoal:
        if is_repository_overview(query):
            return StructuredGoal(
                task_type="repository_overview",
                objective=("Explain the repository's purpose, entry points, core modules, data flow, "
                           "configuration, dependencies, and tests. Use project documentation and "
                           "representative source evidence; distinguish implemented behavior from "
                           f"package scaffolding. Developer request: '{query}'"),
                observed_errors=diagnostics,
                required_context=["project documentation", "entry points", "core modules", "tests"],
                retrieval_questions=["How is the application started?", "What are its main components?",
                                     "Which tests describe the implemented behavior?"],
            )
        query_lower = query.lower().strip()
        objective = DEFAULT_TEMPLATE.format(query=query)
        task_type = "generic_task"
        
        # Simple keyword classifier
        for keyword, template in INTENT_TEMPLATES.items():
            if query_lower.startswith(keyword) or f" {keyword} " in f" {query_lower} ":
                objective = template.format(query=query)
                task_type = "bug_fix" if keyword in {"fix", "debug"} else \
                            "refactor" if keyword == "refactor" else \
                            "feature_addition" if keyword == "add" else \
                            "test_generation" if keyword == "test" else "generic_task"
                break

        # Extract potential identifiers using regex from query/diagnostics
        potential_idents = []
        stop_words = {
            "fix", "bug", "optimize", "add", "remove", "refactor", "test", "debug", 
            "understand", "the", "to", "in", "on", "for", "code", "and", "or", "with", 
            "a", "an", "is", "are", "issue", "validate", "credentials",
            "give", "explain", "full", "overview", "project", "repository", "codebase",
            "please", "me", "my", "this", "whole", "entire", "complete"
        }
        for word in re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', query):
            if word.lower() not in stop_words and len(word) > 2:
                potential_idents.append(word)
        if current_symbol:
            potential_idents.append(current_symbol)

        return StructuredGoal(
            task_type=task_type,
            objective=objective,
            identifiers=list(dict.fromkeys(potential_idents)),
            observed_errors=diagnostics,
            required_context=[],
            retrieval_questions=[f"Where is '{ident}' used or defined?" for ident in potential_idents[:3]],
            clarification_required=False
        )
