# Neuro-Informed Creative Optimization Engine

This pack turns the concept into an actionable product and build system for an AI-assisted personal project.

## Files
- `thesis.md` — core thesis, product doctrine, strategic framing, constraints
- `scope.md` — complete project scope, modules, inputs/outputs, non-goals
- `architecture.md` — system architecture, data flows, model stack, evaluation strategy
- `agent.md` — master operating instructions for Claude/Codex-style coding agents
- `context.md` — project context the agent must understand before coding
- `implementation.md` — build strategy, milestones, engineering rules, repo structure
- `roadmap.md` — phased roadmap from local prototype to autonomous creative system
- `bootstrap.md` — mandatory environment and dependency acquisition plan, including TRIBE v2 setup

## Core principle
This project does **not** claim perfect mind-reading.
It aims to estimate **likely audience response patterns** from writing, music, and multimodal content, then use an LLM-based revision loop to improve the content toward a chosen target effect.

## Strategic framing
The winning version of this project is:
- a **creative response simulator**
- a **neuro-informed revision engine**
- an **audience-fit optimizer**

The losing version is:
- a fake universal emotion detector
- a manipulative "brain hacking" product
- an overbuilt research fantasy with no usable workflow

## Mandatory build assumption
The coding agent must assume a **clean machine**.
Nothing critical is preinstalled, predownloaded, or already configured.
That includes:
- TRIBE v2 source code
- TRIBE v2 weights/cache
- Python environment
- frontend dependencies
- local database setup
- any helper scripts

The agent must therefore:
1. create the environment
2. download/clone all required repositories
3. install dependencies
4. fetch model assets where needed
5. validate that TRIBE v2 inference works
6. only then begin product implementation

## Important external constraints
- TRIBE v2 predicts **average-subject fMRI responses** across video, audio, and text, not exact emotions for a specific person.
- TRIBE v2's public code/weights are under **CC BY-NC 4.0**, so personal/research use is fine, but later commercial deployment would require a different licensing path or replacement stack.
- TRIBE v2 requires **Python 3.11+** according to the current repository README.
- The TRIBE v2 model card/repo workflow may involve gated or heavyweight dependencies in some paths, so the agent must design graceful fallbacks if a particular encoder path is not immediately available.

## Best immediate direction
Build around **text + lyrics + optional audio** first.
Avoid video until the scoring logic, evaluation loop, and revision engine actually work.

## Non-negotiable bootstrap rule
Do not write code under the false assumption that TRIBE v2 already exists locally.
The repo bootstrap and validation step is part of the implementation, not a side note.
