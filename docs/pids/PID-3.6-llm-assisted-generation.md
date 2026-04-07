# PID-3.6 LLM-Assisted Generation

## Objective
Use the provider/prompt layer for variant generation when credentials are available, while preserving a deterministic fallback path.

## Scope
- rendered generation prompts
- policy-based route selection
- provider execution for generation
- graceful fallback on missing credentials or upstream failure

## Exit Criteria
- optimization can use the model layer for generation without becoming dependent on it for basic functionality

## Current Status
Implemented with graceful fallback. Variant generation now uses the prompt registry, routing policy, and provider layer when available, while preserving deterministic local fallback behavior when credentials or upstream execution are unavailable.
