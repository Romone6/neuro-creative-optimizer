# PID-4.3 Calibration Metrics

## Objective
Measure how well model scores align with human judgments.

## Scope
- dimension-level MAE style error
- aggregate calibration score
- rating-vs-model comparison tables

## Exit Criteria
- evaluation returns explicit calibration metrics rather than vague claims of alignment

## Current Status
Implemented for the current evaluation slice. The backend now computes dimension-level absolute error and aggregate alignment summaries from human ratings versus model scores.
