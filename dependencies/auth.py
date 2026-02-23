from copy import copy

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from core.config import ALGORITHM, SECRET
from services.user_service import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Valida el JWT Bearer y devuelve el usuario (sin password/hashed_password)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(username)
    if user is None:
        raise credentials_exception
    # No exponer credenciales y asegurar respuesta JSON-serializable (p. ej. /users/me)
    out = copy(user)
    out.pop("password", None)
    out.pop("hashed_password", None)
    if "_id" in out:
        out["id"] = str(out["_id"])
        del out["_id"]
    return out


def require_admin(user: dict = Depends(get_current_user)):
    """Exige que el usuario tenga role == 'admin'."""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado",
        )
    return user