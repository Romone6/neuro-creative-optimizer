# PID-2.1 Core Schemas

## Objective
Define stable typed contracts for all analysis and revision workflows before scoring logic expands.

## Scope
- content asset
- content segment
- audience profile
- analysis run
- score vector
- confidence summary
- revision plan
- variant asset

## Design Rules
- version every core schema
- JSON-first
- provenance and lineage are required fields, not extras

## Exit Criteria
- ingestion, scoring, and revision layers can share contracts without ad-hoc dicts

## Current Status
Implemented for the initial core data layer. Versioned, lineage-aware contracts now exist for assets, segments, audience profiles, score vectors, analysis runs, revision plans, and variants.
