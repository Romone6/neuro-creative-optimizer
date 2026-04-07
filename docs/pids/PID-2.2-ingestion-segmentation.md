# PID-2.2 Ingestion and Segmentation

## Objective
Turn raw text into normalized, inspectable analysis units.

## Scope
- text submission contract
- normalization
- paragraph segmentation
- sentence segmentation
- rhetorical block extraction
- segment artifact persistence

## Non-goals
- audio/video ingestion
- semantic scoring

## Exit Criteria
- the system can accept text and return a stable segmented representation for downstream scoring

## Current Status
Implemented for text input. The backend can normalize text, create a content asset, and emit paragraph and sentence segments with stable IDs and lineage.
