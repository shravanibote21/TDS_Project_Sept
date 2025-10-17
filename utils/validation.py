from typing import Dict, Any
from .config import SECRET


def verify_secret(provided_secret: str) -> bool:
    return provided_secret == SECRET


def validate_request(data: Dict[str, Any]) -> tuple[bool, str]:
    required_fields = [
        "email",
        "secret",
        "round",
        "nonce",
        "brief",
        "evaluation_url",
    ]

    good_to_have_fields = [
        "task",
        "checks",
    ]

    for field in good_to_have_fields:
        if field not in data:
            print(f"Warning: Good-to-have field '{field}' is missing")

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    if not verify_secret(data.get("secret", "")):
        return False, "Invalid secret"

    if not isinstance(data.get("round"), int) or data.get("round", 0) < 1:
        return False, "Invalid round number"

    if "attachments" in data and not isinstance(data["attachments"], list):
        return False, "Attachments must be a list"

    return True, "Valid"