from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)


class TribeInferenceError(RuntimeError):
    pass


class TribeInferenceService:
    _instance: "TribeInferenceService | None" = None
    _model: object | None = None
    _initialized: bool = False
    _load_error: str | None = None

    def __init__(self, cache_folder: str | Path | None = None) -> None:
        self._cache_folder = cache_folder or os.getenv("TRIBE_CACHE", "./cache/tribev2")
        Path(self._cache_folder).mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_instance(
        cls, cache_folder: str | Path | None = None
    ) -> "TribeInferenceService":
        if cls._instance is None:
            cls._instance = cls(cache_folder=cache_folder)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None
        cls._model = None
        cls._initialized = False
        cls._load_error = None

    def is_available(self) -> bool:
        return self._model is not None and self._initialized

    def get_load_error(self) -> str | None:
        return self._load_error

    def load_model(
        self,
        checkpoint: str = "facebook/tribev2",
        checkpoint_name: str = "best.ckpt",
    ) -> bool:
        if self._initialized and self._model is not None:
            logger.info("TRIBE model already loaded")
            return True

        try:
            from tribev2 import TribeModel
        except ImportError as exc:
            self._load_error = f"Cannot import TribeModel: {exc}"
            logger.warning(self._load_error)
            return False

        try:
            logger.info(f"Loading TRIBE model from {checkpoint}...")
            self._model = TribeModel.from_pretrained(
                checkpoint,
                checkpoint_name=checkpoint_name,
                cache_folder=self._cache_folder,
                device="auto",
            )
            self._initialized = True
            logger.info("TRIBE model loaded successfully")
            return True
        except Exception as exc:
            error_msg = str(exc)
            self._load_error = error_msg
            logger.error(f"Failed to load TRIBE model: {error_msg}")

            if "gated" in error_msg.lower() or "401" in error_msg:
                logger.info(
                    "TRIBE requires gated model access (Llama 3.2). Falling back to baseline mode."
                )
            elif "transformers" in error_msg.lower():
                logger.info(
                    "TRIBE requires transformers library. Falling back to baseline mode."
                )
            else:
                logger.info(
                    f"TRIBE load failed: {error_msg[:100]}. Falling back to baseline mode."
                )

            self._model = None
            self._initialized = False
            return False

    def predict_from_text(self, text: str) -> tuple[np.ndarray, list]:
        if not self._initialized or self._model is None:
            raise TribeInferenceError(
                "TRIBE model not loaded. Call load_model() first."
            )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(text)
            temp_path = f.name

        try:
            events = self._model.get_events_dataframe(text_path=temp_path)
            preds, segments = self._model.predict(events=events, verbose=False)
            return preds, segments
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def get_vertex_count(self) -> int:
        if not self._initialized or self._model is None:
            return 20484
        return self._model.brain_model_config.num_vertices

    def get_roi_vertex_indices(self, roi_name: str) -> list[int]:
        num_verts = self.get_vertex_count()
        return list(range(0, min(500, num_verts)))
