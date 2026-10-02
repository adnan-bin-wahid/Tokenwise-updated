from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field

from .carbon_model_engine import DualModeRegressorEngine, EstimationRequest


class CarbonEstimateRequest(BaseModel):
    input_tokens: int = Field(ge=1)
    output_tokens: int = Field(default=256, ge=1)
    model_name: str = "meta-llama-3-8b-instruct"
    model_size_b: float | None = Field(default=None, gt=0)
    gpu_type: str | None = None
    latency_per_input_token_ms: float | None = Field(default=None, gt=0)
    latency_per_output_token_ms: float | None = Field(default=None, gt=0)
    mmlu_pro_score: float | None = Field(default=None, ge=0, le=1)
    bbh_score: float | None = Field(default=None, ge=0, le=1)
    carbon_intensity_g_per_kwh: float = Field(default=475.0, gt=0)


class CarbonEstimateResponse(BaseModel):
    prefill_joules: float
    decode_joules: float
    total_joules: float
    co2_grams: float
    carbon_intensity_g_per_kwh: float
    model_name: str
    prefill_route: str
    decode_route: str
    features_source: str


DEFAULT_MODEL_REGISTRY = {
    # Closed-source model attributes are assumptions because vendors do not publish all fields.
    "gpt-4o": {
        "model_size_b": 200.0,
        "mmlu_pro_score": 0.70,
        "bbh_score": 0.83,
        "latency_per_input_token_ms": 0.8,
        "latency_per_output_token_ms": 2.2,
        "gpu_type": "nvidia-a100-80gb",
    },
    "claude-3-5-sonnet": {
        "model_size_b": 70.0,
        "mmlu_pro_score": 0.74,
        "bbh_score": 0.86,
        "latency_per_input_token_ms": 0.8,
        "latency_per_output_token_ms": 2.2,
        "gpu_type": "nvidia-a100-80gb",
    },
}


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[2]


class CarbonEstimator:
    """SEAL-derived prompt-level estimator backed only by trained artifacts."""

    def __init__(self, artifacts_dir: str | Path | None = None) -> None:
        if artifacts_dir is None:
            configured = os.getenv("SWEPRUNER_CARBON_ARTIFACTS_DIR")
            artifacts_dir = Path(configured) if configured else _runtime_root() / "carbon_artifacts"
        self.artifacts_dir = Path(artifacts_dir).resolve()

        feature_payload = self._load_json("feature_artifacts.json", required=True)
        self.gpu_encoder = {
            str(k).strip().lower(): int(v)
            for k, v in feature_payload.get("gpu_encoder", {}).items()
        }
        if not self.gpu_encoder:
            raise RuntimeError("feature_artifacts.json does not contain a GPU encoder")

        min_size = float(feature_payload.get("interpolation_min_model_size_b", 7.0))
        max_size = float(feature_payload.get("interpolation_max_model_size_b", 111.0))
        self.engine = DualModeRegressorEngine(
            self.artifacts_dir,
            interpolation_min_model_size_b=min_size,
            interpolation_max_model_size_b=max_size,
        )
        self.model_registry = self._load_model_registry()

    def _load_json(self, filename: str, *, required: bool) -> dict:
        path = self.artifacts_dir / filename
        if not path.exists():
            if required:
                raise RuntimeError(f"Missing carbon artifact: {path}")
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RuntimeError(f"Invalid JSON object in carbon artifact: {path}")
        return payload

    def _load_model_registry(self) -> dict[str, dict]:
        payload = self._load_json("model_registry.json", required=False)
        merged = dict(DEFAULT_MODEL_REGISTRY)
        merged.update({str(k).strip().lower(): v for k, v in payload.items() if isinstance(v, dict)})
        return merged

    def is_ready(self) -> bool:
        return self.engine.is_ready()

    def _resolve_model_features(self, request: CarbonEstimateRequest):
        key = request.model_name.strip().lower()
        defaults = self.model_registry.get(key, {})

        def pick(request_value, registry_key: str, fallback):
            return request_value if request_value is not None else defaults.get(registry_key, fallback)

        model_size_b = float(pick(request.model_size_b, "model_size_b", 200.0))
        mmlu = float(pick(request.mmlu_pro_score, "mmlu_pro_score", 0.50))
        bbh = float(pick(request.bbh_score, "bbh_score", 0.60))
        latency_in = float(pick(request.latency_per_input_token_ms, "latency_per_input_token_ms", 0.8))
        latency_out = float(pick(request.latency_per_output_token_ms, "latency_per_output_token_ms", 2.2))
        gpu_type = str(pick(request.gpu_type, "gpu_type", "nvidia-a100-80gb")).strip().lower()

        # The benchmark features use normalized quality scores in [0, 1].
        if not 0 <= mmlu <= 1 or not 0 <= bbh <= 1:
            raise ValueError("MMLU-Pro and BBH scores must be normalized to the [0, 1] range")
        if gpu_type not in self.gpu_encoder:
            supported = ", ".join(sorted(self.gpu_encoder))
            raise ValueError(f"Unsupported GPU type '{gpu_type}'. Supported values: {supported}")

        source = "model_registry" if key in self.model_registry else "default_assumptions"
        if any(
            value is not None
            for value in (
                request.model_size_b,
                request.gpu_type,
                request.latency_per_input_token_ms,
                request.latency_per_output_token_ms,
                request.mmlu_pro_score,
                request.bbh_score,
            )
        ):
            source += "+request_overrides"

        return model_size_b, mmlu, bbh, latency_in, latency_out, gpu_type, source

    def estimate(self, request: CarbonEstimateRequest) -> CarbonEstimateResponse:
        if not self.is_ready():
            raise RuntimeError("Carbon estimator artifacts are incomplete")

        (
            model_size_b,
            mmlu,
            bbh,
            latency_in,
            latency_out,
            gpu_type,
            source,
        ) = self._resolve_model_features(request)

        prediction = self.engine.predict(
            EstimationRequest(
                n_input_tokens=request.input_tokens,
                n_output_tokens=request.output_tokens,
                model_size_b=model_size_b,
                latency_per_input_token_ms=latency_in,
                latency_per_output_token_ms=latency_out,
                gpu_encoded=self.gpu_encoder[gpu_type],
                mmlu_pro_score=mmlu,
                bbh_score=bbh,
            )
        )

        co2_grams = (prediction.total_joules / 3_600_000.0) * request.carbon_intensity_g_per_kwh
        return CarbonEstimateResponse(
            prefill_joules=prediction.prefill_joules,
            decode_joules=prediction.decode_joules,
            total_joules=prediction.total_joules,
            co2_grams=max(0.0, co2_grams),
            carbon_intensity_g_per_kwh=request.carbon_intensity_g_per_kwh,
            model_name=request.model_name,
            prefill_route=prediction.prefill_route,
            decode_route=prediction.decode_route,
            features_source=f"artifact_models:{source}",
        )
