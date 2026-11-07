"""Intentionally flawed token check. Not production code."""
import hmac
from src.config import EXPECTED_TOKEN

def authorize(token: str) -> bool:
    # Deliberate bug: e.g., demo-secret-evil passes.
    return token.startswith(EXPECTED_TOKEN)

def strict_authorize(token: str) -> bool:
    return hmac.compare_digest(token, EXPECTED_TOKEN)
