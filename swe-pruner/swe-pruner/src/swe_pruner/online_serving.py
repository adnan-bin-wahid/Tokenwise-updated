import os

# Keep CPU execution deterministic and avoid oversubscription in the local API process.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import asyncio
import logging
import re
from pathlib import Path
from typing import List, Optional

import torch
import typer
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .carbon_estimator import CarbonEstimateRequest, CarbonEstimateResponse, CarbonEstimator
from .goal_compiler import GoalCompiler
from .goal_generator_client import LocalGoalGeneratorClient
from .prune_wrapper import PruneRequest, PruneResponse, SwePrunerForCodePruning
from .repository.dependency_graph import DependencyGraph
from .repository.repository_index import RepositoryIndex
from .retrieval.candidate_ranker import CandidateRanker
from .retrieval.context_builder import ContextBuilder
from .retrieval.graph_retriever import GraphRetriever
from .retrieval.lexical_retriever import LexicalRetriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
torch.set_num_threads(1)

RUNTIME_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = RUNTIME_ROOT / "model"

app = FastAPI(title="TokenWise Backend", version="1.0.0")
cli = typer.Typer(help="TokenWise code-pruning service")

model: Optional[SwePrunerForCodePruning] = None
try:
    carbon_estimator: Optional[CarbonEstimator] = CarbonEstimator()
except Exception as exc:  # startup should still expose health diagnostics
    logger.error("Carbon estimator could not be initialized: %s", exc)
    carbon_estimator = None

generator_client = LocalGoalGeneratorClient()
goal_compiler = GoalCompiler(generator_client)


class WorkspacePruneRequest(BaseModel):
    query: str = Field(min_length=1)
    workspace_root: str
    active_file: str
    language: str
    current_symbol: Optional[str] = None
    selected_code: Optional[str] = None
    diagnostics: List[str] = Field(default_factory=list)
    threshold: float = Field(default=0.45, ge=0.0, le=1.0)
    local_llm_url: Optional[str] = None
    local_llm_model: Optional[str] = None
    token_budget: int = Field(default=8192, ge=256, le=32768)


class WorkspacePruneResponse(BaseModel):
    structured_goal: dict
    unified_prompt: str
    pruned_tokens: int
    original_tokens: int
    files: List[dict]


def resolve_model_path() -> Path:
    configured = os.getenv("SWEPRUNER_MODEL_PATH")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_MODEL_PATH.resolve()


def check_model_path(model_path: str | Path) -> bool:
    model_dir = Path(model_path)
    required = (
        "config.json",
        "model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
        "backbone/config.json",
    )
    return model_dir.is_dir() and all((model_dir / filename).is_file() for filename in required)


@app.on_event("startup")
async def startup_event() -> None:
    global model
    model_path = resolve_model_path()
    if not check_model_path(model_path):
        logger.warning(
            "Pruner model is incomplete at %s. /prune and /prune-workspace are disabled until model.safetensors is added.",
            model_path,
        )
        model = None
        return

    try:
        model = SwePrunerForCodePruning.from_pretrained(str(model_path), local_files_only=True)
        logger.info("Pruner model loaded from %s on %s", model_path, next(model.parameters()).device)
    except Exception as exc:
        logger.exception("Failed to load pruning model: %s", exc)
        model = None


@app.get("/health")
async def health_check():
    device = None
    if model is not None:
        try:
            device = str(next(model.parameters()).device)
        except StopIteration:
            device = "unknown"
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "carbon_models_loaded": bool(carbon_estimator and carbon_estimator.is_ready()),
        "device": device,
        "model_path": str(resolve_model_path()),
    }


@app.post("/prune", response_model=PruneResponse)
async def prune_code(request: PruneRequest) -> PruneResponse:
    if model is None:
        raise HTTPException(status_code=503, detail="Pruner model is not loaded")
    return await asyncio.to_thread(model.prune, request)


@app.post("/prune-workspace", response_model=WorkspacePruneResponse)
async def prune_workspace(request: WorkspacePruneRequest) -> WorkspacePruneResponse:
    if model is None:
        raise HTTPException(status_code=503, detail="Pruner model is not loaded")
    if request.language.lower() not in {"python", "py"}:
        raise HTTPException(
            status_code=400,
            detail="Repository-context mode currently supports Python source files only.",
        )

    workspace_root = Path(request.workspace_root).expanduser().resolve()
    active_file = Path(request.active_file).expanduser().resolve()
    if not workspace_root.is_dir():
        raise HTTPException(status_code=400, detail="Workspace root does not exist")
    try:
        active_rel_path = active_file.relative_to(workspace_root).as_posix()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Active file must be inside the workspace") from exc

    repo_index = RepositoryIndex(str(workspace_root))
    await asyncio.to_thread(repo_index.build_index)
    if active_rel_path not in repo_index.index:
        raise HTTPException(status_code=400, detail="Active file is not an indexed Python file")

    goal = await goal_compiler.compile(
        query=request.query.strip(),
        active_file=active_rel_path,
        current_symbol=request.current_symbol,
        selected_code=request.selected_code,
        diagnostics=request.diagnostics,
        local_llm_url=request.local_llm_url,
        local_llm_model=request.local_llm_model,
    )

    dep_graph = DependencyGraph(repo_index)
    await asyncio.to_thread(dep_graph.build_graph)
    graph_retriever = GraphRetriever(dep_graph)

    lexical_seeds = LexicalRetriever(repo_index).search_identifiers(goal.identifiers)
    discovery_seeds = set(lexical_seeds)
    discovery_seeds.add(active_rel_path)
    candidate_distances = graph_retriever.get_neighbors(discovery_seeds, max_hops=2)
    active_distances = graph_retriever.get_neighbors({active_rel_path}, max_hops=2)

    candidates: list[tuple[str, str]] = []
    for path in candidate_distances:
        meta = repo_index.index.get(path)
        if meta is not None:
            candidates.append((path, meta.get("content", "")))

    python_keywords = {
        "def", "class", "import", "from", "as", "return", "if", "else", "elif",
        "try", "except", "finally", "for", "while", "in", "is", "not", "and", "or",
        "with", "pass", "break", "continue", "lambda", "global", "nonlocal", "assert",
        "del", "yield", "raise", "True", "False", "None", "self", "str", "int", "float",
        "list", "dict", "set", "tuple", "bool", "type", "print", "len", "range",
    }
    goal_identifiers = {ident for ident in goal.identifiers if ident not in python_keywords}

    rank_candidates: list[tuple[str, str]] = []
    unranked_scores: list[tuple[str, float]] = []
    for path, content in candidates:
        has_identifier = any(
            re.search(r"\b" + re.escape(identifier) + r"\b", content)
            for identifier in goal_identifiers
        )
        if path == active_rel_path or path in lexical_seeds or has_identifier:
            rank_candidates.append((path, content))
        else:
            unranked_scores.append((path, 0.0))

    ranker = CandidateRanker(model)
    ranked_scores = await asyncio.to_thread(
        ranker.rank_candidates, goal.objective, rank_candidates
    )
    ranked_scores.extend(unranked_scores)
    ranked_scores.sort(key=lambda item: item[1], reverse=True)

    builder = ContextBuilder(token_budget=request.token_budget)
    unified_prompt, file_summaries, packed_tokens = await asyncio.to_thread(
        builder.pack_context,
        goal.objective,
        repo_index.index,
        active_distances,
        ranked_scores,
        model,
        request.threshold,
        active_rel_path,
    )

    return WorkspacePruneResponse(
        structured_goal=goal.model_dump(),
        unified_prompt=unified_prompt,
        pruned_tokens=packed_tokens,
        original_tokens=sum(item["original_tokens"] for item in file_summaries),
        files=file_summaries,
    )


@app.post("/estimate-carbon", response_model=CarbonEstimateResponse)
async def estimate_carbon(request: CarbonEstimateRequest) -> CarbonEstimateResponse:
    if carbon_estimator is None or not carbon_estimator.is_ready():
        raise HTTPException(status_code=503, detail="Carbon estimator artifacts are not loaded")
    try:
        return carbon_estimator.estimate(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@cli.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the server to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to run the server on"),
    model_path: Optional[str] = typer.Option(
        None,
        "--model-path",
        "-m",
        help="Path to the local model directory. Overrides SWEPRUNER_MODEL_PATH.",
    ),
):
    """Start the local TokenWise FastAPI service."""
    if model_path:
        os.environ["SWEPRUNER_MODEL_PATH"] = str(Path(model_path).expanduser().resolve())
    typer.echo(f"Starting TokenWise backend on http://{host}:{port}")
    typer.echo(f"Model path: {resolve_model_path()}")
    uvicorn.run(app, host=host, port=port)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
