"""
Router de facturas (CRUD) y pagos (subdocumentos).

Requisitos:
- Autenticación JWT Bearer obligatoria.
- Solo admin puede eliminar facturas o pagos.
- Códigos HTTP correctos: 200/201/204/400/401/403/404/409.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from dependencies.auth import get_current_user, require_admin
from schemas.factura_schema import (
    FacturaCreate,
    FacturaUpdate,
    PagoCreate,
    PagoEstadoUpdate,
)
from services.factura_service import (
    add_pago_to_factura,
    create_factura,
    delete_factura,
    delete_pago,
    get_all_facturas,
    get_factura_by_id,
    get_factura_by_numero,
    update_factura,
    update_pago_estado,
)
from validations.factura_validations import (
    require_non_empty_update,
    require_valid_object_id,
)


router = APIRouter(
    prefix="/facturas",
    tags=["Facturas"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", status_code=status.HTTP_200_OK)
def listar_facturas():
    return get_all_facturas()


@router.get("/{factura_id}", status_code=status.HTTP_200_OK)
def obtener_factura(factura_id: str):
    try:
        require_valid_object_id(factura_id, "factura_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    factura = get_factura_by_id(factura_id)
    if not factura:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    return factura


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_factura(data: FacturaCreate):
    try:
        require_valid_object_id(data.reserva_id, "reserva_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    existing = get_factura_by_numero(data.numero_factura)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El número de factura ya existe",
        )

    payload = data.dict()
    payload["reserva_id"] = ObjectId(payload["reserva_id"])
    return create_factura(payload)


@router.put("/{factura_id}", status_code=status.HTTP_200_OK)
def actualizar_factura(factura_id: str, data: FacturaUpdate):
    try:
        require_valid_object_id(factura_id, "factura_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    payload = data.dict(exclude_unset=True)
    try:
        require_non_empty_update(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if "reserva_id" in payload:
        try:
            require_valid_object_id(payload["reserva_id"], "reserva_id")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        payload["reserva_id"] = ObjectId(payload["reserva_id"])

    if "numero_factura" in payload:
        existing = get_factura_by_numero(payload["numero_factura"])
        if existing and str(existing["_id"]) != factura_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El número de factura ya existe",
            )

    updated = update_factura(factura_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    return updated


@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_factura(factura_id: str, _user=Depends(require_admin)):
    try:
        require_valid_object_id(factura_id, "factura_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    ok = delete_factura(factura_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    return None


# -----------------------------------------------------------------------------
# Pagos (subdocumentos dentro de facturas)
# -----------------------------------------------------------------------------


@router.post("/{factura_id}/pagos", status_code=status.HTTP_201_CREATED)
def agregar_pago(factura_id: str, data: PagoCreate):
    try:
        require_valid_object_id(factura_id, "factura_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    factura = add_pago_to_factura(factura_id, data.dict())
    if not factura:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    return factura


@router.put("/{factura_id}/pagos/{pago_id}/estado", status_code=status.HTTP_200_OK)
def actualizar_estado_pago_endpoint(factura_id: str, pago_id: str, data: PagoEstadoUpdate):
    try:
        require_valid_object_id(factura_id, "factura_id")
        require_valid_object_id(pago_id, "pago_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    result = update_pago_estado(factura_id, pago_id, data.estado.value)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    if result == {}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
    return result


@router.delete("/{factura_id}/pagos/{pago_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pago(factura_id: str, pago_id: str, _user=Depends(require_admin)):
    try:
        require_valid_object_id(factura_id, "factura_id")
        require_valid_object_id(pago_id, "pago_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    result = delete_pago(factura_id, pago_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    if result == {}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
    return None
