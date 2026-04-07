# PID-1.3 Control Plane API

## Objective
Expose the backend as a callable service for both internal use and future cross-project tool invocation.

## Scope
- health endpoint
- setup status endpoint
- provider catalogue endpoint
- generic LLM execution endpoint
- provider-specific execution endpoints

## Non-goals
- frontend delivery
- authz/authn
- streaming transport

## API Surface
- `GET /health`
- `GET /v1/setup/status`
- `GET /v1/llm/providers`
- `POST /v1/llm/chat`
- `POST /v1/llm/providers/{provider}/chat`

## Design Constraints
- JSON-first responses
- stable error schema
- future-safe for upstream tool callers

## Validation
- endpoint contracts tested with FastAPI client
- provider dispatch verified independently from HTTP

## Exit Criteria
- endpoints execute against the provider gateway
- setup status reflects real bootstrap state

## Current Status
Implemented for backend control-plane v1. Health, provider catalogue, setup status, generic chat, and provider-specific chat routes are live.
