# PID-1.2 Provider Gateway

## Objective
Create a provider abstraction that supports `anthropic`, `openai`, `openrouter`, and `local` without coupling the product logic to one vendor.

## Scope
- provider registry and descriptors
- environment-driven provider settings
- generic execution service
- provider-specific client creation
- transport-specific request mapping
- consistent execution responses and error objects

## Non-goals
- prompt optimization
- tool calling orchestration
- fallback routing policies

## Modules
- `packages/core`
- `packages/llm`
- `apps/api`

## Contracts
- input: provider, model, messages, optional limits/metadata
- output: provider, model, output text, raw identifiers, finish status
- errors: missing credentials, unsupported provider, transport failure, upstream error

## Validation
- registry exposes all four providers
- local provider works without remote credentials
- remote providers fail truthfully when credentials are missing
- API can dispatch via generic and provider-specific routes

## Exit Criteria
- real SDK-backed execution paths exist for all four providers
- errors are machine-readable and stable

## Current Status
Implemented for the first backend slice. Registry, settings, dispatch service, and API integration exist. Remaining work is live credentialed verification and later routing/fallback policy.
