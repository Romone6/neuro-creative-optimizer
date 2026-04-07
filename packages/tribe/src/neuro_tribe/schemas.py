from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TribeRuntimeStatus(StrictModel):
    mode: Literal["baseline_only", "tribe_degraded", "tribe_enabled"]
    tribe_commit: str | None = None
    pretrained_load_ok: bool = False
    available_for_fusion: bool = False
    notes: list[str] = Field(default_factory=list)
    last_checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TribeAnalysisRequest(BaseModel):
    project_id: str
    content_type: str
    body: str
    title: str | None = None
    audience: dict


class BrainMeshRequest(BaseModel):
    project_id: str
    analysis_run_id: str | None = None


class BrainVertex(BaseModel):
    x: float
    y: float
    z: float


class BrainFace(BaseModel):
    a: int
    b: int
    c: int


class ROIData(BaseModel):
    name: str
    label: str
    activation: float
    vertex_indices: list[int]
    center: BrainVertex


class BrainMeshData(BaseModel):
    vertices: list[BrainVertex]
    faces: list[BrainFace]
    rois: list[ROIData]
    hemisphere: str


class BrainMeshResponse(BaseModel):
    mesh: BrainMeshData
    left_hemisphere: BrainMeshData
    right_hemisphere: BrainMeshData
    roi_labels: list[str]
