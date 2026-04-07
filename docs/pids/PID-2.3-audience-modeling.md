# PID-2.3 Audience Modeling

## Objective
Represent audience assumptions explicitly so scoring and revision are conditioned instead of pretending universality.

## Scope
- JSON persona contract
- target response goals
- audience modifiers
- baseline validation rules
- reusable audience presets later

## Initial Fields
- age band
- cultural context
- familiarity with topic
- literacy assumptions
- platform context
- tone preference
- genre preference
- optional brand/political affinity constraints

## Exit Criteria
- analysis requests require an audience profile
- scoring pipeline can consume audience modifiers deterministically

## Current Status
Implemented for baseline runtime use. Audience profiles can be normalized, validated, and converted into deterministic modifier context for downstream scoring and prompting.
