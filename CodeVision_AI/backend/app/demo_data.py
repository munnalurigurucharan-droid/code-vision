"""Synthetic repository for a repeatable, explicitly labeled demonstration."""
from .security import SourceFile

DEMO_FILES = [
    SourceFile('README.md', '# DemoAuth Service\nAn intentionally flawed example authentication API for educational analysis. No user data.'),
    SourceFile('src/__init__.py',''),
    SourceFile('src/config.py', 'import os\nEXPECTED_TOKEN = os.getenv("SERVICE_TOKEN", "demo-secret")\n'),
    SourceFile('src/auth.py', '''"""Token authorization helper. Intentionally flawed for the demo."""
import hmac
from src.config import EXPECTED_TOKEN

def authorize(token: str) -> bool:
    """Check a bearer token; demonstration includes a prefix-validation bug."""
    # BUG: startswith accepts an expected value followed by arbitrary suffix
    return token.startswith(EXPECTED_TOKEN)

def strict_authorize(token: str) -> bool:
    """Corrected option: compare full strings without timing leaks."""
    return hmac.compare_digest(token, EXPECTED_TOKEN)
'''),
    SourceFile('src/api.py','''"""A minimal FastAPI sample service."""
from fastapi import FastAPI, Header, HTTPException
from src.auth import authorize
app = FastAPI(title="DemoAuth")

@app.get("/private")
def private_route(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ")
    if not authorize(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "authorized"}
'''),
    SourceFile('tests/test_auth.py', '''from src.auth import authorize

def test_expected_token_works():
    assert authorize("demo-secret")

def test_wrong_token_rejected():
    assert not authorize("wrong")
# Missing test: token with correct prefix and extra suffix!
'''),
    SourceFile('requirements.txt','fastapi>=0.115\npytest>=8'),
]
DEMO_INCIDENT = {
    'issue':'Authentication accepts the expected token with an arbitrary suffix, e.g. demo-secret-evil.',
    'root_cause':'src/auth.py uses token.startswith(EXPECTED_TOKEN), so prefix matches pass instead of requiring a full equality comparison.',
    'fix':'Replace startswith with hmac.compare_digest(token, EXPECTED_TOKEN) and add tests for suffix, prefix, missing and malformed tokens.',
    'failed_attempts':'Adjusting token expiry and restarting the API did not change the incorrect prefix comparison. Those are not verified fixes.'
}
