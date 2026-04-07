# implementation.md

## 1. Objective
Build the first serious version of the neuro-informed creative optimization engine with a text-first architecture that can later support audio and multimodal input.

## 2. Mandatory setup principle
Implementation starts at zero.
The machine must be treated as if nothing project-critical already exists.
That means setup is part of the product work.

Specifically, the build must include:
- Python environment creation
- Node environment setup
- TRIBE v2 repository acquisition
- TRIBE v2 install and validation
- model asset retrieval/caching where required
- fallback behavior if TRIBE cannot yet run

## 3. Recommended stack
### Frontend
- Next.js
- TypeScript
- Tailwind
- shadcn/ui

### Backend
- Python for ML/scoring services
- FastAPI for model/scoring API
- Node/Next API only if needed for app glue

### Storage
- Postgres / Supabase
- object storage for artifacts

### ML / orchestration
- Python
- PyTorch where needed
- Hugging Face integration for model adapters
- optional background workers for longer analysis jobs

## 4. Core services
### Service A: bootstrap-service
Responsibilities:
- verify Python 3.11+
- create virtual environment
- clone or update `facebookresearch/tribev2`
- install TRIBE package and optional extras as required
- trigger initial pretrained asset fetch
- run smoke tests
- emit setup status JSON

### Service B: ingest-service
Responsibilities:
- accept inputs
- normalize content
- segment content
- emit structured assets

### Service C: feature-service
Responsibilities:
- generate feature bundles
- lexical/statistical features
- embeddings
- structural metadata

### Service D: response-service
Responsibilities:
- produce score vectors
- integrate TRIBE-backed features later or when available
- run audience-conditioned scoring

### Service E: revision-service
Responsibilities:
- generate edit instructions
- generate revised variants
- rerank variants after rescoring

### Service F: evaluation-service
Responsibilities:
- capture human ratings
- compute correlations
- compare variants
- track experiment quality

## 5. Suggested schema objects
- setup_run
- dependency_status
- content_asset
- content_segment
- audience_profile
- analysis_run
- score_dimension
- score_value
- revision_plan
- variant_asset
- evaluation_result
- experiment_run

## 6. Suggested repo layout
```text
/apps
  /web
  /api
  /worker
/packages
  /core-types
  /bootstrap
  /feature-pipeline
  /response-engine
  /tribe-adapter
  /llm-orchestrator
  /audience-model
  /evaluation
  /prompts
  /storage
/third_party
  /tribev2          # cloned external dependency, pinned to a commit
/scripts
  bootstrap.sh
  bootstrap.ps1
  smoke_test_tribe.py
/docs
  thesis.md
  scope.md
  architecture.md
  context.md
  agent.md
  implementation.md
  roadmap.md
  bootstrap.md
```

## 7. Build phases
### Phase -1 — Bootstrap and validation
Deliverables:
- monorepo scaffold
- Python 3.11+ validation
- dependency manifest
- TRIBE v2 clone into `third_party/tribev2`
- editable install flow
- smoke test that attempts pretrained inference
- documented fallback mode if TRIBE path is unavailable

Success condition:
A fresh machine can run one setup command and get a truthful status report.

### Phase 0 — Foundation
Deliverables:
- base schemas
- API contracts
- local dev environment
- artifact storage model
- setup status page or CLI output

### Phase 1 — Text analysis MVP
Deliverables:
- text upload/paste
- segmentation
- initial score engine
- analysis report JSON
- minimal compare UI

### Phase 2 — Revision loop
Deliverables:
- target response selection
- revision instructions
- automatic variants
- variant reranking
- side-by-side compare

### Phase 3 — Evaluation backbone
Deliverables:
- human rating capture
- experiment dashboards
- preference tests
- score calibration utilities

### Phase 4 — TRIBE integration hardening
Deliverables:
- adapter for TRIBE-backed features
- experimental scoring comparison
- feature ablation tests
- contribution analysis
- retry/cache logic for model assets

### Phase 5 — Audio path
Deliverables:
- transcript + timing
- acoustic features
- audio-aware segment scoring

### Phase 6 — Agent integration
Deliverables:
- content generation agent hooks
- batch variant generation
- approve/reject workflow
- optional posting integration later

## 8. Engineering rules
- all core interfaces typed
- all score objects versioned
- all prompt templates versioned
- every generated variant traceable to source input and target deltas
- every model call logged with metadata
- every analysis run reproducible where possible
- every external dependency pinned where possible
- every bootstrap step must be scriptable

## 9. TRIBE setup strategy
The correct integration pattern is:
1. pin a known TRIBE v2 commit
2. clone it into `third_party/tribev2`
3. install it in editable mode
4. keep all direct TRIBE calls inside `packages/tribe-adapter`
5. wrap all failures in explicit status objects
6. never let the rest of the product crash because TRIBE is unavailable

Do not scatter TRIBE imports across the codebase.
Do not make the entire application depend on successful neuroscience-model setup.

## 10. Scoring engine v1 strategy
Do not wait for perfect neuroscience integration.
Build v1 scoring from:
- lexical and structural features
- embedding similarity and contrast features
- handcrafted persuasion / writing heuristics
- LLM grounded interpretation
- audience profile modifiers

Then later test whether TRIBE-derived signals actually improve performance.

## 11. LLM revision strategy
The revision loop should be constraint-driven.
Input to the LLM should include:
- original content
- scored weaknesses
- target audience
- desired target deltas
- length/style constraints
- keep/change instructions

The LLM should output:
- revision rationale
- changed version
- concise diff summary

## 12. UI strategy
The UI should be built around three panes:
1. original content
2. score and explanation layer
3. revised variants and rankings

Optional later:
- setup status dashboard
- score timeline chart
- segment heatmap
- audience profile explorer
- campaign asset grid

## 13. Failure conditions
The implementation is failing if:
- outputs are generic
- scores cannot be explained
- variants are not measurably better
- the system cannot compare versions well
- model-specific code contaminates the whole codebase
- setup depends on hidden manual intervention

## 14. Success criteria for first serious build
A user can:
- run bootstrap from a clean machine
- confirm whether TRIBE is working or degraded
- paste text
- choose an audience
- get useful scores
- ask for stronger trust/clarity/urgency/etc.
- receive multiple revised variants
- compare them
- clearly see why one version is best
