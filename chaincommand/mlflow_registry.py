"""MLflow Model Registry integration for ChainCommand."""
from __future__ import annotations

import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    import mlflow
    from mlflow.tracking import MlflowClient

    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False


class ModelRegistry:
    """Manages model versioning and stage transitions via MLflow."""

    STAGES = ("staging", "production", "archived")

    def __init__(
        self,
        tracking_uri: str = "http://localhost:5000",
        experiment_name: str = "chaincommand",
    ) -> None:
        if not HAS_MLFLOW:
            logger.warning("mlflow not installed — registry disabled")
            self._enabled = False
            return
        self._enabled = True
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self._client = MlflowClient(tracking_uri)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def log_model_run(
        self,
        model_name: str,
        params: dict[str, Any],
        metrics: dict[str, float],
        artifacts: dict[str, str] | None = None,
        tags: dict[str, str] | None = None,
    ) -> str | None:
        """Log a training run and register the model."""
        if not self._enabled:
            return None
        with mlflow.start_run(
            run_name=f"{model_name}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}"
        ) as run:
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            if tags:
                mlflow.set_tags(tags)
            if artifacts:
                for name, path in artifacts.items():
                    if Path(path).exists():
                        mlflow.log_artifact(path, name)
            # Log model metadata
            mlflow.log_dict(
                {
                    "model_name": model_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "params": params,
                    "metrics": metrics,
                },
                "model_metadata.json",
            )
            logger.info(
                "logged mlflow run %s for model %s", run.info.run_id, model_name
            )
            return run.info.run_id

    def register_model(self, run_id: str, model_name: str) -> int | None:
        """Register a model version from a run."""
        if not self._enabled:
            return None
        model_uri = f"runs:/{run_id}/model"
        try:
            result = mlflow.register_model(model_uri, model_name)
            logger.info(
                "registered model %s version %s", model_name, result.version
            )
            return int(result.version)
        except Exception as e:
            logger.error("failed to register model %s: %s", model_name, e)
            return None

    def transition_stage(
        self, model_name: str, version: int, stage: str
    ) -> bool:
        """Transition a model version to a new stage."""
        if not self._enabled:
            return False
        if stage not in self.STAGES:
            raise ValueError(
                f"Invalid stage '{stage}'. Must be one of {self.STAGES}"
            )
        try:
            self._client.transition_model_version_stage(
                model_name, str(version), stage
            )
            logger.info(
                "transitioned %s v%d to %s", model_name, version, stage
            )
            return True
        except Exception as e:
            logger.error(
                "failed to transition %s v%d: %s", model_name, version, e
            )
            return False

    def get_production_model(self, model_name: str) -> dict[str, Any] | None:
        """Get the current production model version."""
        if not self._enabled:
            return None
        try:
            versions = self._client.get_latest_versions(
                model_name, stages=["production"]
            )
            if versions:
                v = versions[0]
                return {
                    "name": model_name,
                    "version": int(v.version),
                    "stage": v.current_stage,
                    "run_id": v.run_id,
                }
        except Exception as e:
            logger.error(
                "failed to get production model %s: %s", model_name, e
            )
        return None

    def list_models(self) -> list[dict[str, Any]]:
        """List all registered models."""
        if not self._enabled:
            return []
        try:
            models = self._client.search_registered_models()
            return [
                {
                    "name": m.name,
                    "latest_versions": [
                        {"version": v.version, "stage": v.current_stage}
                        for v in (m.latest_versions or [])
                    ],
                }
                for m in models
            ]
        except Exception as e:
            logger.error("failed to list models: %s", e)
            return []
