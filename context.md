# context.md

## Project identity
This project is a serious personal R&D build aimed at creating a **neuro-informed creative optimization engine**.
It should feel like a high-agency, research-grade system, not a toy demo.

## Project mission
Take a piece of writing, lyrics, audio, or later multimodal media, estimate how a target audience is likely to respond, explain why, and iteratively improve the content toward a chosen outcome.

## Mission in one line
**Predict likely audience response, then optimize the creative work accordingly.**

## Operational assumption
The project must be buildable from a cold start.
That means the coding agent must assume:
- no TRIBE v2 repo is present yet
- no TRIBE weights are cached yet
- no Python environment is ready yet
- no Node dependencies are installed yet
- no hidden local scripts exist yet

This matters because the build pack is supposed to drive actual implementation, not merely describe an end state.

## What this project is NOT
- not a fake mind-reading demo
- not a generic copywriter wrapper
- not a dashboard that only visualizes embeddings
- not a one-shot prompt hack
- not a universal emotion truth engine
- not a deceptive persuasion machine

## What makes it different
The system combines:
1. response estimation
2. audience conditioning
3. creative interpretation
4. revision and regeneration
5. iterative rescoring

That closed optimization loop is the product.

## Core assumptions
- TRIBE v2 is useful as a brain-response prior, but insufficient on its own.
- Human response should be treated as probabilistic and audience-dependent.
- The first working wedge should be text-first.
- The value comes from improving content, not from pretty neuroscience claims.
- The product must still have a usable baseline mode even if TRIBE integration is temporarily unavailable.

## Current desired end state
A creator can:
1. paste or upload content
2. choose an audience profile
3. choose desired target effects
4. receive a scored breakdown
5. generate improved variants
6. compare those variants
7. keep iterating until one version is clearly strongest

## Product philosophy
- build the most capable version that can still be validated
- do not hide behind small safe toy slices if they break the vision
- sequence aggressively, but rationally
- every module should point toward the end-state system
- avoid dead-end prototype code

## Tone and standard for the code agent
The coding agent must behave like a top-tier product-minded research engineer:
- ambitious
- skeptical
- explicit
- structured
- non-handwavy
- intolerant of fake certainty

## Permanent design instructions
- use typed contracts everywhere
- keep analysis outputs structured and inspectable
- store intermediate artifacts
- make the scoring system explainable
- make variants reproducible
- avoid coupling core logic to one model vendor
- design for later replacement of TRIBE-dependent components if commercialization is needed
- keep third-party setup scripted and repeatable

## Technical reality constraints
- the public TRIBE v2 stack is under a non-commercial license
- a later commercial path may require relicensing or replacement
- audience response dimensions must be calibrated against real human feedback
- scores should always carry uncertainty
- multimodal model setup may be brittle, so adapter isolation is mandatory

## Build priority
1. bootstrap reliability
2. usable scoring loop
3. meaningful revision loop
4. rigorous evaluation
5. TRIBE-backed enrichment
6. audio support
7. autonomous marketing-agent integration later
