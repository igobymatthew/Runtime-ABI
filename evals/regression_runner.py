from __future__ import annotations

from ai_runtime_abi.cli import run_demo


def main() -> None:
    result = run_demo("contracts/summarize_ticket.yaml", "evals/golden_cases.jsonl")
    print(result)


if __name__ == "__main__":
    main()

