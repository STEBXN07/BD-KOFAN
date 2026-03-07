"""
Router de clientes (CRUD).

Todos los endpoints requieren autenticación mediante Bearer token (JWT).
Prefijo: /clientes. Códigos HTTP explícitos en cada ruta.
Los datos cumplen con la colección "clientes" de mongodb_schema.json;
el email se valida como único antes de crear (409 si ya existe).
"""
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.auth import get_current_user
from schemas.cliente_schema import ClienteCreate, ClienteUpdate
from services.cliente_service import (
    create_cliente,
    delete_cliente,
    get_all_clientes,
    get_cliente_by_email,
    get_cliente_by_id,
    update_cliente,
)

# -----------------------------------------------------------------------------
# Router: todas las rutas exigen token válido
# -----------------------------------------------------------------------------

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(get_current_user)],
)

# GET



@router.get("/", status_code=status.HTTP_200_OK)
def listar_clientes():
    """Lista todos los clientes. Requiere autenticación (Bearer token)."""
    return get_all_clientes()


@router.get("/{cliente_id}", status_code=status.HTTP_200_OK)
def obtener_cliente(cliente_id: str):
    """Obtiene un cliente por ID. Requiere autenticación. 404 si no existe."""
    cliente = get_cliente_by_id(cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )
    return cliente


# -----------------------------------------------------------------------------
# POST
# -----------------------------------------------------------------------------


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_cliente(data: ClienteCreate):
    """Crea un nuevo cliente. Requiere autenticación. 409 si el email ya existe."""
    existing = get_cliente_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )
    return create_cliente(data.dict())


# -----------------------------------------------------------------------------
# PUT
# -----------------------------------------------------------------------------


@router.put("/{cliente_id}", status_code=status.HTTP_200_OK)
def actualizar_cliente(cliente_id: str, data: ClienteUpdate):
    """Actualización parcial. Requiere autenticación. 400 si body vacío, 404 si no existe, 409 si el nuevo email ya lo tiene otro cliente."""
    payload = data.dict(exclude_unset=True)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar",
        )
    # Unicidad de email (mongodb_schema.json): si cambian el email, no debe estar usado por otro cliente
    if "email" in payload:
        existing = get_cliente_by_email(payload["email"])
        if existing and existing["id"] != cliente_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado por otro cliente",
            )
    updated = update_cliente(cliente_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )
    return updated


# -----------------------------------------------------------------------------
# DELETE
# -----------------------------------------------------------------------------


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(cliente_id: str):
    """Elimina un cliente por ID. Requiere autenticación. 404 si no existe."""
    deleted = delete_cliente(cliente_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )
    return None
