from typing import Dict, Any, Tuple
from .config import SECRET


def verify_secret(provided_secret: str) -> bool:
    """Check if provided secret matches configured secret."""
    return provided_secret == SECRET


def validate_request(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate incoming JSON payload for /api-endpoint.

    Returns:
        Tuple of (is_valid, message).
    """
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
            # Keep silent other than validation result to avoid log noise
            pass

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
