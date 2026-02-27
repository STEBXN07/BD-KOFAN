"""
Servicio de Cotizaciones.
Colección: cotizaciones en kofan_reservas (DB_architecture.json).
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
from bson import ObjectId
from db.client import db

collection = db.cotizaciones


# --- Helpers ---

def _to_oid(value: str) -> Optional[ObjectId]:
    """Convierte string a ObjectId. None si es inválido."""
    try:
        return ObjectId(value)
    except Exception:
        return None


def _serialize(doc: dict) -> dict[str, Any]:
    """Serializa documento cotización para respuesta API."""
    cid = doc.get("cliente_id")
    uid = doc.get("usuario_cotizador_id")
    return {
        "id": str(doc["_id"]),
        "cliente_id": str(cid) if isinstance(cid, ObjectId) else cid,
        "usuario_cotizador_id": str(uid) if isinstance(uid, ObjectId) else uid,
        "fecha_inicio": doc.get("fecha_inicio"),
        "fecha_finalizacion": doc.get("fecha_finalizacion"),
        "estado": doc["estado"],
        "total": float(doc["total"]),
        "observaciones": doc.get("observaciones"),
        "created_at": doc.get("created_at"),
    }


# --- Consultas ---

def get_all_cotizaciones() -> list[dict[str, Any]]:
    """Lista todas las cotizaciones."""
    return [_serialize(c) for c in collection.find()]


def get_cotizacion_by_id(cotizacion_id: str) -> Optional[dict[str, Any]]:
    """Obtiene cotización por ID. None si no existe."""
    oid = _to_oid(cotizacion_id)
    if not oid:
        return None
    doc = collection.find_one({"_id": oid})
    return _serialize(doc) if doc else None


# --- CRUD ---

def create_cotizacion(data: dict) -> dict[str, Any]:
    """Inserta cotización con created_at en UTC."""
    doc = dict(data)
    doc.setdefault("created_at", datetime.now(timezone.utc))
    result = collection.insert_one(doc)
    return get_cotizacion_by_id(str(result.inserted_id))  # type: ignore[return-value]


def update_cotizacion(cotizacion_id: str, data: dict) -> Optional[dict[str, Any]]:
    """Actualiza campos de la cotización. None si no existe."""
    oid = _to_oid(cotizacion_id)
    if not oid or collection.update_one({"_id": oid}, {"$set": data}).matched_count == 0:
        return None
    return get_cotizacion_by_id(cotizacion_id)


def delete_cotizacion(cotizacion_id: str) -> bool:
    """Elimina cotización. True si se eliminó."""
    oid = _to_oid(cotizacion_id)
    return bool(oid and collection.delete_one({"_id": oid}).deleted_count)
