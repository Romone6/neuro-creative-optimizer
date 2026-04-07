## North star
Build a creative system that can simulate likely audience response and help produce meaningfully stronger content through iterative optimization.

## Phase 0 — Make setup real
Goal: ensure the project is buildable from a clean machine and does not depend on invisible local state.

Deliverables:
- scripted bootstrap for macOS/Linux and Windows
- Python 3.11+ validation
- TRIBE v2 clone/download automation
- dependency install flow
- model asset fetch attempt
- smoke test and status reporting
- degraded-mode fallback if TRIBE is unavailable

Success test:
A clean machine reaches a truthful working state with one documented setup command.

## Phase 1 — Build the credible core
Goal: prove the loop works for text.

Deliverables:
- text ingestion
- audience profiles
- base score dimensions
- explanation layer
- revision instructions
- generated variants
- reranking

Success test:
Users consistently prefer revised variants over originals for specified audience goals.

## Phase 2 — Build evaluation rigor
Goal: prove the system is not fooling itself.

Deliverables:
- human rating workflows
- A/B preference collection
- calibration metrics
- dimension-level validation
- experiment tracking

Success test:
Scores show meaningful alignment with human judgments and useful rank ordering.

## Phase 3 — Add TRIBE-backed enrichment
Goal: test whether brain-response priors improve the engine.

Deliverables:
- TRIBE adapter
- feature extraction experiments
- ablation tests
- score-delta studies
- contribution analysis

Success test:
TRIBE-backed features improve at least some target tasks versus baseline without harming explainability.

## Phase 4 — Add audio and lyrics
Goal: extend from pure text to musical/emotional pacing.

Deliverables:
- transcript/timing alignment
- acoustic feature ingestion
- lyric-aware scoring
- tension/release timeline analysis
- chorus/section comparison

Success test:
The system can diagnose and improve song sections in a way users judge as useful.

## Phase 5 — Build creative workstation quality
Goal: make the system fast and usable enough for repeated iteration.

Deliverables:
- project history
- reusable audience presets
- experiment notebooks / dashboards
- saved score profiles
- diff and change tracking

Success test:
A user actively chooses this tool as part of their creative drafting workflow.

## Phase 6 — Connect to an agentic content system
Goal: turn the engine into a gatekeeper and optimizer for autonomous content creation.

Deliverables:
- API for batch scoring
- generate-score-revise-rank loop
- approval workflow
- campaign-level comparison
- optional channel constraints per platform

Success test:
An upstream content agent can reliably use this engine to improve output quality before anything is published.

## Phase 7 — Commercial decision point
Goal: decide whether to keep this as a personal research system or push toward a real product.

Questions to answer:
- is the model stack materially better than baseline creative tooling?
- do users actually trust and use the scores?
- does the revision loop save enough time or improve enough quality?
- do licensing constraints force replacement of key components?

## Aggression level
This project should be built aggressively in terms of ambition, but disciplined in terms of validation.

Aggressive means:
- do not shrink the vision into a toy
- design every module for the end state
- build with real extensibility

Disciplined means:
- validate every score dimension
- keep uncertainty explicit
- measure improvement against humans
- prove usefulness before autonomy
