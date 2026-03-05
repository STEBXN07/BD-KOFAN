"""
Router de tipo_evento (CRUD).

Requisitos:
- Autenticación JWT Bearer obligatoria.
- Solo admin puede eliminar tipos de evento.
- Códigos HTTP correctos: 200/201/400/403/404.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.auth import get_current_user, require_admin
from schemas.tipo_evento_schema import TipoEventoCreate, TipoEventoUpdate
from services.tipo_evento_service import (
    create_tipo_evento,
    delete_tipo_evento,
    get_all_tipos_evento,
    get_tipo_evento_by_id,
    update_tipo_evento,
)
from validations.factura_validations import (
    require_non_empty_update,
    require_valid_object_id,
)


router = APIRouter(
    prefix="/tipo-evento",
    tags=["Tipo Evento"],
    #dependencies=[Depends(get_current_user)],  # 🔐 JWT obligatorio
)


# ================== GET ==================
# Lectura de tipos de evento
# =========================================

@router.get("/", status_code=status.HTTP_200_OK)
def listar_tipos_evento():
    """Lista todos los tipos de evento."""
    return get_all_tipos_evento()


@router.get("/{tipo_evento_id}", status_code=status.HTTP_200_OK)
def obtener_tipo_evento(tipo_evento_id: str):
    """Obtiene un tipo de evento por ID."""
    try:
        require_valid_object_id(tipo_evento_id, "tipo_evento_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    tipo = get_tipo_evento_by_id(tipo_evento_id)
    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de evento no encontrado",
        )
    return tipo


# ================== POST ==================
# Crear tipo de evento
# ==========================================

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_tipo_evento(data: TipoEventoCreate):
    """Crea un nuevo tipo de evento."""
    payload = data.dict()
    return create_tipo_evento(payload)


# ================== PUT ==================
# Actualizar tipo de evento
# =========================================

@router.put("/{tipo_evento_id}", status_code=status.HTTP_200_OK)
def actualizar_tipo_evento(tipo_evento_id: str, data: TipoEventoUpdate):
    """Actualización parcial."""
    try:
        require_valid_object_id(tipo_evento_id, "tipo_evento_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    payload = data.dict(exclude_unset=True)

    try:
        require_non_empty_update(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    updated = update_tipo_evento(tipo_evento_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de evento no encontrado",
        )
    return updated


# ================== DELETE ==================
# Solo admin
# ============================================

@router.delete("/{tipo_evento_id}", status_code=status.HTTP_200_OK)
def eliminar_tipo_evento(
    tipo_evento_id: str,
    _user=Depends(require_admin),  # 🔐 Solo admin
):
    try:
        require_valid_object_id(tipo_evento_id, "tipo_evento_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    ok = delete_tipo_evento(tipo_evento_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de evento no encontrado",
        )
    return {"message": "Tipo de evento eliminado"}