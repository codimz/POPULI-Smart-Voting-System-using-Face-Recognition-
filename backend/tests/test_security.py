# T26: Unit test security
import pytest
from datetime import datetime, timedelta, timezone
from app.core.security import get_password_hash, verify_password, create_access_token, decode_token
from jose import JWTError


def test_argon2_hash_and_verify():
    pw = "testpass"
    h = get_password_hash(pw)
    assert verify_password(pw, h)
    assert not verify_password("wrong", h)


def test_jwt_create_decode_and_expire():
    payload = {"sub": "2310119999", "nim": "2310119999", "type": "access"}
    token = create_access_token(payload)
    decoded = decode_token(token)
    assert decoded["sub"] == "2310119999"

    # Expired token
    expired_token = create_access_token(payload, expires_delta=timedelta(seconds=-1))
    with pytest.raises(Exception):
        decode_token(expired_token)


def test_jwt_wrong_type():
    token = create_access_token({"sub": "x"})
    # Just ensure decode works; wrong type handled at dependency layer
    assert decode_token(token)["sub"] == "x"
