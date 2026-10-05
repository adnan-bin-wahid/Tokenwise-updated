"""Trusted, stdlib-only installer shipped with the extension. Never needs Git or Node."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path, PurePosixPath


BACKEND = Path("swe-pruner/swe-pruner")
TORCH_VERSION = "2.14.1"
CORE_PINS = ["transformers==4.57.6", "huggingface-hub==0.36.2", "fastapi==0.141.1", "uvicorn==0.52.4"]
STEPS = {"prerequisites": 1, "files": 2, "environment": 3, "tools": 4,
         "torch": 4, "dependencies": 4, "model": 5, "verify": 5, "check": 6, "complete": 7}
HINTS = {
    "prerequisites": "Use 64-bit Python 3.12 and a trusted local folder. Reinstall the VSIX if bundled files fail verification.",
    "files": "Check free disk space and permissions for TokenWise user storage, then retry.",
    "environment": "Check your Python 3.12 installation and storage permissions, then retry.",
    "tools": "Check internet/proxy access to PyPI and free disk space, then retry. Completed steps are retained.",
    "torch": "Check access to download.pytorch.org and free disk space, then retry. No GPU is required.",
    "dependencies": "Check access to PyPI and free disk space, then retry. Verified completed dependency steps are reused.",
    "model": "Check access to Hugging Face and free disk space, then retry. Partial downloads resume when supported.",
    "verify": "Retry to verify or replace the download. Corrupt weights are not used.",
    "check": "Open TokenWise Setup output for the import error. Retry rechecks dependencies and repairs failed checks.",
    "complete": "Check storage/settings permissions, then retry. The verified installation is retained.",
}
current_stage = "prerequisites"


def progress(stage: str, message: str, **extra) -> None:
    global current_stage
    current_stage = stage
    print("TOKENWISE_PROGRESS " + json.dumps({"stage": stage, "message": message,
          "step": STEPS.get(stage, 1), "total_steps": 7, **extra}), flush=True)


def checksum(filename: Path) -> str:
    digest = hashlib.sha256()
    with filename.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    parts = PurePosixPath(relative)
    if not parts.parts or parts.is_absolute() or any(part in {"..", "."} or "\\" in part or ":" in part for part in parts.parts):
        raise ValueError(f"Unsafe installer path: {relative}")
    current = root
    for part in parts.parts:
        current /= part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError(f"Installer paths cannot contain symbolic links or junctions: {current}")
    if not current.resolve().is_relative_to(root.resolve()):
        raise ValueError("Installer paths must remain in user storage.")
    return current


def load_manifest(bundle: Path) -> tuple[dict, str]:
    raw = (bundle / "backend-manifest.json").read_bytes()
    manifest = json.loads(raw)
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), list) or not manifest["files"]:
        raise ValueError("Invalid bundled backend manifest. Reinstall the TokenWise extension.")
    seen = set()
    for entry in manifest["files"]:
        relative = entry["path"]
        if relative in seen:
            raise ValueError("Duplicate bundled backend path.")
        seen.add(relative)
        source = safe_path(bundle, relative)
        if source.stat().st_size != entry["size"] or checksum(source) != entry["sha256"]:
            raise ValueError(f"Bundled file failed verification: {relative}. Reinstall the extension.")
    model = manifest["model"]
    expected_url = f"https://huggingface.co/{model['repository']}/resolve/{model['revision']}/model.safetensors"
    if (model["repository"] != "ayanami-kitasan/code-pruner" or not re.fullmatch(r"[a-f0-9]{40}", model["revision"])
            or not re.fullmatch(r"[a-f0-9]{64}", model["sha256"]) or model["url"] != expected_url
            or type(model["size"]) is not int or model["size"] <= 0):
        raise ValueError("Invalid pinned model download metadata.")
    return manifest, hashlib.sha256(raw).hexdigest()


def download_model(model: dict, cache: Path, local_file: Path | None = None) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    destination = safe_path(cache, model["sha256"] + ".safetensors")
    if destination.is_file() and destination.stat().st_size == model["size"] and checksum(destination) == model["sha256"]:
        progress("model", "Reusing the verified model download")
        return destination
    partial = safe_path(cache, model["sha256"] + ".part")
    if partial.is_file() and partial.stat().st_size == model["size"] and checksum(partial) == model["sha256"]:
        progress("verify", "Recovering an already complete, verified partial download")
        os.replace(partial, destination)
        return destination
    if local_file:
        if local_file.stat().st_size != model["size"] or checksum(local_file) != model["sha256"]:
            raise ValueError("The selected model does not match the pinned SWE-Pruner weights.")
        shutil.copyfile(local_file, partial)
    else:
        offset = partial.stat().st_size if partial.exists() else 0
        if offset >= model["size"]:
            partial.unlink()
            offset = 0
        headers = {"User-Agent": "TokenWise-Installer/0.4"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        progress("model", "Downloading verified SWE-Pruner weights (about 1.35 GB)", current=offset, total=model["size"])
        request = urllib.request.Request(model["url"], headers=headers)
        with urllib.request.urlopen(request, timeout=60) as response:
            if not response.geturl().startswith("https://"):
                raise ValueError("The model download must remain on HTTPS.")
            if response.status == 206:
                content_range = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", response.headers.get("Content-Range", ""))
                if (not content_range or int(content_range[1]) != offset or int(content_range[3]) != model["size"]
                        or not offset <= int(content_range[2]) < model["size"]):
                    raise ValueError("Invalid model download resume response.")
            elif response.status == 200:
                offset = 0  # Some proxies do not support byte ranges; restart rather than corrupt the file.
            else:
                raise ValueError(f"Unexpected model download HTTP status: {response.status}")
            reported = time.monotonic()
            with partial.open("ab" if offset else "wb") as stream:
                while chunk := response.read(1024 * 1024):
                    stream.write(chunk)
                    offset += len(chunk)
                    if offset > model["size"]:
                        raise ValueError("The downloaded model is larger than expected.")
                    if time.monotonic() - reported >= 1:
                        progress("model", "Downloading model", current=offset, total=model["size"])
                        reported = time.monotonic()
    progress("verify", "Checking the model's SHA-256 checksum")
    if partial.stat().st_size < model["size"]:
        raise ValueError("Model download ended early. Run setup again to resume the partial download.")
    if partial.stat().st_size != model["size"] or checksum(partial) != model["sha256"]:
        partial.unlink(missing_ok=True)
        raise ValueError("Model download failed integrity verification. Run setup again to retry.")
    os.replace(partial, destination)
    return destination


def execute(arguments: list[str], **kwargs) -> None:
    subprocess.run(arguments, check=True, stdin=subprocess.DEVNULL,
                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0, **kwargs)


def read_checkpoint(filename: Path, fingerprint: str) -> set[str]:
    try:
        if filename.stat().st_size > 16384:
            return set()
        data = json.loads(filename.read_text(encoding="utf-8"))
        if (isinstance(data, dict) and data.get("schema_version") == 1
                and data.get("bundle_sha256") == fingerprint and isinstance(data.get("completed"), list)):
            return {stage for stage in data["completed"] if isinstance(stage, str) and stage in {"tools", "torch", "dependencies"}}
    except (OSError, ValueError):
        pass
    return set()


def write_checkpoint(installation: Path, fingerprint: str, completed: set[str]) -> None:
    temporary = safe_path(installation, "setup-state.json.tmp")
    temporary.write_text(json.dumps({"schema_version": 1, "bundle_sha256": fingerprint,
                                    "completed": sorted(completed)}), encoding="utf-8")
    os.replace(temporary, safe_path(installation, "setup-state.json"))


def install(bundle: Path, storage: Path, version: str, local_model: Path | None = None) -> Path:
    progress("prerequisites", "Checking Python and bundled file integrity")
    if sys.version_info[:2] != (3, 12) or sys.maxsize <= 2**32:
        raise ValueError("Install 64-bit Python 3.12, then run TokenWise setup again.")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Invalid TokenWise version.")
    bundle = bundle.resolve()
    manifest, fingerprint = load_manifest(bundle)
    storage.mkdir(parents=True, exist_ok=True)
    storage = storage.resolve()
    installation = safe_path(storage, f"backend/managed/{version}-{fingerprint[:12]}")
    installation.mkdir(parents=True, exist_ok=True)
    lock = safe_path(storage, "backend/install.lock")
    try:
        with lock.open("x") as stream:
            stream.write(str(os.getpid()))
    except FileExistsError as exc:
        raise ValueError("Another backend setup may be running. Wait for it to finish; if the IDE was closed during setup, remove backend/install.lock from TokenWise user storage and retry.") from exc
    try:
        progress("files", "Preparing the bundled backend in user storage")
        for entry in manifest["files"]:
            target = safe_path(installation, entry["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe_path(bundle, entry["path"]), target)
        venv = safe_path(installation, ".venv")
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        checkpoint = safe_path(installation, "setup-state.json")
        completed = read_checkpoint(checkpoint, fingerprint)
        progress("environment", "Checking the private Python environment")
        usable = python.exists()
        if usable:
            try:
                execute([str(python), "-c", "import sys, struct, pip; assert sys.version_info[:2] == (3, 12) and struct.calcsize('P') == 8"])
            except (subprocess.CalledProcessError, OSError):
                usable = False
        if not usable:
            progress("environment", "Creating a private Python environment")
            execute([sys.executable, "-m", "venv", "--clear", str(venv)])
            completed.clear()
            write_checkpoint(installation, fingerprint, completed)
        package_environment = os.environ.copy()
        package_environment["PIP_CACHE_DIR"] = str(safe_path(storage, "backend/pip-cache"))
        environment = os.environ.copy()
        environment.update({"PYTHONUTF8": "1", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
                            "PYTHONPATH": str(installation / BACKEND / "src"),
                            "SWEPRUNER_MODEL_PATH": str(installation / BACKEND / "model"),
                            "SWEPRUNER_CARBON_ARTIFACTS_DIR": str(installation / BACKEND / "carbon_artifacts")})

        def packages(stage: str, message: str, arguments: list[str], check: str) -> None:
            progress(stage, message)
            if stage in completed:
                try:
                    execute([str(python), "-c", check], cwd=installation, env=environment)
                except (subprocess.CalledProcessError, OSError):
                    completed.remove(stage)
                    write_checkpoint(installation, fingerprint, completed)
                    progress(stage, "Repairing a previously completed dependency step")
                    if stage == "dependencies" and sys.platform != "darwin":
                        arguments += [f"torch=={TORCH_VERSION}+cpu", "--extra-index-url", "https://download.pytorch.org/whl/cpu"]
                    arguments.append("--force-reinstall")
                else:
                    progress(stage, "Completed dependency step verified and reused")
                    return
            execute(arguments, env=package_environment)
            execute([str(python), "-c", check], cwd=installation, env=environment)
            completed.add(stage)
            write_checkpoint(installation, fingerprint, completed)

        packages("tools", "Installing packaging tools", [str(python), "-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "pip", "setuptools", "wheel"],
                 "import importlib.metadata as m; [m.version(name) for name in ('pip', 'setuptools', 'wheel')]")
        torch_args = [str(python), "-m", "pip", "install", "--disable-pip-version-check", f"torch=={TORCH_VERSION}"]
        if sys.platform != "darwin":
            torch_args += ["--index-url", "https://download.pytorch.org/whl/cpu"]
        packages("torch", "Installing CPU PyTorch; first setup may take several minutes", torch_args,
                 f"import torch; assert torch.__version__.split('+')[0] == {TORCH_VERSION!r}")
        dependency_check = ("import importlib.metadata as m; import fastapi, uvicorn, transformers, swe_pruner.online_serving; "
                            f"assert all(m.version(name) == version for name, version in {[pin.split('==') for pin in CORE_PINS]!r}); m.version('swe-pruner')")
        packages("dependencies", "Installing TokenWise backend dependencies", [str(python), "-m", "pip", "install", "--disable-pip-version-check", *CORE_PINS, str(installation / BACKEND)], dependency_check)
        progress("model", "Checking or downloading the verified model")
        model = download_model(manifest["model"], safe_path(storage, "backend/downloads"), local_model)
        target = safe_path(installation, f"{BACKEND.as_posix()}/model/model.safetensors")
        if target.exists() and (target.stat().st_size != manifest["model"]["size"] or checksum(target) != manifest["model"]["sha256"]):
            target.unlink()
        if not target.exists():
            try:
                os.link(model, target)
            except OSError:
                shutil.copyfile(model, target)
        progress("check", "Checking backend imports, tokenizer, and trained carbon artifacts")
        check = "import swe_pruner.online_serving as s; from tokenizers import Tokenizer; assert s.check_model_path(s.resolve_model_path()); Tokenizer.from_file(str(s.resolve_model_path()/'tokenizer.json')); assert s.carbon_estimator and s.carbon_estimator.is_ready(); print('TOKENWISE_BACKEND_IMPORTS_OK')"
        execute([str(python), "-c", check], cwd=installation, env=environment)
        marker = safe_path(installation, "managed-install.json")
        marker.write_text(json.dumps({"schema_version": 1, "version": version, "bundle_sha256": fingerprint}), encoding="utf-8")
        progress("complete", "Backend installation complete", installation_root=str(installation))
        return installation
    finally:
        if lock.exists() and lock.read_text() == str(os.getpid()):
            lock.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--storage", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--model-file", type=Path)
    args = parser.parse_args()
    try:
        install(args.bundle, args.storage, args.version, args.model_file)
        return 0
    except Exception as exc:
        print("TOKENWISE_SETUP_ERROR " + json.dumps({"stage": current_stage, "message": str(exc),
              "hint": HINTS.get(current_stage, HINTS["prerequisites"]), "step": STEPS.get(current_stage, 1)}), file=sys.stderr, flush=True)
        print(f"TokenWise setup failed: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
