from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.security import hash_password, verify_password, create_access_token, create_refresh_token
from services.user_service import get_user_by_email, get_user_db, create_user
from models.user_model import UserCreate, UserInDB

router = APIRouter(prefix="/auth", tags=["auth"])

# REGISTER
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    # Verifica si ya existe
    existing = get_user_by_email(user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )

    # Convertir a diccionario y hashear contraseña
    new_user = user.model_dump()  # model_dump() de Pydantic
    new_user["password"] = hash_password(new_user["password"])

    created_user = create_user(new_user)

    return created_user

# LOGIN
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    # 1. Usa get_user_db porque este mapea manualmente el password del dict de Mongo
    user = get_user_db(form.username) 
    
    if not user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrecta")

    # 2. Ahora sí, user.password tendrá el hash $2b$12...
    if not verify_password(form.password, user.password):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrecta")

    # Generar tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }