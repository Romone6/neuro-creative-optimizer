# Complete Project Scope

## 1. Project name
Working name: **Neuro-Informed Creative Optimization Engine**
Possible product names later:
- Response Layer
- Signal Studio
- Audience Resonance Engine
- Creative Response Simulator
- Resonance Lab

## 2. Core user jobs
The system should help a creator:
- upload content
- select an audience target
- choose desired response goals
- receive a scored response breakdown
- see weak spots and strong spots
- generate improved variants
- compare variants side by side
- store results over time

## 3. Content types
### Phase 1
- persuasive writing
- ad copy
- captions
- speeches
- essays
- lyrics

### Phase 2
- audio demos
- song clips
- spoken word audio

### Phase 3
- video ads
- narrated reels
- multimodal campaigns

## 4. Response dimensions
The system should support two layers of dimensions.

### Layer A: direct modeling dimensions
These are dimensions we can operationalize and score more reliably.
- valence
- arousal
- cognitive load
- clarity
- memorability
- novelty
- narrative momentum
- tension
- release
- warmth
- urgency
- trust
- confidence
- ambiguity
- emotional contrast
- sensory vividness

### Layer B: interpreted high-level dimensions
These are more subjective and should be treated as estimated constructs.
- nostalgia
- melancholy
- hopefulness
- awe
- discomfort
- persuasion strength
- relatability
- brand fit
- audience affinity
- social virality likelihood

## 5. Inputs
### Required inputs
- content body
- content type
- target audience profile
- target response goals

### Optional inputs
- creator notes
- reference examples
- brand voice constraints
- platform constraints
- word-count / duration limits
- taboo themes to avoid

## 6. Outputs
### Analysis outputs
- response profile summary
- section-level or timestamp-level score breakdown
- strongest and weakest moments
- response curve
- audience-fit score
- risk flags
- confidence estimates

### Optimization outputs
- edit suggestions
- rewrite instructions
- variant generation
- ranked variants
- delta report versus original
- final recommended version

## 7. Interfaces
### Analyst mode
Deep breakdown and explanation.

### Editor mode
Tight revision suggestions and regenerated alternatives.

### Comparator mode
Compare version A / B / C.

### Campaign mode (later)
Evaluate multiple assets for one campaign and choose the strongest combination.

## 8. Audience modeling
The system must support audience profiles such as:
- age band
- cultural context
- familiarity with topic
- education/literacy assumptions
- platform context
- tone preference
- genre preference
- political/brand affinity if relevant and ethically appropriate

## 9. Non-goals
The project should **not** initially attempt:
- exact individual mind-reading
- mental health diagnosis
- lie detection
- fully autonomous publishing
- universal emotional truth claims
- real-time neurofeedback from actual brain scans
- heavy BCI integration

## 10. MVP definition
A real MVP is:
- text-first
- local or semi-local pipeline
- audience profiles are simple JSON personas
- scores are produced for several reliable dimensions
- LLM gives targeted edits tied to scores
- user can compare original vs revised variants

If those six things do not work, the rest is irrelevant.
