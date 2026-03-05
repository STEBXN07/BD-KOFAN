from fastapi import APIRouter, Depends, HTTPException, status
from dependencies.auth import get_current_user, require_admin
from services.user_service import (
    get_users as get_users_service,
    get_user_by_id,
    create_user as post_create_service,
    update_user as update_user_service,
    delete_user,
    get_user_by_email,
    get_user_by_document
)

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
    return {
        "message": "Bienvenido, admin!"
    }


# Obtener todos los usuarios
@router.get("/")
def get_users(page: int = 1, limit: int = 10, user=Depends(require_admin)):
    return get_users_service(page, limit)


# Obtener usuario por ID
@router.get("/{user_id}")
def get_user(user_id: str, user=Depends(require_admin)):

    db_user = get_user_by_id(user_id)

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return db_user


# Crear usuario
@router.post("/", status_code=201)
def create_user(New_user: dict, user=Depends(require_admin)):

    user_email = get_user_by_email(New_user["email"])

    if user_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El correo ya se encuentra registrado"
        )
    
    user_document = get_user_by_document(New_user["document_number"])

    if user_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El número de documento ya se encuentra registrado"
        )

    user_dic = dict(New_user)
    if user_dic.get("id"):
        del user_dic["id"]

    resp = post_create_service(user_dic)
    if not resp:
        raise HTTPException(
            status_code=400,
            detail="Error al crear el usuario"
        )

    return resp


# Actualizar usuario
@router.put("/")
def update_user(data_user: dict, user=Depends(require_admin)):

    id = data_user.get("id")
    if not id:
        raise HTTPException(
            status_code=400,
            detail="ID de usuario es requerido"
        )   
    
    resp = update_user_service(data_user)
    if not resp:
        raise HTTPException(
            status_code=404,
            detail="Id de usuario invalido"
        )
    return resp


# Eliminar usuario
@router.delete("/{user_id}")
def delete_existing_user(user_id: str, user=Depends(require_admin)):

    db_user = get_user_by_id(user_id)

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    if delete_user(user_id):
        return {
        "message": "Usuario eliminado correctamente"
    }

    return {
        "message": "Error al eliminar el usuario"
    }
