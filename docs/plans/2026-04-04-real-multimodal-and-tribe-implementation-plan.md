# Real Multimodal and TRIBE Implementation Plan

## Purpose
This document defines the implementation plan for the remaining real product work after placeholder removal.

The goal is to turn the project from:
- baseline text analysis plus honest TRIBE-unavailable reporting

Into:
- real multimodal ingestion
- real media-backed analysis
- real TRIBE-enabled inference when verified
- honest UI states for every runtime condition
- a clinically minimal frontend that only exposes working capabilities

## Current Baseline

### Working Now
- baseline text analysis
- optimization and revision loop
- evaluation pipeline
- setup/runtime status reporting
- honest frontend state for text-only analysis
- TRIBE refusal path when live inference is unavailable

### Not Yet Implemented
- file upload for audio
- file upload for video
- persistent media artifacts
- transcript extraction from uploaded media
- video frame analysis
- live TRIBE inference integration
- verified anatomical brain visualization tied to real signals

## Implementation Principles

### 1. No implied capability
If a feature is not backed by a real endpoint and verified runtime behavior, it must not appear active in the product.

### 2. Baseline and TRIBE stay separate
Baseline analysis remains usable on its own.
TRIBE is an enhancement layer, not the only path and not a hidden heuristic overlay.

### 3. Multimodal work is artifact-first
The system should not analyze raw browser state. It should ingest files, persist artifacts, extract derived assets, and then analyze those assets.

### 4. UI reflects system truth
The frontend should show one of these states explicitly:
- baseline available
- TRIBE available
- TRIBE unavailable
- upload unavailable
- processing in progress
- analysis complete

## Workstreams

## Workstream A: Real Upload and Artifact Pipeline

### Objective
Add real upload-backed ingestion for audio and video.

### Scope
- multipart upload endpoints
- local artifact storage abstraction
- upload metadata records
- media validation
- persisted references for downstream processing

### Backend Modules
- new upload service package
- API routes for audio upload
- API routes for video upload
- storage adapter for local development
- artifact manifest schema

### Required Outputs
- uploaded file ID
- content type
- original filename
- artifact path or storage URI
- duration when detectable
- processing status

### Acceptance Criteria
- the frontend can upload a real audio file
- the frontend can upload a real video file
- the backend stores a stable artifact record
- the API returns a real artifact identifier
- unsupported file types fail cleanly

## Workstream B: Audio and Video Derivation Pipeline

### Objective
Create real derived assets from uploaded media instead of proxying through text.

### Audio Derivations
- transcript extraction
- timing alignment
- duration and section metadata
- optional diarization hooks later

### Video Derivations
- audio extraction from video
- transcript extraction from extracted audio
- keyframe sampling
- scene boundary approximation
- media metadata extraction

### Backend Modules
- transcription service wrapper
- ffmpeg-based extraction pipeline
- artifact lineage recording
- processing job status service

### Acceptance Criteria
- uploaded audio produces a transcript artifact and timing data
- uploaded video produces extracted audio, transcript, and keyframes
- each derived asset is linked to the original artifact
- failures are surfaced with explicit stage-level status

## Workstream C: Multimodal Analysis Layer

### Objective
Analyze text, audio, and video through real modality-specific pipelines.

### Text
- keep current baseline text analysis path

### Audio
- use transcript plus real section/timing metadata
- score pacing, contrast, emphasis, hook strength, emotional pacing

### Video
- combine transcript with visual scene descriptors
- answer operator prompts like:
  - what is the audience likely feeling from this video
  - where does the reaction intensify
  - which scene or spoken line drives the response

### Required Model Behavior
- no mandatory target audience selection
- default interpretation is general audience
- operator prompt can add context explicitly

### Acceptance Criteria
- audio analysis operates on uploaded audio artifacts
- video analysis operates on uploaded video artifacts
- the output names the source modality honestly
- evidence points back to timestamps, transcript segments, or scenes

## Workstream D: Real TRIBE Integration

### Objective
Replace refusal-only TRIBE status with real TRIBE-backed analysis when the runtime truly supports it.

### Required Preconditions
- runtime reaches `tribe_enabled`
- full inference path is verified
- request/response contract is stable
- latency and failure modes are known

### Implementation Tasks
- identify the exact TRIBE inference entrypoint to call
- build a dedicated runtime wrapper around the real call
- define the actual TRIBE output contract the app will consume
- map only verified TRIBE outputs into the app
- keep refusal behavior when the runtime is not actually ready

### Non-Goals
- no heuristic proxy dressed up as TRIBE
- no partial fusion pretending to be biological evidence

### Acceptance Criteria
- TRIBE endpoint returns real runtime-backed output
- degraded mode still refuses cleanly
- output provenance explicitly states it came from live TRIBE inference

## Workstream E: Signal Mapping and Brain Visualization

### Objective
Reintroduce the brain stage only when it is tied to real assets and real signal mapping.

### Required Inputs
- high-detail anatomical brain asset
- defined mapping between supported signals and displayed regions
- explicit distinction between:
  - baseline model signals
  - TRIBE-backed region activations

### UI Rules
- if only baseline analysis exists, do not show faux TRIBE region activation
- if TRIBE is unavailable, show status, not anatomy theater
- if TRIBE is available, show only verified mapped regions

### Acceptance Criteria
- brain asset is real and high-detail
- signal overlays correspond to documented mappings
- UI copy distinguishes baseline signal view from TRIBE view

## Workstream F: Operator Experience and Prompt Flow

### Objective
Make the interaction model fit the intended use case:
- upload media
- ask what the audience is likely feeling
- inspect evidence
- optionally revise or compare

### UI Changes
- add real upload controls for audio and video
- keep text entry available
- maintain bottom-composer-first workflow
- default audience mode to general audience
- move advanced audience controls behind explicit optional UI later

### Chat/Operator Behaviors
- operator can ask general-response questions directly
- analysis summaries should mirror the operator’s modality
- errors should explain missing runtime capability plainly

### Acceptance Criteria
- user can submit text, audio, or video from one operator surface
- the UI clearly shows processing, analysis, and unavailable states
- no hidden hardcoded audience assumptions are injected as if chosen by the user

## Workstream G: Runtime Truth and Observability

### Objective
Make capability state inspectable for both users and developers.

### Required Status Surfaces
- upload pipeline readiness
- transcription readiness
- video extraction readiness
- TRIBE runtime readiness
- baseline analysis readiness

### Required Outputs
- machine-readable status endpoint additions
- UI status labels
- artifact-level processing logs

### Acceptance Criteria
- every major subsystem has an inspectable readiness state
- user-facing failures correspond to real backend conditions

## Recommended Execution Order

### Phase 1
Implement upload and artifact storage.

### Phase 2
Implement transcription and media derivation.

### Phase 3
Wire real audio and video analysis to uploaded artifacts.

### Phase 4
Integrate real TRIBE runtime inference behind a strict capability gate.

### Phase 5
Reintroduce the brain visualization only after verified region mapping exists.

### Phase 6
Refine the operator workflow and clinical frontend around the now-real backend surfaces.

## Deliverables by Phase

### Phase 1 Deliverables
- upload API
- artifact schemas
- local storage adapter
- upload status UI

### Phase 2 Deliverables
- transcript extraction pipeline
- video audio extraction
- keyframe generation
- derivation status tracking

### Phase 3 Deliverables
- audio analysis endpoint on real uploads
- video analysis endpoint on real uploads
- evidence-linked modality-specific output

### Phase 4 Deliverables
- real TRIBE wrapper
- verified TRIBE response contract
- TRIBE-enabled endpoint behavior
- degraded refusal retained when needed

### Phase 5 Deliverables
- anatomical brain asset
- verified signal mapping spec
- honest TRIBE/baseline rendering split

### Phase 6 Deliverables
- final operator console
- upload-first multimodal workflow
- evidence and signal inspection UI

## Definition of Done
The remaining implementation is complete when:
- text, audio, and video all use real ingestion paths
- no modality relies on browser-side proxies
- TRIBE either runs for real or says it is unavailable
- the frontend does not visualize unverifiable biology
- all active UI controls correspond to live backend features

## Immediate Next Step
Start with Workstream A.

That means:
1. define upload schemas
2. add upload endpoints
3. add artifact storage
4. expose upload status in the API

Until that exists, multimodal implementation is blocked at the correct place.
