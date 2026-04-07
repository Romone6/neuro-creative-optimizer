from __future__ import annotations

from pydantic import BaseModel, Field


class CommercialCriterion(BaseModel):
    name: str
    status: str
    note: str


class CommercialDecisionReport(BaseModel):
    project_id: str
    recommendation: str
    summary: str
    blockers: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    criteria: list[CommercialCriterion] = Field(default_factory=list)
