"""Bounded project metadata and representative Python evidence for broad requests."""

import hashlib
from collections import Counter
from pathlib import Path

from ..repository.repository_index import RepositoryIndex


DOCUMENT_LIMIT = 64 * 1024
DOCUMENT_NAMES = (
    "README.md", "readme.md", "README.rst", "README.txt", "README", "readme.txt",
    "pyproject.toml", "setup.cfg", "requirements.txt", "package.json",
)
ENTRY_NAMES = {"app.py", "main.py", "__main__.py", "cli.py", "manage.py", "server.py", "wsgi.py", "asgi.py"}


def file_role(filename: str, metadata: dict) -> str:
    path = Path(filename)
    parts = {part.lower() for part in path.parts[:-1]}
    stem = path.stem.lower()
    if "tests" in parts or "test" in parts or stem.startswith("test_") or stem.endswith("_test"):
        return "tests"
    if path.name.lower() in ENTRY_NAMES or "main" in metadata.get("functions", {}):
        return "entry point"
    if parts & {"services", "service", "core", "application", "usecases"} or "service" in stem:
        return "core logic"
    if parts & {"api", "routes", "controllers", "views"}:
        return "API"
    if parts & {"models", "schemas", "types"} or "model" in stem:
        return "data model"
    if parts & {"repositories", "storage", "database", "db"}:
        return "storage"
    if parts & {"config", "settings"} or stem in {"settings", "config"}:
        return "configuration"
    if path.name == "__init__.py":
        return "package interface"
    if parts & {"utils", "utilities", "helpers"}:
        return "utility"
    return "core logic" if metadata.get("functions") or metadata.get("classes") else "module"


def load_project_documents(root: Path) -> tuple[dict, str, list[str]]:
    documents, warnings = {}, []
    has_readme = False
    for name in DOCUMENT_NAMES:
        if len(documents) >= 2:
            break
        is_readme = name.lower().startswith("readme")
        if is_readme and has_readme:
            continue
        filename = root / name
        try:
            filename.resolve().relative_to(root)
            if filename.is_symlink() or not filename.is_file():
                continue
            for _ in range(3):
                before = filename.stat()
                with filename.open("rb") as stream:
                    content_bytes = stream.read(DOCUMENT_LIMIT + 1)
                after = filename.stat()
                if (before.st_mtime_ns, before.st_size, before.st_ctime_ns) == (
                    after.st_mtime_ns, after.st_size, after.st_ctime_ns
                ):
                    break
            else:
                warnings.append(f"{name} changed while being read; omitted from this overview.")
                continue
            if len(content_bytes) > DOCUMENT_LIMIT:
                content_bytes = content_bytes[:DOCUMENT_LIMIT]
                warnings.append(f"{name}: only the first {DOCUMENT_LIMIT} bytes were inspected.")
            content = content_bytes.decode("utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\r", "\n").strip()
            if not content:
                continue
            documents[name] = {
                "content": content, "_overview_content": content,
                "_overview_relation": "project documentation" if is_readme else "project configuration",
                "_language": "markdown" if is_readme else "json" if name.endswith(".json") else "text",
                "_content_hash": hashlib.sha256(content_bytes).hexdigest(),
            }
            has_readme = has_readme or is_readme
        except (OSError, ValueError):
            continue
    fingerprint = hashlib.sha256(repr(sorted(
        (name, data["_content_hash"]) for name, data in documents.items()
    )).encode("utf-8")).hexdigest()
    return documents, fingerprint, warnings


def select_overview_files(index: RepositoryIndex, graph, limit: int) -> list[str]:
    groups = {}
    for name, metadata in index.index.items():
        groups.setdefault(file_role(name, metadata), []).append(name)
    for names in groups.values():
        names.sort(key=lambda name: (
            -len(graph.dependencies.get(name, set())) - len(graph.dependents.get(name, set())),
            -len(index.index[name].get("classes", {})) - len(index.index[name].get("functions", {})),
            len(Path(name).parts), name,
        ))
    order = ("entry point", "core logic", "tests", "data model", "API", "configuration", "storage",
             "utility", "module", "package interface")
    selected = []
    while len(selected) < limit:
        added = False
        for role in order:
            if groups.get(role):
                selected.append(groups[role].pop(0))
                added = True
                if len(selected) >= limit:
                    break
        if not added:
            break
    return selected


def overview_metadata(index: RepositoryIndex, documents: dict, selected: list[str]) -> dict:
    metadata = dict(documents)
    for name in selected:
        item = dict(index.index[name])
        # Small implementations stay intact; larger modules expose cached interfaces.
        item["_overview_content"] = item["content"] if len(item["content"]) <= 1600 else (
            item.get("_signature") or item["content"]
        )
        item["_overview_relation"] = f"project {file_role(name, item)}"
        metadata[name] = item
    return metadata


def repository_map(index: RepositoryIndex) -> str:
    groups = Counter(file_role(name, metadata) for name, metadata in index.index.items())
    counts = ", ".join(f"{role}: {count}" for role, count in sorted(groups.items()))
    paths = sorted(index.index)
    listed = paths[:24]
    listing = "\n".join(listed)
    if len(paths) > len(listed):
        listing += f"\n... {len(paths) - len(listed)} more indexed Python files"
    return f"Components: {counts}\nPython file map:\n{listing}"
