from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password,
)
from services.user_service import get_user_by_email, get_user_db, create_user
from models.user_model import UserPassword 

router = APIRouter(prefix="/auth", tags=["auth"])

# REGISTER
@router.post("/register")
def register(user: UserPassword):

    existing = get_user_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya existe"
        )

    new_user = user.dict()

    # usamos el service
    create_user(new_user)

    return {"message": "Usuario creado correctamente"}



@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):

    user = get_user_db(form.username)  # 👈 usa esta función

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Usuario incorrecto"
        )

    if not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Contraseña incorrecta"
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }