from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_runtime_abi.contract import TaskContract


@dataclass(frozen=True)
class EvalResult:
    name: str
    passed: bool
    score: float
    reason: str


class EvalGate:
    def evaluate(self, contract: TaskContract, output: dict[str, Any]) -> list[EvalResult]:
        results: list[EvalResult] = []
        if contract.raw.get("evidence_required"):
            evidence = output.get("evidence")
            passed = isinstance(evidence, list) and len(evidence) > 0
            results.append(EvalResult("evidence_required", passed, 1.0 if passed else 0.0, "evidence array present"))
        text = str(output)
        pii_tokens = ["ssn", "social security", "password", "api key"]
        pii_passed = not any(token in text.lower() for token in pii_tokens)
        results.append(EvalResult("pii_leak_check_v1", pii_passed, 1.0 if pii_passed else 0.0, "basic forbidden-token scan"))
        return results

    @staticmethod
    def passed(results: list[EvalResult]) -> bool:
        return all(result.passed for result in results)

