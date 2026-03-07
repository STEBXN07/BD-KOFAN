from fastapi import APIRouter, Depends, HTTPException, status
from dependencies.auth import get_current_user, require_admin
from models.user_model import UserBase, UserCreate
from services.user_service import (
    get_users as get_users_service,
    get_user_by_id,
    create_user as post_create_service,
    update_user as update_user_service,
    delete_user,
    get_user_by_email,
    get_user_by_document
)
from core.security import hash_password

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)]
)


# Usuario actual
@router.get("/me")
def read_me(user: dict = Depends(get_current_user)):
    return user


# Solo admin
@router.get("/admin")
def admin_only(user=Depends(require_admin)):
    return {"message": "Bienvenido, admin!"}


# Obtener todos los usuarios
@router.get("/")
def get_users(page: int = 1, limit: int = 10, user=Depends(require_admin)):
    return get_users_service(page, limit)


# Obtener usuario por ID
@router.get("/{user_id}")
def get_user(user_id: str, user=Depends(require_admin)):
    db_user = get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Usuario no encontrado")
    return db_user


# Crear usuario (solo admin)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(new_user: UserCreate, user=Depends(require_admin)):

    # Validar email y documento
    if get_user_by_email(new_user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El correo ya se encuentra registrado")
    if get_user_by_document(new_user.document_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El número de documento ya se encuentra registrado")

    # Convertir a dict y hashear contraseña
    user_dict = new_user.model_dump()  # model_dump() de Pydantic
    user_dict["password"] = hash_password(user_dict["password"])

    # Eliminar id si se envía
    user_dict.pop("id", None)

    resp = post_create_service(user_dict)
    if not resp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error al crear el usuario")
    return resp


# Actualizar usuario (solo admin)
@router.put("/{user_id}")
def update_user(user_id: str, data_user: UserBase, user=Depends(require_admin)):

    user_dict = data_user.dict()
    user_dict["id"] = user_id

    # Si la contraseña viene en la actualización, la hasheamos
    if "password" in user_dict:
        user_dict["password"] = hash_password(user_dict["password"])

    resp = update_user_service(user_dict)
    if not resp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Id de usuario invalido")
    return resp


# Eliminar usuario (solo admin)
@router.delete("/{user_id}")
def delete_existing_user(user_id: str, user=Depends(require_admin)):

    db_user = get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Usuario no encontrado")

    if delete_user(user_id):
        return {"message": "Usuario eliminado correctamente"}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Error al eliminar el usuario")
    