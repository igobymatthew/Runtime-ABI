from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_CONTRACT_FIELDS = {
    "task",
    "version",
    "input_schema",
    "output_schema",
    "allowed_models",
    "allowed_tools",
    "side_effects",
    "evidence_required",
    "max_cost_usd",
    "max_latency_ms",
    "eval_suite",
    "fallback_policy",
    "trace_policy",
}


@dataclass(frozen=True)
class TaskContract:
    raw: dict[str, Any]
    path: Path | None = None

    @property
    def task(self) -> str:
        return str(self.raw["task"])

    @property
    def version(self) -> str:
        return str(self.raw["version"])

    @property
    def allowed_models(self) -> list[str]:
        return list(self.raw["allowed_models"])

    @property
    def allowed_tools(self) -> list[str]:
        return list(self.raw["allowed_tools"])

    @classmethod
    def from_file(cls, path: str | Path) -> "TaskContract":
        contract_path = Path(path)
        with contract_path.open("r", encoding="utf-8") as file:
            raw = json.load(file)
        if not isinstance(raw, dict):
            raise ContractError(f"{contract_path} must contain a YAML mapping")
        contract = cls(raw=raw, path=contract_path)
        contract.validate_shape()
        return contract

    def validate_shape(self) -> None:
        missing = sorted(REQUIRED_CONTRACT_FIELDS - self.raw.keys())
        if missing:
            raise ContractError(f"contract missing required fields: {', '.join(missing)}")
        if not self.allowed_models:
            raise ContractError("contract must allow at least one capability class")
        if self.raw["side_effects"] not in {"read_only", "write", "execute", "external"}:
            raise ContractError("side_effects must be read_only, write, execute, or external")


class ContractError(ValueError):
    pass
