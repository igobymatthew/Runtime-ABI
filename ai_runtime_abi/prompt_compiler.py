from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ai_runtime_abi.contract import TaskContract


@dataclass(frozen=True)
class PromptArtifact:
    text: str
    hash: str
    template_version: str
    contract_task: str
    contract_version: str


def compile_prompt(contract: TaskContract) -> PromptArtifact:
    text = "\n".join(
        [
            f"Task: {contract.task}",
            f"Contract version: {contract.version}",
            "Return only JSON matching the output schema.",
            "Use only allowed tools and cite evidence objects when required.",
            f"Side effects: {contract.raw['side_effects']}",
        ]
    )
    digest = sha256(text.encode("utf-8")).hexdigest()
    return PromptArtifact(text, digest, "structured-default-v0", contract.task, contract.version)

