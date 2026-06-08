from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class RuntimeTrace:
    contract_task: str
    contract_version: str
    prompt_hash: str | None = None
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model: str | None = None
    policy_decisions: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    eval_scores: list[dict[str, Any]] = field(default_factory=list)
    final_output: dict[str, Any] | None = None

    def record_policy(self, decision: Any) -> None:
        self.policy_decisions.append(asdict(decision))

    def record_evals(self, results: list[Any]) -> None:
        self.eval_scores.extend(asdict(result) for result in results)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

