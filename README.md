# Runtime ABI

Runtime ABI is an experimental contract layer for AI calls.

The premise is simple: application code should not call models directly. It
should call versioned task contracts that declare schemas, tool permissions,
capabilities, policy limits, evaluation gates, tracing rules, and fallback
behavior.

This repository starts as a small Python "AI Contract Runtime" that can sit
above model gateways such as LiteLLM or Portkey and below application code.

## Core Idea

```text
Application Code
  ↓
Task Contract API
  ↓
AI Runtime ABI
  ↓
Policy Engine + Eval Gate + Trace Layer
  ↓
Capability Router
  ↓
Model Gateway
  ↓
Frontier Models / Local Models
```

Side channel:

```text
Context Registry ↔ Tool Registry ↔ Trace Store ↔ Regression Suite
```

## Minimum Useful Version

```text
contracts/
  summarize_ticket.json
runtime/
  router.py
  policy.py
  eval_gate.py
  trace.py
  schema_validator.py
tools/
  tool_manifest.yaml
evals/
  golden_cases.jsonl
  adversarial_cases.jsonl
  regression_runner.py
```

## Quick Start

```bash
python -m ai_runtime_abi.cli validate contracts/summarize_ticket.json
python -m ai_runtime_abi.cli inspect contracts/summarize_ticket.json
python -m ai_runtime_abi.cli run-demo contracts/summarize_ticket.json evals/golden_cases.jsonl
```

## Status

Prototype scaffold. The first milestone is enforcing one boring rule:

> Every AI call must pass through a typed task contract.
