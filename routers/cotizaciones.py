"""
Router de cotizaciones (CRUD).

Requisitos:
- Autenticación JWT Bearer obligatoria.
- Solo admin puede eliminar cotizaciones.
- Códigos HTTP correctos: 200/201/400/403/404.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from dependencies.auth import get_current_user, require_admin
from schemas.cotizacion_schema import CotizacionCreate, CotizacionUpdate
from services.cotizacion_service import (
    create_cotizacion,
    delete_cotizacion,
    get_all_cotizaciones,
    get_cotizacion_by_id,
    update_cotizacion,
)
from validations.factura_validations import (
    require_non_empty_update,
    require_valid_object_id,
)


router = APIRouter(
    prefix="/cotizaciones",
    tags=["Cotizaciones"],
    dependencies=[Depends(get_current_user)],  # Token JWT obligatorio en todas las rutas
)


# ================== GET ==================
# Lectura de cotizaciones (requiere token)
# =========================================

@router.get("/", status_code=status.HTTP_200_OK)
def listar_cotizaciones():
    """Lista todas las cotizaciones."""
    return get_all_cotizaciones()


@router.get("/{cotizacion_id}", status_code=status.HTTP_200_OK)
def obtener_cotizacion(cotizacion_id: str):
    """Obtiene una cotización por ID. 404 si no existe."""
    try:
        require_valid_object_id(cotizacion_id, "cotizacion_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    cotizacion = get_cotizacion_by_id(cotizacion_id)
    if not cotizacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cotización no encontrada")
    return cotizacion


# ================== POST ==================
# Crear cotización
# ==========================================

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_cotizacion(data: CotizacionCreate):
    """Crea cotización. Valida que cliente_id y usuario_cotizador_id sean ObjectId válidos."""
    try:
        require_valid_object_id(data.cliente_id, "cliente_id")
        require_valid_object_id(data.usuario_cotizador_id, "usuario_cotizador_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    payload = data.dict()
    payload["cliente_id"] = ObjectId(payload["cliente_id"])
    payload["usuario_cotizador_id"] = ObjectId(payload["usuario_cotizador_id"])
    return create_cotizacion(payload)


# ================== PUT ==================
# Actualizar cotización
# =========================================

@router.put("/{cotizacion_id}", status_code=status.HTTP_200_OK)
def actualizar_cotizacion(cotizacion_id: str, data: CotizacionUpdate):
    """Actualización parcial. 400 body vacío, 404 si no existe."""
    try:
        require_valid_object_id(cotizacion_id, "cotizacion_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    payload = data.dict(exclude_unset=True)
    try:
        require_non_empty_update(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if "cliente_id" in payload:
        try:
            require_valid_object_id(payload["cliente_id"], "cliente_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        payload["cliente_id"] = ObjectId(payload["cliente_id"])

    if "usuario_cotizador_id" in payload:
        try:
            require_valid_object_id(payload["usuario_cotizador_id"], "usuario_cotizador_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        payload["usuario_cotizador_id"] = ObjectId(payload["usuario_cotizador_id"])

    updated = update_cotizacion(cotizacion_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cotización no encontrada")
    return updated


# ================== DELETE ==================
# Eliminar cotización (solo admin)
# ============================================

@router.delete("/{cotizacion_id}", status_code=status.HTTP_200_OK)
def eliminar_cotizacion(cotizacion_id: str, _user=Depends(require_admin)):  # Solo admin
    try:
        require_valid_object_id(cotizacion_id, "cotizacion_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    ok = delete_cotizacion(cotizacion_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cotización no encontrada")
    return {"message": "Cotización eliminada"}
