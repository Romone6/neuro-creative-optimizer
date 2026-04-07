# PID-4.7 Evaluation API

## Objective
Expose the full evaluation pipeline as a callable backend endpoint.

## Scope
- text evaluation request contract
- evaluation orchestration service
- API endpoint for evaluation

## Exit Criteria
- one request can produce evaluation metrics, experiment artifacts, and a report

## Current Status
Implemented. The backend now exposes the full request-driven evaluation pipeline through `POST /v1/evaluate/text`.
