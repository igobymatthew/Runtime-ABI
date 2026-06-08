from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_runtime_abi.contract import TaskContract


READ_ONLY_SIDE_EFFECTS = {"read_only"}
HUMAN_APPROVAL_SIDE_EFFECTS = {"write", "execute", "external"}


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    requires_human_approval: bool = False


class PolicyEngine:
    def decide(self, contract: TaskContract, tool_manifest: dict[str, Any] | None = None) -> PolicyDecision:
        side_effects = str(contract.raw["side_effects"])
        if side_effects in READ_ONLY_SIDE_EFFECTS:
            return PolicyDecision(True, "contract is read-only")
        if side_effects in HUMAN_APPROVAL_SIDE_EFFECTS:
            return PolicyDecision(False, f"{side_effects} requires human approval", True)
        return PolicyDecision(False, f"unknown side-effect level: {side_effects}")

