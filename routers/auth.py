from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from services.user_service import get_user_by_username

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    """Login con username/password. Devuelve access_token y refresh_token (JWT Bearer)."""
    user = get_user_by_username(form.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario incorrecto",
        )
    # Soporta tanto "password" como "hashed_password" según cómo se haya creado el usuario
    stored = user.get("hashed_password") or user.get("password")
    if not stored or not verify_password(form.password, stored):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña incorrecta",
        )
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }