# PID-3.1 Prompt and Policy Layer

## Objective
Create versioned prompt templates and deterministic model-routing policy so analysis and revision logic can target different providers cleanly.

## Scope
- prompt template registry
- prompt versioning
- rendered prompt contract
- routing policy for local, cheap, and heavy paths
- provider/model defaults from environment

## Non-goals
- autonomous fallback chains
- prompt optimization experiments
- tool calling orchestration

## Exit Criteria
- backend can render prompts for core tasks
- backend can choose a provider/model route deterministically for each task class

## Current Status
Implemented for the first backend slice. Versioned prompt templates exist, prompts can be rendered through the API, and deterministic routing policy now selects between analysis, heavy, and local model paths.
