# PID-1.5 TRIBE Bootstrap Adapter

## Objective
Integrate `tribev2` as an isolated dependency that can be enabled, degraded, or replaced without breaking the product core.

## Scope
- clone into `third_party/tribev2`
- editable install
- pinned revision capture
- pretrained checkpoint load
- optional full inference smoke
- adapter boundary for later feature extraction

## Non-goals
- broad TRIBE feature exploitation
- direct imports across the app

## Design Rules
- all TRIBE dependency handling stays isolated
- bootstrap success does not imply product-wide dependency on TRIBE
- degraded mode remains usable

## Validation
- repo present
- install succeeds
- checkpoint load succeeds
- full smoke can be opt-in because text inference is heavy

## Exit Criteria
- bootstrap can prove whether TRIBE is enabled or degraded
- future response engine can consume TRIBE through one boundary

## Current Status
Clone, install, and pretrained load are working. Full `predict()` smoke is available as opt-in rather than the default path.

