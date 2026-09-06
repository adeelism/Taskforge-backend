from app.security import hash_password, verify_password


def test_hash_is_not_plaintext_and_verifies():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong-password", hashed)
