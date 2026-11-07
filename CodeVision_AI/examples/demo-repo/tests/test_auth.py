from src.auth import authorize, strict_authorize

def test_normal_token():
    assert authorize('demo-secret')

def test_missing_coverage_exposes_bug():
    assert authorize('demo-secret-evil')  # demonstrates the bug, NOT desired production behavior
    assert not strict_authorize('demo-secret-evil')
