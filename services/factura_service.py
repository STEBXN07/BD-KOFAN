"""
Capa de servicio para la entidad Factura (facturas) y subdocumentos de pagos.

MongoDB (PyMongo síncrono) con estructura alineada a Docs/DB_architecture.json.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId

from db.client import db

collection = db.facturas


def _pago_entity(pago: dict) -> dict[str, Any]:
    return {
        "id": str(pago["_id"]),
        "monto": float(pago["monto"]),
        "fecha_pago": pago["fecha_pago"],
        "metodo_pago": pago["metodo_pago"],
        "estado": pago["estado"],
    }


def _factura_entity(factura: dict) -> dict[str, Any]:
    reserva_id = factura.get("reserva_id")
    if isinstance(reserva_id, ObjectId):
        reserva_id = str(reserva_id)
    return {
        "id": str(factura["_id"]),
        "reserva_id": reserva_id,
        "numero_factura": factura["numero_factura"],
        "fecha_emision": factura.get("fecha_emision"),
        "valor_total": float(factura["valor_total"]),
        "valor_pagado": float(factura.get("valor_pagado", 0)),
        "estado": factura["estado"],
        "pagos": [_pago_entity(p) for p in factura.get("pagos", [])],
        "created_at": factura.get("created_at"),
    }


def _calc_valor_pagado(pagos: list[dict]) -> float:
    total = 0.0
    for p in pagos:
        if p.get("estado") == "PAGADO":
            try:
                total += float(p.get("monto", 0))
            except Exception:
                pass
    return total


def _sync_valores_factura(factura_oid: ObjectId) -> None:
    doc = collection.find_one({"_id": factura_oid})
    if not doc:
        return
    pagos = doc.get("pagos", [])
    valor_pagado = _calc_valor_pagado(pagos)
    updates: dict[str, Any] = {"valor_pagado": valor_pagado}

    valor_total = float(doc.get("valor_total", 0) or 0)
    estado_actual = doc.get("estado")
    if valor_total > 0 and valor_pagado >= valor_total:
        updates["estado"] = "PAGADA"
    elif estado_actual == "PAGADA" and valor_pagado < valor_total:
        updates["estado"] = "PENDIENTE"

    collection.update_one({"_id": factura_oid}, {"$set": updates})


def get_all_facturas() -> list[dict[str, Any]]:
    return [_factura_entity(f) for f in collection.find()]


def get_factura_by_id(factura_id: str) -> Optional[dict[str, Any]]:
    try:
        doc = collection.find_one({"_id": ObjectId(factura_id)})
    except Exception:
        return None
    return _factura_entity(doc) if doc else None


def get_factura_by_numero(numero_factura: str) -> Optional[dict]:
    return collection.find_one({"numero_factura": numero_factura})


def create_factura(data: dict) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    doc = dict(data)
    doc.setdefault("fecha_emision", now)
    doc.setdefault("created_at", now)
    doc.setdefault("pagos", [])
    doc.setdefault("valor_pagado", 0.0)
    result = collection.insert_one(doc)
    return get_factura_by_id(str(result.inserted_id))  # type: ignore[return-value]


def update_factura(factura_id: str, data: dict) -> Optional[dict[str, Any]]:
    try:
        oid = ObjectId(factura_id)
    except Exception:
        return None
    result = collection.update_one({"_id": oid}, {"$set": data})
    if result.matched_count == 0:
        return None
    _sync_valores_factura(oid)
    return get_factura_by_id(factura_id)


def delete_factura(factura_id: str) -> bool:
    try:
        oid = ObjectId(factura_id)
    except Exception:
        return False
    result = collection.delete_one({"_id": oid})
    return result.deleted_count == 1


def add_pago_to_factura(factura_id: str, pago_data: dict) -> Optional[dict[str, Any]]:
    try:
        factura_oid = ObjectId(factura_id)
    except Exception:
        return None

    pago_doc = dict(pago_data)
    pago_doc["_id"] = ObjectId()

    result = collection.update_one({"_id": factura_oid}, {"$push": {"pagos": pago_doc}})
    if result.matched_count == 0:
        return None
    _sync_valores_factura(factura_oid)
    return get_factura_by_id(factura_id)


def update_pago_estado(factura_id: str, pago_id: str, nuevo_estado: str) -> Optional[dict[str, Any]]:
    try:
        factura_oid = ObjectId(factura_id)
        pago_oid = ObjectId(pago_id)
    except Exception:
        return None

    result = collection.update_one(
        {"_id": factura_oid},
        {"$set": {"pagos.$[p].estado": nuevo_estado}},
        array_filters=[{"p._id": pago_oid}],
    )
    if result.matched_count == 0:
        return None
    if result.modified_count == 0:
        doc = collection.find_one({"_id": factura_oid})
        pagos = doc.get("pagos", []) if doc else []
        existe = any(p.get("_id") == pago_oid for p in pagos)
        if not existe:
            return {}
    _sync_valores_factura(factura_oid)
    return get_factura_by_id(factura_id)


def delete_pago(factura_id: str, pago_id: str) -> Optional[dict[str, Any]]:
    try:
        factura_oid = ObjectId(factura_id)
        pago_oid = ObjectId(pago_id)
    except Exception:
        return None

    result = collection.update_one({"_id": factura_oid}, {"$pull": {"pagos": {"_id": pago_oid}}})
    if result.matched_count == 0:
        return None
    if result.modified_count == 0:
        return {}
    _sync_valores_factura(factura_oid)
    return get_factura_by_id(factura_id)
