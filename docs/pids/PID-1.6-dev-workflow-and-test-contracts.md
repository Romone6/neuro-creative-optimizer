# PID-1.6 Dev Workflow and Test Contracts

## Objective
Establish the minimum engineering discipline required to keep the backend credible as it grows.

## Scope
- `uv`-managed Python environment
- pytest contracts
- lockfile generation
- reproducible scripts
- backend-first package layout

## Validation
- tests cover provider registry, API shape, and setup status
- bootstrap can be rerun without repo corruption

## Exit Criteria
- new backend features ship test-first
- bootstrap and execution contracts regress visibly when broken

## Current Status
Implemented for the current backend foundation. Coverage includes provider registry, provider execution, API dispatch, and setup status contracts.
