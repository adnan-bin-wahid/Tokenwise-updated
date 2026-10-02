from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import joblib
import numpy as np
import pandas as pd

from .features import FEATURE_COLUMNS

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover
    XGBRegressor = None

RouteType = Literal["xgboost_interpolation", "ridge_extrapolation"]
REFERENCE_INPUT_TOKENS = 256
REFERENCE_OUTPUT_TOKENS = 128


@dataclass(frozen=True)
class EstimationRequest:
    n_input_tokens: int
    n_output_tokens: int
    model_size_b: float
    latency_per_input_token_ms: float
    latency_per_output_token_ms: float
    gpu_encoded: int
    mmlu_pro_score: float
    bbh_score: float


@dataclass(frozen=True)
class EstimationResponse:
    prefill_joules: float
    decode_joules: float
    total_joules: float
    prefill_route: RouteType
    decode_route: RouteType


class DualModeRegressorEngine:
    def __init__(
        self,
        artifacts_dir: str | Path,
        interpolation_min_model_size_b: float = 7.0,
        interpolation_max_model_size_b: float = 111.0,
    ) -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.interpolation_min_model_size_b = interpolation_min_model_size_b
        self.interpolation_max_model_size_b = interpolation_max_model_size_b
        self.xgb_prefill = self._load_xgb("xgb_prefill_interpolation.json")
        self.xgb_decode = self._load_xgb("xgb_decode_interpolation.json")
        self.ridge_prefill = self._load_pickle("ridge_prefill_extrapolation.pkl")
        self.ridge_decode = self._load_pickle("ridge_decode_extrapolation.pkl")

    def _load_xgb(self, filename: str):
        if XGBRegressor is None:
            return None
        path = self.artifacts_dir / filename
        if not path.exists():
            return None
        model = XGBRegressor()
        model.load_model(path)
        return model

    def _load_pickle(self, filename: str):
        path = self.artifacts_dir / filename
        return joblib.load(path) if path.exists() else None

    def is_ready(self) -> bool:
        return all(
            model is not None
            for model in (self.xgb_prefill, self.xgb_decode, self.ridge_prefill, self.ridge_decode)
        )

    def _route(self, model_size_b: float) -> RouteType:
        if self.interpolation_min_model_size_b <= model_size_b <= self.interpolation_max_model_size_b:
            return "xgboost_interpolation"
        return "ridge_extrapolation"

    @staticmethod
    def _as_reference_frame(request: EstimationRequest) -> pd.DataFrame:
        return pd.DataFrame(
            [{
                "n_input_tokens": REFERENCE_INPUT_TOKENS,
                "n_output_tokens": REFERENCE_OUTPUT_TOKENS,
                "model_size_b": request.model_size_b,
                "latency_per_input_token_ms": request.latency_per_input_token_ms,
                "latency_per_output_token_ms": request.latency_per_output_token_ms,
                "gpu_encoded": request.gpu_encoded,
                "mmlu_pro_score": request.mmlu_pro_score,
                "bbh_score": request.bbh_score,
            }],
            columns=FEATURE_COLUMNS,
        )

    def predict(self, request: EstimationRequest) -> EstimationResponse:
        if not self.is_ready():
            raise RuntimeError("Carbon estimator artifacts are incomplete")
        features = self._as_reference_frame(request)
        route = self._route(request.model_size_b)
        if route == "xgboost_interpolation":
            prefill_ref = float(self.xgb_prefill.predict(features)[0])
            decode_ref = float(self.xgb_decode.predict(features)[0])
        else:
            prefill_ref = float(np.asarray(self.ridge_prefill.predict(features))[0])
            decode_ref = float(np.asarray(self.ridge_decode.predict(features))[0])

        prefill = max(0.0, prefill_ref) * (request.n_input_tokens / REFERENCE_INPUT_TOKENS)
        decode = max(0.0, decode_ref) * (request.n_output_tokens / REFERENCE_OUTPUT_TOKENS)
        return EstimationResponse(prefill, decode, prefill + decode, route, route)
