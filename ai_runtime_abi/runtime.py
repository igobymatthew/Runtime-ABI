from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from ai_runtime_abi.contract import TaskContract
from ai_runtime_abi.eval_gate import EvalGate
from ai_runtime_abi.policy import PolicyEngine
from ai_runtime_abi.prompt_compiler import compile_prompt
from ai_runtime_abi.router import CapabilityRegistry, default_registry
from ai_runtime_abi.schema_validator import validate_input, validate_output
from ai_runtime_abi.trace import RuntimeTrace


class ModelGateway(Protocol):
    def complete(self, prompt: str, payload: dict[str, Any], provider_model: str) -> dict[str, Any]:
        pass


@dataclass(frozen=True)
class RuntimeResult:
    output: dict[str, Any]
    trace: dict[str, Any]
    passed_eval_gate: bool


class ContractRuntime:
    def __init__(
        self,
        model_gateway: ModelGateway,
        registry: CapabilityRegistry | None = None,
        policy: PolicyEngine | None = None,
        eval_gate: EvalGate | None = None,
    ) -> None:
        self.model_gateway = model_gateway
        self.registry = registry or default_registry()
        self.policy = policy or PolicyEngine()
        self.eval_gate = eval_gate or EvalGate()

    def run(self, contract: TaskContract, payload: dict[str, Any]) -> RuntimeResult:
        validate_input(contract, payload)
        capability = self.registry.select(contract)
        prompt = compile_prompt(contract)
        trace = RuntimeTrace(contract.task, contract.version, prompt_hash=prompt.hash)
        trace.model = capability.provider_model

        policy_decision = self.policy.decide(contract)
        trace.record_policy(policy_decision)
        if not policy_decision.allowed:
            raise PolicyRuntimeError(policy_decision.reason, trace.to_dict())

        output = self.model_gateway.complete(prompt.text, payload, capability.provider_model)
        validate_output(contract, output)
        eval_results = self.eval_gate.evaluate(contract, output)
        trace.record_evals(eval_results)
        trace.final_output = output

        return RuntimeResult(output, trace.to_dict(), self.eval_gate.passed(eval_results))


class PolicyRuntimeError(RuntimeError):
    def __init__(self, message: str, trace: dict[str, Any]) -> None:
        super().__init__(message)
        self.trace = trace


class EchoComplaintGateway:
    def complete(self, prompt: str, payload: dict[str, Any], provider_model: str) -> dict[str, Any]:
        message = payload.get("customer_message", payload.get("resume_text", ""))
        category = "other"
        urgency = "medium"
        lowered = message.lower()
        if "refund" in lowered or "charged" in lowered:
            category = "refund"
        elif "down" in lowered or "outage" in lowered:
            category = "outage"
            urgency = "high"
        if "today" in lowered or "enterprise" in str(payload).lower():
            urgency = "high"
        return {
            "summary": str(message)[:160],
            "category": category,
            "urgency": urgency,
            "evidence": [{"source_id": payload.get("ticket_id", "input"), "quote": str(message)[:120]}],
        }

