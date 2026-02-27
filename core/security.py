from passlib.context import CryptContext
from jose import jwt 
from datetime import datetime, timedelta, timezone
from core.config import (
    SECRET,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash de contraseña con bcrypt"""
    if not password or not isinstance(password, str):
        raise ValueError("La contraseña debe ser un texto no vacío")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    if not plain_password or not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Crea token JWT de acceso (30 minutos)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire, 
        "type": "access",
        "iat": datetime.now(timezone.utc)
    })
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Crea token JWT de refresco (7 días)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire, 
        "type": "refresh",
        "iat": datetime.now(timezone.utc)
    })
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)