# Frontend Development Plan

## Status
Validated design direction. Ready for implementation.

## Objective
Build a frontend that acts as a clinical neuro-response workstation for the completed backend, with the brain visualization as the hero object and the chat composer as the operator entry point.

The frontend must stay minimal outside of:
- the MRI-style TRIBE brain visualization
- the signal and insight overlays
- the right-side inspection rail
- the bottom operator chat composer

This is not a generic SaaS dashboard. It is a sparse analysis stage.

## Locked Product Direction

### Core UX Thesis
The interface should open as an operator-led session rather than a pre-filled dashboard.

Default flow:
1. user opens the workspace
2. the bottom composer is the primary call to action
3. the user pastes text or attaches audio/video
4. analysis runs
5. the center brain stage activates
6. the right rail fills with signal readouts and inspection details

The brain becomes the focal point after the first run. Chat remains as the control surface, not the main content.

### Visual Direction
- tone: clinical
- mood: restrained neuroimaging lab
- background: soft gradient charcoal with faint lab-light bloom
- hero object: MRI-style semi-transparent brain
- overall density: maximum minimalism outside of the brain and the signals

The brain should feel diagnostic, not decorative. It should use cold white, muted cyan, and highly restrained localized activation accents. No glossy consumer-health styling. No neon dashboard treatment.

## Layout

### Shell
The app should use a single full-screen workspace with three persistent regions:
- top control strip
- central analysis stage
- bottom operator composer

The signal inspector rail is part of the analysis stage, not a separate app area.

### Region Breakdown

#### Top Control Strip
Minimal, thin, and technical.

Contains:
- project switcher
- modality selector (`text`, `audio`, `video`)
- audience preset selector
- run status
- primary `Analyze` action

It should not contain heavy navigation or dashboard chrome.

#### Central Analysis Stage
This is the dominant region.

Contains:
- large MRI-style brain visualization in the center
- signal overlay layer around the brain
- right-side signal inspector rail

The brain must occupy the emotional and visual center of the page.

#### Bottom Operator Composer
This is the entry point and ongoing control surface.

Contains:
- compact chat thread
- main input
- attach / paste controls for text, audio, and video
- run context chips
- mode switches such as `analyze`, `compare`, and `revise`

The composer should feel like an operator console, not a consumer chat interface.

## Right Rail Behavior

The rail should use a hybrid structure:
- a visible stack of all signals
- a deeper tabbed inspector for the selected signal

### Default Rail Layer
Show all active signals at once as compact rows:
- signal name
- value
- confidence
- delta if in compare mode

These rows should be very restrained. No chunky cards.

### Deep Inspection Layer
Selecting a signal opens tabbed detail for that signal.

Tabs:
- `Signal`
- `Evidence`
- `Revision`

This gives full visibility and deep inspection without sacrificing minimalism.

## Main Screen States

### 1. Standby
Before analysis is run:
- top strip visible
- brain stage in standby / low-power state
- composer active and dominant
- no populated right-rail diagnostics yet

### 2. Active Analysis
After a text, audio, or video run:
- brain becomes fully rendered and signal-active
- signal overlays appear
- right rail populates with all signals
- one signal can be focused for deep inspection

### 3. Compare / Revision
When variants are being compared:
- signal rows show delta values
- brain overlays can switch between runs or show a diff mode
- rail tabs should expose evidence and revision guidance for the selected target

## Brain Visualization Rules

The brain is the primary visual artifact and should be implemented as:
- MRI-style
- semi-transparent
- pale volumetric
- faintly cyan edge-lit
- softly activated by selected signals

The overlay system should use:
- pinned signal labels
- thin connector lines
- subtle contour or region emphasis
- numeric values and confidence metadata

Signals should be rendered as interpreted responses rather than cartoon emotions. Example:
- `TRUST 0.78`
- `TENSION 0.61`
- `NOVELTY 0.54`

If compare mode is active, show deltas quietly beneath or alongside each value.

## Component Map

### Root
- `NeuroWorkspace`

### Shell
- `TopControlBar`
- `AnalysisStage`
- `OperatorComposer`

### Analysis Stage
- `BrainCanvas`
- `SignalOverlayLayer`
- `SignalInspectorRail`

### Signal Rail
- `SignalList`
- `SignalDetailTabs`
- `SignalSummaryTab`
- `SignalEvidenceTab`
- `SignalRevisionTab`

### Composer
- `ChatThread`
- `ComposerInput`
- `AttachmentTray`
- `RunContextChips`

## Backend Contract Mapping

The frontend should bind directly to the completed backend endpoints.

### Core Analysis
- `POST /v1/analyze/text`
- `POST /v1/analyze/text/tribe`
- `POST /v1/analyze/audio`

### Optimization and Revision
- `POST /v1/optimize/text`
- `POST /v1/evaluate/text`

### Workbench
- `POST /v1/workbench/audience-presets`
- `POST /v1/workbench/optimize/text`
- `POST /v1/workbench/evaluate/text`
- `GET /v1/workbench/projects/{project_id}/dashboard`

### Agent Integration
- `POST /v1/agent/batch/score`
- `POST /v1/agent/campaign/optimize`
- `POST /v1/agent/approval`

### Decision Layer
- `GET /v1/decision/commercial-readiness/{project_id}`

## Recommended Frontend Build Order

### Phase A
Create the shell and standby state.

Deliver:
- top control strip
- background system
- central stage frame
- bottom composer shell

### Phase B
Wire text-first operator flow.

Deliver:
- composer submit
- text analysis request handling
- loading states
- activation transition from standby to analysis

### Phase C
Build the brain and signal presentation layer.

Deliver:
- brain visualization component
- signal overlay system
- selected-signal interaction model

### Phase D
Build the right rail.

Deliver:
- full signal stack
- selected signal tabs
- evidence and revision display

### Phase E
Add compare and optimization interactions.

Deliver:
- compare mode
- delta display
- revision loop bindings

### Phase F
Add audio and video operator flows.

Deliver:
- attachment handling
- modality switching
- transcript or media metadata presentation

### Phase G
Add workbench and agent-supporting views as secondary states.

Deliver:
- audience preset usage
- dashboard summary fetch
- campaign loop integration

## Non-Goals For Initial Frontend Build
- multi-page admin navigation
- heavy analytics tables
- dense card dashboards
- ornamental visual effects unrelated to the clinical thesis
- autonomous posting UI

## Success Criteria
- the interface feels like a clinical scan workstation, not a SaaS dashboard
- the brain is clearly the hero object
- the user can start from chat and activate the analysis stage naturally
- all signals remain visible while one signal can be deeply inspected
- the frontend maps cleanly onto the existing backend without inventing a second product model

## Next Step
Begin frontend implementation against this document and use it as the source of truth for layout, interaction hierarchy, and backend wiring.
