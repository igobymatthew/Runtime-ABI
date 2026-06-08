# AI Runtime ABI Specification

This document defines the first draft of the AI Runtime ABI: a stable contract
surface between application code and volatile model, prompt, tool, retriever,
and gateway implementations.

## Design Rule

Application code never calls a model directly.

Application code calls:

```text
run_task(task_name, version, input)
```

The runtime resolves the contract, validates input, compiles the prompt, checks
policy, routes to a capability, validates output, records a trace, and applies
evaluation gates.

## Task Contract Fields

| Field | Purpose |
| --- | --- |
| `task` | Stable task name used by application code. |
| `version` | Behavioral semantic version. |
| `input_schema` | JSON Schema for caller input. |
| `output_schema` | JSON Schema for model output. |
| `allowed_models` | Capability classes, not provider model names. |
| `allowed_tools` | Tool names from the tool registry. |
| `side_effects` | Runtime authority: `read_only`, `write`, `execute`, or `external`. |
| `evidence_required` | Whether outputs must cite context objects. |
| `max_cost_usd` | Per-call budget ceiling. |
| `max_latency_ms` | Per-call latency ceiling. |
| `eval_suite` | Contract-specific gates and regression suites. |
| `fallback_policy` | Runtime behavior on schema, quality, and tool failures. |
| `trace_policy` | Redaction, hashing, retention, and logging behavior. |

## Behavioral Semver

AI contracts use semantic versioning with behavioral meaning:

- `major`: output meaning, tool authority, side effects, or business semantics changed.
- `minor`: better model, retrieval, or prompt with the same contract.
- `patch`: latency, cost, formatting, retries, or observability improved.
- `shadow`: candidate route tested against traces but not user-facing.

## Capability Registry

Business logic should reference capability classes:

- `fast_classifier`
- `long_context_reader`
- `strict_json_extractor`
- `vision_parser`
- `code_patch_planner`
- `high_risk_reasoner`
- `local_private_fallback`

The registry maps those classes to provider models using eval score, latency,
cost, compliance, availability, and rollout state.

## Tool Manifest Metadata

Tools require blast-radius metadata beyond a function signature:

- read/write scope
- idempotency
- side effects
- required approval level
- auth scope
- rate limit
- rollback function
- secret exposure risk
- whether output may contain untrusted instructions

## Trace Contract

Every run should emit a portable trace with:

- request and contract version
- prompt hash
- selected capability and provider model
- schema versions
- context objects used
- tool calls and tool outputs policy
- retries and fallback decisions
- guardrail and eval scores
- final output
- policy decisions

OpenTelemetry should be the production trace base layer. This scaffold currently
emits JSON-shaped traces so the ABI can evolve before binding to a telemetry SDK.

