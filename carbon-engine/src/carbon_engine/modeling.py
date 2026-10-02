from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict

from .features import FEATURE_COLUMNS

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover - runtime environment may not have xgboost yet
    XGBRegressor = None


@dataclass(frozen=True)
class Metrics:
    mape: float
    mae: float
    rmse: float
    r2: float



def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Metrics:
    return Metrics(
        mape=float(mean_absolute_percentage_error(y_true, y_pred) * 100.0),
        mae=float(mean_absolute_error(y_true, y_pred)),
        rmse=float(np.sqrt(np.mean((y_true - y_pred) ** 2))),
        r2=float(r2_score(y_true, y_pred)),
    )



def _cross_validate(model, x: pd.DataFrame, y: pd.Series, n_splits: int = 5) -> Metrics:
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    preds = cross_val_predict(model, x, y, cv=cv)
    return _metrics(y.to_numpy(), preds)



def _fit_xgb(x: pd.DataFrame, y: pd.Series):
    if XGBRegressor is None:
        raise RuntimeError("xgboost is required for interpolation models. Install xgboost first.")

    from xgboost import XGBRegressor as _XGBRegressor
    model = _XGBRegressor(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.3,
        objective="reg:squarederror",
        random_state=42,
    )
    model.fit(x, y)
    return model



def _fit_ridge(x: pd.DataFrame, y: pd.Series):
    model = Ridge(alpha=1.0, random_state=42)
    model.fit(x, y)
    return model



def _train_one(
    df: pd.DataFrame,
    target_col: str,
    use_xgb: bool,
) -> tuple[object, Metrics]:
    x = df[FEATURE_COLUMNS]
    y = df[target_col]

    if use_xgb:
        if XGBRegressor is None:
            raise RuntimeError("xgboost is required for interpolation models. Install xgboost first.")
        from xgboost import XGBRegressor as _XGBRegressor
        probe_model = _XGBRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.3,
            objective="reg:squarederror",
            random_state=42,
        )
        cv_metrics = _cross_validate(probe_model, x, y)
        model = _fit_xgb(x, y)
        return model, cv_metrics

    probe_model = Ridge(alpha=1.0, random_state=42)
    cv_metrics = _cross_validate(probe_model, x, y)
    model = _fit_ridge(x, y)
    return model, cv_metrics



def train_all_models(feature_df: pd.DataFrame) -> tuple[dict[str, object], dict[str, Metrics]]:
    interpolation_df = feature_df[feature_df["is_interpolation"]].copy()
    extrapolation_df = feature_df[~feature_df["is_interpolation"]].copy()

    if interpolation_df.empty:
        raise ValueError("Interpolation split is empty. Cannot train interpolation models.")
    if extrapolation_df.empty:
        raise ValueError("Extrapolation split is empty. Cannot train extrapolation models.")

    models: dict[str, object] = {}
    metrics: dict[str, Metrics] = {}

    models["xgb_prefill_interpolation"], metrics["xgb_prefill_interpolation"] = _train_one(
        interpolation_df,
        "prefill_energy_j",
        use_xgb=True,
    )
    models["xgb_decode_interpolation"], metrics["xgb_decode_interpolation"] = _train_one(
        interpolation_df,
        "decode_energy_j",
        use_xgb=True,
    )
    models["ridge_prefill_extrapolation"], metrics["ridge_prefill_extrapolation"] = _train_one(
        extrapolation_df,
        "prefill_energy_j",
        use_xgb=False,
    )
    models["ridge_decode_extrapolation"], metrics["ridge_decode_extrapolation"] = _train_one(
        extrapolation_df,
        "decode_energy_j",
        use_xgb=False,
    )

    return models, metrics



def save_models(models: dict[str, object], output_dir: str | Path) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for name, model in models.items():
        if name.startswith("xgb_"):
            model.save_model(str(out / f"{name}.json"))
        else:
            joblib.dump(model, out / f"{name}.pkl")
