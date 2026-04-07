# Architecture Strategy

## 1. System overview
The system is a layered pipeline, not a single model.

```text
Input Content
  -> Preprocessing / Segmentation
  -> Feature Extraction
  -> Brain-Response Prior Layer (TRIBE-inspired or TRIBE-backed)
  -> Response Interpretation Layer
  -> Audience Conditioning Layer
  -> Scoring Engine
  -> LLM Reasoning + Revision Engine
  -> Variant Generation
  -> Re-scoring and Ranking
  -> Report + Artifact Storage
```

## 2. Core architecture principle
TRIBE v2 should not be treated as the whole product.
It should be treated as one part of a broader response-modeling stack.

## 3. Main layers

### A. Content ingestion layer
Responsibilities:
- accept text, lyrics, audio, later video
- normalize formats
- chunk long inputs into interpretable segments
- preserve metadata

For text:
- sentence segmentation
- paragraph segmentation
- rhetorical block extraction

For audio:
- transcript generation
- timing extraction
- acoustic feature alignment

### B. Feature extraction layer
Outputs should include:
- semantic embeddings
- stylistic embeddings
- structural metadata
- rhythm / pacing markers
- lexical density
- repetition patterns
- sentiment priors
- acoustic embeddings for audio

Possible stack:
- text encoder
- audio encoder
- handcrafted writing features
- handcrafted music structure features

### C. Brain-response prior layer
This is where TRIBE v2 or a compatible surrogate sits.

Purpose:
- estimate response structure over time
- identify salience and cortical-response dynamics
- provide a nontrivial multimodal representation for downstream interpretation

Use cases:
- map content segments to predicted neural-response signatures
- compare signatures across variants
- derive interpretable summary statistics

Important rule:
Never present raw TRIBE output as direct emotion truth.

### D. Response interpretation layer
This layer translates low-level signals into working creative dimensions.

Methods can include:
- regression heads
- small task-specific classifiers
- rubric-based feature synthesis
- learned mapping from human ratings to latent features
- hybrid symbolic + learned rules

This layer outputs dimensions like:
- clarity
- tension
- trust
- warmth
- novelty
- momentum
- memorability

### E. Audience conditioning layer
The same piece of content lands differently for different audiences.
This layer adjusts scoring based on audience profile.

Mechanisms:
- persona embeddings
- conditioning prompts
- calibration weights by segment
- prior distributions from audience feedback history

### F. LLM reasoning and revision layer
The LLM should not invent analysis from scratch.
It must work from structured scores and evidence.

Inputs:
- content
- target audience
- current score breakdown
- target score profile
- constraints

Outputs:
- explanation
- edits
- variant drafts
- change rationale

### G. Evaluation and ranking layer
Every generated variant is rescored.
The system ranks candidates by:
- target-dimension improvement
- constraint satisfaction
- originality preservation
- readability/listenability
- downside risk

## 4. Data model
Main entities:
- Project
- Asset
- Segment
- AudienceProfile
- AnalysisRun
- ScoreVector
- RevisionInstruction
- Variant
- EvaluationReport
- Experiment

## 5. Suggested repo modules
```text
/apps
  /web
  /api
  /worker
/packages
  /core-types
  /scoring-engine
  /tribe-adapter
  /feature-pipeline
  /llm-orchestrator
  /audience-model
  /evaluation
  /prompts
  /storage
/docs
  thesis.md
  architecture.md
  agent.md
```

## 6. Scoring logic
Each score should contain:
- value
- confidence
- evidence span(s)
- explanation
- target delta

Example:
```json
{
  "dimension": "trust",
  "score": 0.61,
  "confidence": 0.72,
  "evidence": ["para_2", "para_4"],
  "reason": "Strong specificity and moderate certainty, but weakened by overclaiming in the opener.",
  "target": 0.78
}
```

## 7. Evaluation strategy
The system must be measured on:
- correlation with human ratings
- agreement on weak/strong segments
- quality of revision improvements
- ability to rank variants correctly
- calibration of confidence
- stability across reruns

## 8. Suggested build order
1. text ingestion
2. deterministic feature extraction
3. basic scoring engine without TRIBE
4. LLM explanation and revision loop
5. human rating collection
6. TRIBE integration as prior/signal source
7. better calibration
8. audio path
9. multimodal path

This order matters.
If you start with the hardest neuroscience component first, you will slow the project for no reason.
