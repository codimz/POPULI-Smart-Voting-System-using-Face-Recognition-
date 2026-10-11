from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from pydantic import SecretStr

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__time_cost=settings.ARGON2_TIME_COST,
    argon2__memory_cost=settings.ARGON2_MEMORY_COST,
    argon2__parallelism=settings.ARGON2_PARALLELISM,
    argon2__hash_len=32,
    argon2__salt_size=16,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def create_voting_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        seconds=settings.VOTING_TOKEN_EXPIRE_SECONDS
    )
    to_encode.update({"exp": expire, "type": "voting"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_voting_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "voting":
        raise ValueError("Invalid token type")
    return payload