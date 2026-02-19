from fastapi import APIRouter, Depends, HTTPException, Depends 
from fastapi.security import OAuth2PasswordRequestForm
from core.security import create_access_token, create_refresh_token, verify_password
from services.user_service import get_user_by_username

router = APIRouter(
    prefix="/auth", 
    tags=["auth"]
    )

@router.post("/login")
def login (form: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form.username)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario incorrecto")
    
    if not verify_password(form.password, user["password"]):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}