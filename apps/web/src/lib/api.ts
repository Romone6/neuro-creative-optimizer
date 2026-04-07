"use client";

export type Modality = "text" | "audio" | "video";

export type SignalMetric = {
  id: string;
  label: string;
  value: number;
  confidence: number;
  delta?: number;
  interpretation: string;
  evidence: string[];
  revision: string[];
  anchor: { x: number; y: number; region: string; lobe: string };
  sourceType?: string;
};

export type WorkspaceResult = {
  runType: Modality;
  summary: string;
  detailSummary: string;
  runtimeLabel: string;
  audienceLabel: string;
  sourceExcerpt: string;
  selectedAssetTitle: string;
  selectedContentLabel: string;
  revisionNotes: string[];
  signals: SignalMetric[];
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

const ANCHOR_MAP: Record<string, { x: number; y: number; region: string; lobe: string }> = {
  trust: { x: 18, y: 28, region: "medial prefrontal cortex", lobe: "frontal" },
  clarity: { x: 22, y: 52, region: "wernicke's area", lobe: "temporal" },
  urgency: { x: 30, y: 75, region: "amygdala", lobe: "limbic" },
  novelty: { x: 78, y: 25, region: "lateral prefrontal cortex", lobe: "frontal" },
  tension: { x: 45, y: 42, region: "anterior cingulate cortex", lobe: "frontal" },
  narrative_momentum: { x: 68, y: 68, region: "hippocampus", lobe: "temporal" },
  cognitive_load: { x: 28, y: 35, region: "dorsolateral prefrontal cortex", lobe: "frontal" },
  memorability: { x: 35, y: 22, region: "orbitofrontal cortex", lobe: "frontal" },
  emotional_engagement: { x: 52, y: 70, region: "amygdala / ventral striatum", lobe: "limbic" },
  memory_encoding: { x: 72, y: 55, region: "hippocampus", lobe: "temporal" },
  attention_focus: { x: 42, y: 30, region: "superior parietal lobule", lobe: "parietal" },
  reward_response: { x: 58, y: 78, region: "nucleus accumbens", lobe: "limbic" },
  processing_speed: { x: 25, y: 58, region: "broca's area", lobe: "temporal" },
  visual_imagery: { x: 85, y: 35, region: "visual cortex", lobe: "occipital" },
  auditory_processing: { x: 75, y: 45, region: "auditory cortex", lobe: "temporal" },
  decision_confidence: { x: 48, y: 25, region: "anterior cingulate", lobe: "frontal" },
  arousal_level: { x: 38, y: 68, region: "hypothalamus / brainstem", lobe: "limbic" },
};

type SetupStatusResponse = {
  mode: string;
  pretrained_load_ok: boolean;
  smoke_test_ok: boolean;
};

type TextAnalysisResponse = {
  asset: { body: string; title?: string | null; content_type: string };
  audience_profile: { label: string };
  report: { summary: string; risk_flags: string[] };
  analysis_run: {
    score_vector: {
      scores: Array<{
        dimension: string;
        value: number;
        confidence: number;
        explanation: string;
        evidence: Array<{ quote?: string | null; reason: string }>;
      }>;
    };
  };
};

export type ROIActivation = {
  name: string;
  label: string;
  activation: number;
  vertex_indices: number[];
  center: { x: number; y: number; z: number };
};

export type BrainActivationResponse = {
  analysis: TextAnalysisResponse;
  roi_activations: ROIActivation[];
};

export async function runAnalysis(input: {
  projectId: string;
  title?: string;
  content: string;
  modality: Modality;
}): Promise<WorkspaceResult> {
  const [statusResponse, analysisResponse] = await Promise.all([
    fetch(`${API_BASE_URL}/v1/setup/status`),
    fetch(`${API_BASE_URL}/v1/analyze/text/brain-activation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_id: input.projectId,
        content_type: "speech",
        title: input.title ?? "Submitted text",
        body: input.content,
        audience: {
          label: "General audience",
          platform_context: "general",
          target_goals: [
            { dimension: "trust", target_value: 0.82, priority: 1 },
            { dimension: "clarity", target_value: 0.8, priority: 2 },
          ],
        },
      }),
    }),
  ]);

  if (!analysisResponse.ok) {
    const payload = (await analysisResponse.json().catch(() => null)) as
      | { detail?: { message?: string } }
      | null;
    throw new Error(payload?.detail?.message ?? "Text analysis failed.");
  }

  if (!statusResponse.ok) {
    throw new Error("Setup status could not be loaded.");
  }

  const statusPayload = (await statusResponse.json()) as SetupStatusResponse;
  const payload = (await analysisResponse.json()) as BrainActivationResponse;
  
  const tribeStatusLabel =
    statusPayload.mode === "tribe_enabled"
      ? "TRIBE inference active"
      : `Baseline analysis · ${statusPayload.mode}`;

  return {
    runType: input.modality,
    summary: payload.analysis.report.summary,
    detailSummary: payload.analysis.report.summary,
    runtimeLabel: `Neural response mapped · ${tribeStatusLabel}`,
    audienceLabel: payload.analysis.audience_profile.label,
    sourceExcerpt: payload.analysis.asset.body,
    selectedAssetTitle: payload.analysis.asset.title ?? "Submitted text",
    selectedContentLabel: "Text input",
    revisionNotes: payload.analysis.report.risk_flags.length
      ? payload.analysis.report.risk_flags
      : ["Use the revision loop to intensify the strongest signal or stabilize the weakest one."],
    signals: payload.analysis.analysis_run.score_vector.scores.map((score) => ({
      id: score.dimension,
      label: formatSignalLabel(score.dimension),
      value: score.value,
      confidence: score.confidence,
      interpretation: score.explanation,
      evidence: score.evidence.map((item) => item.quote ?? item.reason).filter(Boolean),
      revision: payload.analysis.report.risk_flags.length
        ? payload.analysis.report.risk_flags
        : ["Request a targeted revision around this signal from the operator console."],
      anchor: ANCHOR_MAP[score.dimension] ?? fallbackAnchor(score.dimension),
      sourceType: "text",
    })),
  };
}

function formatSignalLabel(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function fallbackAnchor(seed: string) {
  const hash = Array.from(seed).reduce((total, char) => total + char.charCodeAt(0), 0);
  return {
    x: 18 + (hash % 64),
    y: 18 + ((hash * 7) % 64),
    region: "association cortex",
    lobe: "frontal",
  };
}

export type BrainMeshData = {
  vertices: Array<{ x: number; y: number; z: number }>;
  faces: Array<{ a: number; b: number; c: number }>;
  roiLabels: string[];
  rois: Array<{
    name: string;
    label: string;
    activation: number;
    vertex_indices: number[];
    center: { x: number; y: number; z: number };
  }>;
  hemisphere: string;
  resolution?: string;
  vertexCount?: number;
};

export async function fetchBrainMesh(hemisphere: string = "both", resolution: string = "fsaverage5"): Promise<BrainMeshData> {
  const response = await fetch(`${API_BASE_URL}/v1/brain/mesh?hemisphere=${hemisphere}&resolution=${resolution}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch brain mesh: ${response.statusText}`);
  }
  return response.json();
}
