from __future__ import annotations

from dataclasses import dataclass

from ai_runtime_abi.contract import TaskContract


@dataclass(frozen=True)
class Capability:
    name: str
    provider_model: str
    eval_score: float
    p95_latency_ms: int
    cost_per_1k_tokens_usd: float
    compliance_tags: tuple[str, ...] = ()


class CapabilityRegistry:
    def __init__(self, capabilities: list[Capability]) -> None:
        self.capabilities = capabilities

    def select(self, contract: TaskContract) -> Capability:
        candidates = [
            capability
            for capability in self.capabilities
            if capability.name in contract.allowed_models
            and capability.p95_latency_ms <= int(contract.raw["max_latency_ms"])
        ]
        if not candidates:
            raise RoutingError(f"no capability satisfies {contract.task}@{contract.version}")
        return sorted(candidates, key=lambda item: (-item.eval_score, item.cost_per_1k_tokens_usd))[0]


class RoutingError(RuntimeError):
    pass


def default_registry() -> CapabilityRegistry:
    return CapabilityRegistry(
        [
            Capability("reasoning_medium", "openai:gpt-4.1", 0.91, 6200, 0.012, ("standard",)),
            Capability("local_private_fallback", "ollama:llama3.1", 0.74, 4500, 0.0, ("private",)),
            Capability("strict_json_extractor", "openai:gpt-4.1-mini", 0.88, 2400, 0.003, ("standard",)),
            Capability("high_risk_reasoner", "openai:gpt-4.1", 0.93, 6500, 0.012, ("standard",)),
        ]
    )

