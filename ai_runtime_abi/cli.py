from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_runtime_abi.contract import TaskContract
from ai_runtime_abi.policy import PolicyEngine
from ai_runtime_abi.prompt_compiler import compile_prompt
from ai_runtime_abi.router import default_registry
from ai_runtime_abi.runtime import ContractRuntime, EchoComplaintGateway
from ai_runtime_abi.schema_validator import validate_input


def main() -> None:
    parser = argparse.ArgumentParser(prog="ai-runtime-abi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("contract")

    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("contract")

    demo_parser = subparsers.add_parser("run-demo")
    demo_parser.add_argument("contract")
    demo_parser.add_argument("cases")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("contract")
    run_parser.add_argument("payload_json")

    args = parser.parse_args()
    if args.command == "validate":
        contract = TaskContract.from_file(args.contract)
        print(json.dumps({"ok": True, "task": contract.task, "version": contract.version}, indent=2))
    elif args.command == "inspect":
        print(json.dumps(inspect_contract(args.contract), indent=2))
    elif args.command == "run-demo":
        print(json.dumps(run_demo(args.contract, args.cases), indent=2))
    elif args.command == "run":
        payload = json.loads(args.payload_json)
        contract = TaskContract.from_file(args.contract)
        runtime = ContractRuntime(EchoComplaintGateway())
        result = runtime.run(contract, payload)
        print(json.dumps(result.__dict__, indent=2))


def inspect_contract(path: str) -> dict[str, Any]:
    contract = TaskContract.from_file(path)
    capability = default_registry().select(contract)
    prompt = compile_prompt(contract)
    decision = PolicyEngine().decide(contract)
    return {
        "task": contract.task,
        "version": contract.version,
        "selected_capability": capability.name,
        "provider_model": capability.provider_model,
        "prompt_hash": prompt.hash,
        "policy": decision.__dict__,
    }


def run_demo(contract_path: str, cases_path: str) -> dict[str, Any]:
    contract = TaskContract.from_file(contract_path)
    runtime = ContractRuntime(EchoComplaintGateway())
    traces = []
    for case in _read_jsonl(Path(cases_path)):
        if case.get("task") != contract.task:
            continue
        validate_input(contract, case["input"])
        result = runtime.run(contract, case["input"])
        traces.append(result.trace)
    return {"ok": True, "traces": traces}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


if __name__ == "__main__":
    main()
