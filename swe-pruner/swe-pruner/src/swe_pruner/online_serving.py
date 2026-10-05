import os

# Bound CPU parallelism; model requests are serialized to avoid oversubscription.
CPU_THREADS = max(1, min(8, int(os.getenv("TOKENWISE_CPU_THREADS", "4"))))
os.environ.setdefault("OMP_NUM_THREADS", str(CPU_THREADS))
os.environ.setdefault("MKL_NUM_THREADS", str(CPU_THREADS))
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import asyncio
import logging
import threading
from pathlib import Path
from typing import List, Optional, Literal

import torch
import typer
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .carbon_estimator import CarbonEstimateRequest, CarbonEstimateResponse, CarbonEstimator
from .goal_compiler import GoalCompiler
from .goal_generator_client import LocalGoalGeneratorClient
from .prune_wrapper import PruneRequest, PruneResponse, SwePrunerForCodePruning
from .repository.repository_index import RepositoryIndexCache
from .retrieval.workspace_context import WorkspaceContextBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
torch.set_num_threads(CPU_THREADS)

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
repository_cache = RepositoryIndexCache()
workspace_builder = WorkspaceContextBuilder()
inference_lock = threading.RLock()
reconciliation_task: Optional[asyncio.Task] = None


class WorkspaceIndexRequest(BaseModel):
    workspace_root: str
    watcher_id: str = Field(min_length=1, max_length=128, pattern=r"^[a-zA-Z0-9_-]+$")
    action: Literal["start", "update", "reconcile", "stop"]
    paths: List[str] = Field(default_factory=list, max_length=512)
    sequence: Optional[int] = Field(default=None, ge=0)


class WorkspaceIndexResponse(BaseModel):
    indexed_files: int
    repository_fingerprint: str
    retrieval_cache_hit: bool


class WorkspacePruneRequest(BaseModel):
    query: str = Field(min_length=1)
    workspace_root: str
    active_file: Optional[str] = None
    language: str = "python"
    current_symbol: Optional[str] = None
    selected_code: Optional[str] = None
    diagnostics: List[str] = Field(default_factory=list)
    threshold: float = Field(default=0.45, ge=0.0, le=1.0)
    local_llm_url: Optional[str] = None
    local_llm_model: Optional[str] = None
    token_budget: int = Field(default=8192, ge=256, le=32768)
    max_candidates: int = Field(default=8, ge=1, le=32)


class WorkspacePruneResponse(BaseModel):
    structured_goal: dict
    unified_prompt: str
    pruned_tokens: int
    original_tokens: int
    files: List[dict]
    selected_file: str
    repository_fingerprint: str
    index_cache_hit: bool = False
    context_cache_hit: bool = False
    retrieval_cache_hit: bool = False
    context_mode: str = "focused"
    indexed_files: int = 0
    raw_context_tokens: int = 0
    retained_source_tokens: int = 0
    context_overhead_tokens: int = 0
    warnings: List[str] = Field(default_factory=list)


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
    global model, reconciliation_task
    reconciliation_task = asyncio.create_task(reconcile_indexes())
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


def refresh_indexes() -> None:
    for index in repository_cache.reconcile_watched():
        workspace_builder.prepare(index)


async def reconcile_indexes() -> None:
    while True:
        await asyncio.sleep(15)
        try:
            await asyncio.to_thread(refresh_indexes)
        except Exception:
            logger.exception("Background repository reconciliation failed")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    global reconciliation_task
    if reconciliation_task is not None:
        reconciliation_task.cancel()
        try:
            await reconciliation_task
        except asyncio.CancelledError:
            pass
        reconciliation_task = None


@app.get("/health")
async def health_check():
    device = None
    if model is not None:
        try:
            device = str(next(model.parameters()).device)
        except StopIteration:
            device = "unknown"
    return {
        "service": "tokenwise",
        "status": "healthy",
        "model_loaded": model is not None,
        "carbon_models_loaded": bool(carbon_estimator and carbon_estimator.is_ready()),
        "device": device,
        "model_path": str(resolve_model_path()),
        "pid": os.getpid(),
        "repository_indexing": True,
    }


@app.post("/index-workspace", response_model=WorkspaceIndexResponse)
async def index_workspace(request: WorkspaceIndexRequest) -> WorkspaceIndexResponse:
    root = Path(request.workspace_root)
    if not root.is_absolute() or (request.action != "stop" and not root.is_dir()):
        raise HTTPException(status_code=400, detail="Indexing requires an existing absolute workspace directory")

    def synchronize() -> WorkspaceIndexResponse:
        try:
            index = repository_cache.synchronize(str(root), request.watcher_id, request.action, request.paths, request.sequence)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        reused = False
        if request.action != "stop":
            _, _, reused = workspace_builder.prepare(index)
        return WorkspaceIndexResponse(indexed_files=len(index.index), repository_fingerprint=index.fingerprint,
                                      retrieval_cache_hit=reused)
    return await asyncio.to_thread(synchronize)


@app.post("/prune", response_model=PruneResponse)
async def prune_code(request: PruneRequest) -> PruneResponse:
    if model is None:
        raise HTTPException(status_code=503, detail="Pruner model is not loaded")
    def run() -> PruneResponse:
        with inference_lock:
            return model.prune(request)
    return await asyncio.to_thread(run)


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
    if not workspace_root.is_dir():
        raise HTTPException(status_code=400, detail="Workspace root does not exist")
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be blank")
    active_rel_path = None
    if request.active_file:
        active_file = Path(request.active_file).expanduser()
        if not active_file.is_absolute():
            active_file = workspace_root / active_file
        try:
            active_rel_path = active_file.resolve().relative_to(workspace_root).as_posix()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Active file must be inside the workspace") from exc

    repo_index, cache_hit = await asyncio.to_thread(repository_cache.get, str(workspace_root))
    if not repo_index.index:
        raise HTTPException(status_code=400, detail="Workspace contains no indexed Python files")
    if active_rel_path and active_rel_path not in repo_index.index:
        raise HTTPException(status_code=400, detail="Active file is not an indexed Python file")

    goal = await goal_compiler.compile(
        query=request.query.strip(),
        active_file=active_rel_path or "(automatic repository discovery)",
        current_symbol=request.current_symbol,
        selected_code=request.selected_code,
        diagnostics=request.diagnostics,
        local_llm_url=request.local_llm_url,
        local_llm_model=request.local_llm_model,
    )

    def build() -> dict:
        with inference_lock:
            return workspace_builder.build(
                repo_index, goal, model, active_rel_path, request.query.strip(),
                request.threshold, request.token_budget, request.max_candidates,
            )

    result = await asyncio.to_thread(build)
    return WorkspacePruneResponse(**result, index_cache_hit=cache_hit)


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
