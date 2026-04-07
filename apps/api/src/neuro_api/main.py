from __future__ import annotations

import json
import platform
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from neuro_agent import (
    AgentApprovalRequest,
    AgentWorkflowService,
    BatchScoreRequest,
    AgentCampaignRequest,
)
from neuro_analysis import (
    AnalysisService,
    AudienceProfileInput,
    AudienceService,
    IngestionService,
    OptimizationService,
    TextAnalysisRequest,
    TextIngestionRequest,
    TextOptimizationRequest,
    VariantGenerationService,
)
from neuro_audio import AudioAnalysisRequest, AudioAnalysisService
from neuro_bootstrap.status import build_setup_status
from neuro_core.llm import ChatExecutionRequest, ChatExecutionResponse, ChatMessage
from neuro_decision import CommercialDecisionService
from neuro_evaluation import EvaluationService, TextEvaluationRequest
from neuro_llm import (
    ProviderExecutionError,
    ProviderRegistry,
    ProviderService,
    ProviderSettings,
)
from neuro_prompts import PromptRegistry, PromptRoutingPolicy, RoutingRequest
from neuro_tribe import TribeAnalysisRequest, TribeAnalysisService
from neuro_tribe.analysis import TribeUnavailableError
from neuro_tribe.brain_mesh import BrainMeshService
from neuro_workbench import AudiencePresetRequest, WorkbenchService

app = FastAPI(title="Neuro Creative Optimizer API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
registry = ProviderRegistry.default()
PROJECT_ROOT = Path(__file__).resolve().parents[4]
provider_service = ProviderService(registry=registry, settings=ProviderSettings())
ingestion_service = IngestionService()
audience_service = AudienceService()
prompt_registry = PromptRegistry.default()
prompt_policy = PromptRoutingPolicy(ProviderSettings())
analysis_service = AnalysisService(
    ingestion_service=ingestion_service,
    audience_service=audience_service,
)
variant_generation_service = VariantGenerationService(
    provider_service=provider_service,
    prompt_registry=prompt_registry,
    prompt_policy=prompt_policy,
)
optimization_service = OptimizationService(
    analysis_service=analysis_service,
    variant_generation_service=variant_generation_service,
)
evaluation_service = EvaluationService(analysis_service=analysis_service)
tribe_analysis_service = TribeAnalysisService(
    repo_root=PROJECT_ROOT,
)
brain_mesh_service = BrainMeshService()
audio_analysis_service = AudioAnalysisService(text_analysis_service=analysis_service)
workbench_service = WorkbenchService(
    repo_root=PROJECT_ROOT,
    optimization_service=optimization_service,
    evaluation_service=evaluation_service,
)
agent_workflow_service = AgentWorkflowService(
    repo_root=PROJECT_ROOT,
    analysis_service=analysis_service,
    optimization_service=optimization_service,
)
commercial_decision_service = CommercialDecisionService(
    repo_root=PROJECT_ROOT,
    workbench_service=workbench_service,
)


class GenericChatRequest(BaseModel):
    provider: str
    model: str
    messages: list[ChatMessage]
    max_output_tokens: int | None = None


class ProviderChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    max_output_tokens: int | None = None


class PromptRenderRequest(BaseModel):
    task_type: str
    variables: dict[str, str]


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/llm/providers")
def list_providers() -> dict[str, list[dict[str, str | None]]]:
    return {"providers": [provider.model_dump() for provider in registry.list()]}


@app.get("/v1/setup/status")
def get_setup_status() -> dict[str, str | bool | None]:
    status = build_setup_status(
        repo_root=PROJECT_ROOT,
        python_version=platform.python_version(),
        tribe_install_ok=False,
        pretrained_load_ok=False,
        smoke_test_ok=False,
    )
    return status.model_dump()


def get_provider_service() -> ProviderService:
    return provider_service


def get_ingestion_service() -> IngestionService:
    return ingestion_service


def get_audience_service() -> AudienceService:
    return audience_service


def get_prompt_registry() -> PromptRegistry:
    return prompt_registry


def get_prompt_policy() -> PromptRoutingPolicy:
    return prompt_policy


def get_analysis_service() -> AnalysisService:
    return analysis_service


def get_optimization_service() -> OptimizationService:
    return optimization_service


def get_evaluation_service() -> EvaluationService:
    return evaluation_service


def get_tribe_analysis_service() -> TribeAnalysisService:
    return tribe_analysis_service


def get_audio_analysis_service() -> AudioAnalysisService:
    return audio_analysis_service


def get_workbench_service() -> WorkbenchService:
    return workbench_service


def get_agent_workflow_service() -> AgentWorkflowService:
    return agent_workflow_service


def get_commercial_decision_service() -> CommercialDecisionService:
    return commercial_decision_service


@app.post("/v1/llm/chat", response_model=ChatExecutionResponse)
def chat(request: GenericChatRequest) -> ChatExecutionResponse:
    try:
        return get_provider_service().execute(
            ChatExecutionRequest(**request.model_dump())
        )
    except ProviderExecutionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc


@app.post(
    "/v1/llm/providers/{provider_name}/chat", response_model=ChatExecutionResponse
)
def provider_chat(
    provider_name: str, request: ProviderChatRequest
) -> ChatExecutionResponse:
    try:
        return get_provider_service().execute(
            ChatExecutionRequest(provider=provider_name, **request.model_dump())
        )
    except ProviderExecutionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc


@app.post("/v1/assets/ingest/text")
def ingest_text(request: TextIngestionRequest):
    try:
        return get_ingestion_service().ingest_text(request).model_dump()
    except Exception as exc:
        status_code = getattr(exc, "status_code", 500)
        code = getattr(exc, "code", "ingestion_failed")
        raise HTTPException(
            status_code=status_code, detail={"code": code, "message": str(exc)}
        ) from exc


@app.post("/v1/audiences/validate")
def validate_audience(request: AudienceProfileInput):
    return get_audience_service().validate_profile(request).model_dump()


@app.post("/v1/policy/route")
def route_policy(request: RoutingRequest):
    return get_prompt_policy().select_route(request).model_dump()


@app.post("/v1/prompts/render")
def render_prompt(request: PromptRenderRequest):
    return (
        get_prompt_registry()
        .render(
            task_type=request.task_type,
            variables=request.variables,
        )
        .model_dump()
    )


@app.post("/v1/analyze/text")
def analyze_text(request: TextAnalysisRequest):
    return get_analysis_service().analyze_text(request).model_dump()


@app.post("/v1/analyze/text/tribe")
def analyze_text_with_tribe(request: TribeAnalysisRequest):
    try:
        return get_tribe_analysis_service().analyze_text(request).model_dump()
    except TribeUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "tribe_unavailable",
                "message": str(exc),
                "mode": exc.mode,
                "notes": exc.notes,
            },
        ) from exc


@app.post("/v1/analyze/text/brain-activation")
def analyze_text_brain_activation(request: TextAnalysisRequest):
    analysis_result = get_analysis_service().analyze_text(request)
    scores = [
        score.model_dump() for score in analysis_result.analysis_run.score_vector.scores
    ]
    roi_activations = get_tribe_analysis_service().map_scores_to_rois(scores)
    return {
        "analysis": analysis_result.model_dump(),
        "roi_activations": [roi.model_dump() for roi in roi_activations],
    }


@app.post("/v1/analyze/audio")
def analyze_audio(request: AudioAnalysisRequest):
    return get_audio_analysis_service().analyze(request).model_dump()


@app.post("/v1/analyze/audio/file")
async def analyze_audio_file(
    project_id: str = Form(...),
    content_type: str = Form(...),
    title: Optional[str] = Form(None),
    audience: str = Form(...),
    file: UploadFile = File(...),
):
    audio_request = AudioAnalysisRequest(
        project_id=project_id,
        content_type=content_type,
        transcript="",  # Would need audio transcription
        sections=[],  # Would need audio analysis
        audience=json.loads(audience),
        title=title,
    )
    return get_audio_analysis_service().analyze(audio_request).model_dump()


@app.post("/v1/analyze/video")
async def analyze_video(
    project_id: str = Form(...),
    content_type: str = Form(...),
    title: Optional[str] = Form(None),
    audience: str = Form(...),
    file: UploadFile = File(...),
):
    return {
        "status": "video_analysis_pending",
        "message": "Video analysis endpoint - requires video processing pipeline",
        "project_id": project_id,
    }


@app.post("/v1/workbench/audience-presets")
def save_audience_preset(request: AudiencePresetRequest):
    return (
        get_workbench_service()
        .save_audience_preset(
            project_id=request.project_id,
            preset_name=request.preset_name,
            audience=request.audience,
        )
        .model_dump()
    )


@app.post("/v1/workbench/optimize/text")
def workbench_optimize_text(request: TextOptimizationRequest):
    return get_workbench_service().record_optimization(request).model_dump()


@app.post("/v1/workbench/evaluate/text")
def workbench_evaluate_text(request: TextEvaluationRequest):
    return get_workbench_service().record_evaluation(request).model_dump()


@app.get("/v1/workbench/projects/{project_id}/dashboard")
def workbench_dashboard(project_id: str):
    return get_workbench_service().get_project_dashboard(project_id).model_dump()


@app.post("/v1/agent/batch/score")
def agent_batch_score(request: BatchScoreRequest):
    return get_agent_workflow_service().batch_score(request).model_dump()


@app.post("/v1/agent/campaign/optimize")
def agent_campaign_optimize(request: AgentCampaignRequest):
    return get_agent_workflow_service().optimize_campaign(request).model_dump()


@app.post("/v1/agent/approval")
def agent_record_approval(request: AgentApprovalRequest):
    return get_agent_workflow_service().record_approval(request).model_dump()


@app.get("/v1/brain/mesh")
def get_brain_mesh(hemisphere: str = "both", resolution: str = "fsaverage5"):
    try:
        if resolution == "fsaverage6":
            mesh_data = brain_mesh_service.load_fsaverage6_mesh(hemisphere)
        else:
            mesh_data = brain_mesh_service.load_fsaverage5_mesh(hemisphere)
        return {
            "vertices": [v.model_dump() for v in mesh_data.mesh.vertices],
            "faces": [f.model_dump() for f in mesh_data.mesh.faces],
            "roiLabels": mesh_data.roi_labels,
            "rois": [r.model_dump() for r in mesh_data.mesh.rois],
            "hemisphere": hemisphere,
            "resolution": resolution,
            "vertexCount": len(mesh_data.mesh.vertices),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail={"code": "mesh_error", "message": str(exc)}
        ) from exc


@app.get("/v1/decision/commercial-readiness/{project_id}")
def commercial_readiness(project_id: str):
    return get_commercial_decision_service().assess_project(project_id).model_dump()


@app.post("/v1/optimize/text")
def optimize_text(request: TextOptimizationRequest):
    return get_optimization_service().optimize_text(request).model_dump()


@app.post("/v1/evaluate/text")
def evaluate_text(request: TextEvaluationRequest):
    return get_evaluation_service().evaluate_text(request).model_dump()
