# PID-3.7 Optimization Run Traceability

## Objective
Track optimization runs as first-class artifacts with route, source, and recommendation metadata.

## Scope
- optimization run object
- source analysis linkage
- provider/model route capture
- recommended variant capture

## Exit Criteria
- every optimize request yields a traceable optimization run record

## Current Status
Implemented for the current backend slice. Every optimize request now yields an optimization run record with source linkage, route metadata, and recommended variant capture.
