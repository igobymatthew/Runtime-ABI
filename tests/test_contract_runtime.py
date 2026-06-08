import unittest

from ai_runtime_abi.contract import TaskContract
from ai_runtime_abi.eval_gate import EvalGate
from ai_runtime_abi.router import default_registry
from ai_runtime_abi.schema_validator import validate_input, validate_output


class ContractRuntimeTest(unittest.TestCase):
    def test_summarize_ticket_contract_loads(self) -> None:
        contract = TaskContract.from_file("contracts/summarize_ticket.yaml")
        self.assertEqual(contract.task, "summarize_customer_complaint")
        self.assertEqual(default_registry().select(contract).name, "reasoning_medium")

    def test_schema_and_eval_gate_accept_valid_output(self) -> None:
        contract = TaskContract.from_file("contracts/summarize_ticket.yaml")
        validate_input(
            contract,
            {
                "ticket_id": "T-1",
                "customer_message": "I was charged twice and need a refund.",
                "customer_tier": "pro",
                "locale": "en-US",
            },
        )
        output = {
            "summary": "Customer was charged twice and requests a refund.",
            "category": "refund",
            "urgency": "medium",
            "evidence": [{"source_id": "T-1", "quote": "charged twice"}],
        }
        validate_output(contract, output)
        self.assertTrue(EvalGate.passed(EvalGate().evaluate(contract, output)))


if __name__ == "__main__":
    unittest.main()
