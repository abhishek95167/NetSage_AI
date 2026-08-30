"""
NetSage AI — Diagnosis JSON Schema
Validates AI diagnosis output against the required schema.
"""

DIAGNOSIS_SCHEMA = {
    "type": "object",
    "required": ["root_cause", "confidence", "osi_layer", "evidence", "next_command", "fix_steps", "alternative_causes"],
    "properties": {
        "root_cause": {"type": "string", "minLength": 1},
        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
        "osi_layer": {"type": "string", "minLength": 1},
        "evidence": {"type": "array", "items": {"type": "string"}},
        "next_command": {"type": "string"},
        "fix_steps": {"type": "array", "items": {"type": "string"}},
        "alternative_causes": {"type": "array", "items": {"type": "string"}}
    }
}


def validate_diagnosis(data: dict) -> tuple[bool, list[str]]:
    """
    Validate a diagnosis dict against the required schema.
    Returns (is_valid, list_of_errors).
    """
    errors = []

    required_fields = ["root_cause", "confidence", "osi_layer", "evidence", "next_command", "fix_steps", "alternative_causes"]

    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if "root_cause" in data:
        if not isinstance(data["root_cause"], str) or len(data["root_cause"]) == 0:
            errors.append("root_cause must be a non-empty string")

    if "confidence" in data:
        if not isinstance(data["confidence"], (int, float)):
            errors.append("confidence must be a number")
        elif data["confidence"] < 0 or data["confidence"] > 100:
            errors.append("confidence must be between 0 and 100")

    if "osi_layer" in data:
        if not isinstance(data["osi_layer"], str) or len(data["osi_layer"]) == 0:
            errors.append("osi_layer must be a non-empty string")

    if "evidence" in data:
        if not isinstance(data["evidence"], list):
            errors.append("evidence must be an array")
        elif not all(isinstance(e, str) for e in data["evidence"]):
            errors.append("All evidence items must be strings")

    if "next_command" in data:
        if not isinstance(data["next_command"], str):
            errors.append("next_command must be a string")

    if "fix_steps" in data:
        if not isinstance(data["fix_steps"], list):
            errors.append("fix_steps must be an array")
        elif not all(isinstance(s, str) for s in data["fix_steps"]):
            errors.append("All fix_steps items must be strings")

    if "alternative_causes" in data:
        if not isinstance(data["alternative_causes"], list):
            errors.append("alternative_causes must be an array")
        elif not all(isinstance(a, str) for a in data["alternative_causes"]):
            errors.append("All alternative_causes items must be strings")

    return len(errors) == 0, errors
