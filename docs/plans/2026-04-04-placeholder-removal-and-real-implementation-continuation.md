# Placeholder Removal and Real Implementation Continuation

## Why This Document Exists
The frontend and TRIBE integration previously implied capabilities that were not fully real:
- TRIBE analysis could appear active while the runtime was only in degraded mode
- audio and video were exposed in the frontend without true file upload or multimodal processing
- the brain visualization was a stylized placeholder rather than a verified anatomical render
- the frontend imposed a hardcoded audience-targeting flow that did not match the intended operator prompt

This continuation plan records what has now been removed or hardened, and what must be implemented next to make the system real.

## What Has Been Removed or Hardened

### 1. Synthetic TRIBE prior is no longer allowed
The synthetic TRIBE fallback path and the heuristic TRIBE-fusion code have been removed from the live app path and from the TRIBE package implementation.

New behavior:
- if TRIBE is not `tribe_enabled`
- if full fusion is not available
- if the runtime is only `tribe_degraded`

Then the TRIBE analysis route must refuse the request rather than fabricate a pseudo-TRIBE result.

The product must now say, explicitly, that TRIBE v2 is unavailable.

Current live behavior:
- baseline text analysis works
- TRIBE runtime status is exposed separately
- TRIBE live analysis endpoint refuses requests until a real inference path exists

### 2. Unsupported multimodal frontend paths are removed
The frontend no longer pretends to support audio or video upload.

Removed from the active UI:
- audio mode
- video mode
- transcript-proxy language
- inferred audio sections in the browser
- fake video analysis path through text

Until there is a real file-upload and media-processing pipeline, the frontend is text-only.

### 3. Hardcoded audience targeting is removed from the frontend
The frontend no longer exposes fake audience-selection UX.

Current intended operator model:
- user submits content
- user can optionally describe context in the chat
- analysis defaults to general audience interpretation unless later extended with explicit operator-controlled audience mode

### 4. Fake anatomical brain render is removed
The stylized SVG brain is not a verified anatomical or TRIBE-driven render.

It has been removed from the live diagnostic stage.

Current honest behavior:
- the stage shows runtime readiness and signal status only
- no fake anatomical claim is made

## What Is Real Right Now

### Backend
- text analysis pipeline
- revision and optimization loop
- evaluation pipeline
- workbench persistence
- agent workflow endpoints
- commercial-readiness reporting
- TRIBE installation and checkpoint-load validation

### Not Real Yet
- full TRIBE-enabled live fusion in the app
- real multimodal file upload for audio/video
- real media decoding and upload-backed transcript pipeline
- real high-detail anatomical brain rendering tied to verified signals

## Required Next Implementation Steps

### A. Real TRIBE Activation
1. Make the TRIBE path reach `tribe_enabled`
2. Enable a verified full predict path
3. Replace degraded refusal with true TRIBE-backed outputs only after runtime validation
4. Keep the UI explicit about runtime state

### B. Real Multimodal Upload
1. Add frontend file upload for audio and video
2. Add backend upload endpoints and artifact storage
3. Add transcript extraction / ingestion pipeline
4. Add media metadata and real section alignment from uploaded assets

### C. Real Brain Visualization
1. acquire or generate a medically plausible high-detail anatomical brain asset
2. define a real signal-to-region mapping
3. render only verified region activations
4. remove any purely decorative activation graphics

### D. General-Audience Operator Flow
1. default all analysis to general audience
2. allow user-supplied context in chat prompt
3. add advanced audience conditioning later as an explicit optional control, not an assumed default

## Current Rule
If a feature is not live, verified, and wired to a real backend path, it should not appear in the product as if it exists.
