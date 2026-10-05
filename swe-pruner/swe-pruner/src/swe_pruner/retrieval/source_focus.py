"""Omit independently excluded Python units from query-specific reference views."""

import ast
import copy
from pathlib import Path

from ..query_focus import QueryFocus
from ..repository.python_indexer import PythonASTIndexer
from .lexical_retriever import terms


UNITS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
TASK_WORDS = set(terms("explain describe understand show find fix add remove refactor debug "
                      "test tests testing code class function method behavior logic context "
                      "project repository this that the and or not of to in on for with from "
                      "my me its their please can could would how why what is are it be do does"))


def _names(node, omitted: set[int], descend_units: bool = False) -> set[str]:
    names: set[str] = set()

    def visit(item):
        if id(item) in omitted or (item is not node and isinstance(item, UNITS) and not descend_units):
            return
        if isinstance(item, (ast.Name, ast.Attribute)):
            names.add(item.id if isinstance(item, ast.Name) else item.attr)
        elif isinstance(item, UNITS):
            names.add(item.name)
        elif isinstance(item, ast.arg):
            names.add(item.arg)
        for child in ast.iter_child_nodes(item):
            visit(child)

    visit(node)
    return names


def _span(node, lines: list[str]) -> tuple[int, int] | None:
    start = min([node.lineno] + [decorator.lineno for decorator in getattr(node, "decorator_list", ())]) - 1
    end = node.end_lineno
    # AST columns are byte offsets. Never remove another statement sharing a line.
    prefix = lines[start].encode("utf-8")[:node.col_offset].strip()
    suffix = lines[end - 1].encode("utf-8")[node.end_col_offset:].strip()
    if prefix or (suffix and not suffix.startswith(b"#")):
        return None
    return start, end


def focus_sources(metadata: dict[str, dict], focus: QueryFocus) -> tuple[dict[str, dict], list[str]]:
    if not focus.excluded_topics:
        return metadata, []
    positive = set(terms(focus.positive_query)) - TASK_WORDS
    negative = set(terms(" ".join(focus.excluded_topics))) - TASK_WORDS
    if not positive or not negative:
        return metadata, []

    trees, lines, units = {}, {}, {}
    omitted: set[int] = set()
    candidates: set[int] = set()
    roots: set[int] = set()
    by_name: dict[str, list] = {}
    for path, item in metadata.items():
        if "_focus_tree" not in item:
            try:
                item["_focus_tree"] = ast.parse(item["content"])
            except (SyntaxError, ValueError):
                item["_focus_tree"] = None
        tree = item["_focus_tree"]
        if tree is None:
            continue
        trees[path], lines[path] = tree, item["content"].splitlines(keepends=True)
        units[path] = [node for node in ast.walk(tree) if isinstance(node, UNITS)]
        for node in ast.walk(tree):
            # Independent display statements can omit the other topic; never discard
            # assignments, conditions, returns, or side-effect calls on this basis.
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) \
                    and isinstance(node.value.func, ast.Name) and node.value.func.id == "print":
                words = set(terms(" ".join(_names(node, set()))))
                if words & negative and not words & positive and _span(node, lines[path]):
                    omitted.add(id(node))
        for node in units[path]:
            by_name.setdefault(node.name, []).append(node)

    references = {}
    for path, nodes in units.items():
        aliases = {alias.asname: alias.name for node in ast.walk(trees[path]) if isinstance(node, ast.ImportFrom)
                   for alias in node.names if alias.asname}
        for node in nodes:
            names = _names(node, omitted)
            references[id(node)] = (names | {aliases[name] for name in names if name in aliases}) - {node.name}
            words = set(terms(" ".join(names)))
            all_words = set(terms(" ".join(_names(node, omitted, descend_units=True))))
            if words & positive:
                roots.add(id(node))
            if all_words & negative and not all_words & positive and _span(node, lines[path]):
                candidates.add(id(node))
        for node in trees[path].body:
            if isinstance(node, (*UNITS, ast.Import, ast.ImportFrom)):
                continue
            names = _names(node, omitted)
            if set(terms(" ".join(names))) & positive:
                roots.add(id(node))
                references[id(node)] = names | {aliases[name] for name in names if name in aliases}

    # Protect helpers used by the positive topic, including cross-file dependencies.
    required = set(roots)
    pending = list(roots)
    while pending:
        for name in references.get(pending.pop(), ()):
            for dependency in by_name.get(name, ()):
                if id(dependency) not in required:
                    required.add(id(dependency))
                    pending.append(id(dependency))
    for nodes in units.values():
        for node in nodes:
            if isinstance(node, ast.ClassDef) and any(id(child) in required for child in ast.walk(node)):
                required.add(id(node))
    removable = candidates - required
    output = dict(metadata)
    warnings: list[str] = []
    for path, tree in trees.items():
        edits: dict[int, str] = {}
        removed: list[str] = []
        protected = sorted(node.name for node in units[path] if id(node) in candidates & required)
        if protected:
            warnings.append(f"{path}: kept excluded-topic helpers needed by the requested topic: {', '.join(protected)}.")
        for node in ast.walk(tree):
            if id(node) not in removable | omitted:
                continue
            span = _span(node, lines[path])
            if span:
                edits.update((line, "") for line in range(*span))
                removed.append(node.name if isinstance(node, UNITS) else "excluded-topic display statement")
        if not edits:
            continue
        for node in units[path]:
            if id(node) not in removable and node.body and all(child.lineno - 1 in edits for child in node.body):
                edits[node.body[0].lineno - 1] = " " * node.body[0].col_offset + "pass\n"
        remaining = "".join(edits.get(line, text) for line, text in enumerate(lines[path]))
        try:
            remaining_tree = ast.parse(remaining)
            used = {node.id for node in ast.walk(remaining_tree) if isinstance(node, ast.Name)}
            for node in tree.body:
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue
                aliases = [alias for alias in node.names if not (set(terms(alias.name)) & negative)
                           or (alias.asname or alias.name.split(".")[0]) in used]
                if aliases == node.names:
                    continue
                span = _span(node, lines[path])
                if span:
                    replacement = copy.copy(node)
                    replacement.names = aliases
                    edits.update((line, "") for line in range(*span))
                    edits[span[0]] = ast.unparse(replacement) + "\n" if aliases else ""
            remaining = "".join(edits.get(line, text) for line, text in enumerate(lines[path]))
            final_tree = ast.parse(remaining)
        except (SyntaxError, ValueError):
            warnings.append(f"{path}: could not safely isolate excluded units; retained original reference source.")
            continue
        if all(isinstance(node, (ast.Import, ast.ImportFrom)) or
               (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str))
               for node in final_tree.body):
            output.pop(path)
            continue
        output[path] = {**PythonASTIndexer().index_file(Path(path), remaining), "content": remaining,
                        "_scope_removed": sorted(set(removed))}
    return output, warnings
