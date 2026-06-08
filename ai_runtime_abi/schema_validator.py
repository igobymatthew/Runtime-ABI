from __future__ import annotations

from typing import Any

from ai_runtime_abi.contract import TaskContract


class SchemaValidationError(ValueError):
    pass


def validate_input(contract: TaskContract, payload: dict[str, Any]) -> None:
    _validate(contract.raw["input_schema"], payload, "input")


def validate_output(contract: TaskContract, payload: dict[str, Any]) -> None:
    _validate(contract.raw["output_schema"], payload, "output")


def _validate(schema: dict[str, Any], payload: dict[str, Any], label: str) -> None:
    error = _first_error(schema, payload, "<root>")
    if error:
        raise SchemaValidationError(f"{label} schema failed at {error}")


def _first_error(schema: dict[str, Any], value: Any, path: str) -> str | None:
    schema_type = schema.get("type")
    if schema_type == "object":
        if not isinstance(value, dict):
            return f"{path}: expected object"
        for required_key in schema.get("required", []):
            if required_key not in value:
                return f"{path}.{required_key}: required field missing"
        for key, child_schema in schema.get("properties", {}).items():
            if key in value:
                child_error = _first_error(child_schema, value[key], f"{path}.{key}")
                if child_error:
                    return child_error
    elif schema_type == "array":
        if not isinstance(value, list):
            return f"{path}: expected array"
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < int(min_items):
            return f"{path}: expected at least {min_items} items"
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                child_error = _first_error(item_schema, item, f"{path}[{index}]")
                if child_error:
                    return child_error
    elif schema_type == "string" and not isinstance(value, str):
        return f"{path}: expected string"
    elif schema_type == "number" and not isinstance(value, int | float):
        return f"{path}: expected number"
    elif schema_type == "integer" and not isinstance(value, int):
        return f"{path}: expected integer"
    elif schema_type == "boolean" and not isinstance(value, bool):
        return f"{path}: expected boolean"
    if "enum" in schema and value not in schema["enum"]:
        return f"{path}: expected one of {schema['enum']}"
    return None
