"""
Servicio de Facturas y Pagos (subdocumentos embebidos).
Colección: facturas en kofan_reservas (DB_architecture.json).
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
from bson import ObjectId
from db.client import db

collection = db.facturas


# --- Helpers ---

def _to_oid(value: str) -> Optional[ObjectId]:
    """Convierte string a ObjectId. None si es inválido."""
    try:
        return ObjectId(value)
    except Exception:
        return None


def _serialize_pago(p: dict) -> dict[str, Any]:
    """Serializa subdocumento pago para respuesta API."""
    return {
        "id": str(p["_id"]), "monto": float(p["monto"]),
        "fecha_pago": p["fecha_pago"], "metodo_pago": p["metodo_pago"],
        "estado": p["estado"],
    }


def _serialize_factura(f: dict) -> dict[str, Any]:
    """Serializa documento factura para respuesta API."""
    rid = f.get("reserva_id")
    return {
        "id": str(f["_id"]),
        "reserva_id": str(rid) if isinstance(rid, ObjectId) else rid,
        "numero_factura": f["numero_factura"],
        "fecha_emision": f.get("fecha_emision"),
        "valor_total": float(f["valor_total"]),
        "valor_pagado": float(f.get("valor_pagado", 0)),
        "estado": f["estado"],
        "pagos": [_serialize_pago(p) for p in f.get("pagos", [])],
        "created_at": f.get("created_at"),
    }


def _sync_valores(factura_oid: ObjectId) -> None:
    """Recalcula valor_pagado y actualiza estado según pagos embebidos."""
    doc = collection.find_one({"_id": factura_oid})
    if not doc:
        return
    pagado = sum(float(p.get("monto", 0)) for p in doc.get("pagos", []) if p.get("estado") == "PAGADO")
    total = float(doc.get("valor_total", 0) or 0)
    updates: dict[str, Any] = {"valor_pagado": pagado}
    if total > 0 and pagado >= total:
        updates["estado"] = "PAGADA"
    elif doc.get("estado") == "PAGADA" and pagado < total:
        updates["estado"] = "PENDIENTE"
    collection.update_one({"_id": factura_oid}, {"$set": updates})


# --- Consultas ---

def get_all_facturas() -> list[dict[str, Any]]:
    """Lista todas las facturas."""
    return [_serialize_factura(f) for f in collection.find()]


def get_factura_by_id(factura_id: str) -> Optional[dict[str, Any]]:
    """Obtiene factura por ID. None si no existe."""
    oid = _to_oid(factura_id)
    if not oid:
        return None
    doc = collection.find_one({"_id": oid})
    return _serialize_factura(doc) if doc else None


def get_factura_by_numero(numero_factura: str) -> Optional[dict]:
    """Busca por numero_factura (único). Para validar duplicados."""
    return collection.find_one({"numero_factura": numero_factura})


# --- CRUD Facturas ---

def create_factura(data: dict) -> dict[str, Any]:
    """Inserta factura con defaults (pagos=[], valor_pagado=0, fechas UTC)."""
    now = datetime.now(timezone.utc)
    doc = {**data, **{"pagos": [], "valor_pagado": 0.0}}
    doc.setdefault("fecha_emision", now)
    doc.setdefault("created_at", now)
    result = collection.insert_one(doc)
    return get_factura_by_id(str(result.inserted_id))  # type: ignore[return-value]


def update_factura(factura_id: str, data: dict) -> Optional[dict[str, Any]]:
    """Actualiza campos y recalcula valor_pagado/estado."""
    oid = _to_oid(factura_id)
    if not oid or collection.update_one({"_id": oid}, {"$set": data}).matched_count == 0:
        return None
    _sync_valores(oid)
    return get_factura_by_id(factura_id)


def delete_factura(factura_id: str) -> bool:
    """Elimina factura. True si se eliminó."""
    oid = _to_oid(factura_id)
    return bool(oid and collection.delete_one({"_id": oid}).deleted_count)


# --- Pagos (embebidos en facturas con $push / $pull) ---

def add_pago_to_factura(factura_id: str, pago_data: dict) -> Optional[dict[str, Any]]:
    """Inserta pago en array embebido con $push."""
    oid = _to_oid(factura_id)
    if not oid:
        return None
    pago = {**pago_data, "_id": ObjectId()}
    if collection.update_one({"_id": oid}, {"$push": {"pagos": pago}}).matched_count == 0:
        return None
    _sync_valores(oid)
    return get_factura_by_id(factura_id)


def update_pago_estado(factura_id: str, pago_id: str, nuevo_estado: str) -> Optional[dict[str, Any]]:
    """Actualiza estado de un pago con array_filters. {} si pago no existe."""
    foid, poid = _to_oid(factura_id), _to_oid(pago_id)
    if not foid or not poid:
        return None
    result = collection.update_one(
        {"_id": foid}, {"$set": {"pagos.$[p].estado": nuevo_estado}},
        array_filters=[{"p._id": poid}],
    )
    if result.matched_count == 0:
        return None
    if result.modified_count == 0:
        doc = collection.find_one({"_id": foid})
        if not any(p.get("_id") == poid for p in (doc or {}).get("pagos", [])):
            return {}
    _sync_valores(foid)
    return get_factura_by_id(factura_id)


def delete_pago(factura_id: str, pago_id: str) -> Optional[dict[str, Any]]:
    """Elimina pago del array con $pull. {} si pago no existe."""
    foid, poid = _to_oid(factura_id), _to_oid(pago_id)
    if not foid or not poid:
        return None
    result = collection.update_one({"_id": foid}, {"$pull": {"pagos": {"_id": poid}}})
    if result.matched_count == 0:
        return None
    if result.modified_count == 0:
        return {}
    _sync_valores(foid)
    return get_factura_by_id(factura_id)
