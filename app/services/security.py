from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def get_fernet() -> Fernet:
    return Fernet(settings.fernet_key.encode())


def encrypt_embedding(embedding: list[float]) -> str:
    return get_fernet().encrypt(str(embedding).encode()).decode()


def decrypt_embedding(encrypted: str) -> list[float]:
    raw = get_fernet().decrypt(encrypted.encode()).decode()
    values = raw.strip("[]")
    return [float(x.strip()) for x in values.split(",") if x.strip()]
