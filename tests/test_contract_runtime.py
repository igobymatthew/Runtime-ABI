import unittest

from ai_runtime_abi.cli import run_demo
from ai_runtime_abi.contract import TaskContract
from ai_runtime_abi.eval_gate import EvalGate
from ai_runtime_abi.router import default_registry
from ai_runtime_abi.schema_validator import SchemaValidationError, validate_input, validate_output


class ContractRuntimeTest(unittest.TestCase):
    def test_summarize_ticket_contract_loads(self) -> None:
        contract = TaskContract.from_file("contracts/summarize_ticket.json")
        self.assertEqual(contract.task, "summarize_customer_complaint")
        self.assertEqual(default_registry().select(contract).name, "reasoning_medium")

    def test_schema_and_eval_gate_accept_valid_output(self) -> None:
        contract = TaskContract.from_file("contracts/summarize_ticket.json")
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

    def test_run_demo_passes_golden_refund_case(self) -> None:
        result = run_demo("contracts/summarize_ticket.json", "evals/golden_cases.jsonl")
        refund_result = next(item for item in result["results"] if item["case_id"] == "ticket_refund_001")
        self.assertTrue(refund_result["passed"])
        self.assertEqual(refund_result["failures"], [])

    def test_run_demo_fails_expected_category_mismatch(self) -> None:
        result = run_demo("contracts/summarize_ticket.json", "tests/fixtures/category_mismatch.jsonl")
        self.assertFalse(result["ok"])
        self.assertFalse(result["results"][0]["passed"])
        self.assertIn("expected category='billing', got 'refund'", result["results"][0]["failures"])

    def test_adversarial_case_forbids_strings(self) -> None:
        result = run_demo("contracts/summarize_ticket.json", "evals/adversarial_cases.jsonl")
        self.assertTrue(result["ok"])
        self.assertTrue(result["results"][0]["passed"])

    def test_invalid_input_schema_raises(self) -> None:
        contract = TaskContract.from_file("contracts/summarize_ticket.json")
        with self.assertRaises(SchemaValidationError):
            validate_input(contract, {"ticket_id": "T-1"})


if __name__ == "__main__":
    unittest.main()
