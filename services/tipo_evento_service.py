"""
Servicio de Tipos de Evento.
Colección: tipos_evento en kofan_reservas.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
from bson import ObjectId
from db.client import db

collection = db.tipos_evento


# --- Helpers ---

def _to_oid(value: str) -> Optional[ObjectId]:
    """Convierte string a ObjectId. None si es inválido."""
    try:
        return ObjectId(value)
    except Exception:
        return None


def _serialize(doc: dict) -> dict[str, Any]:
    return {
        "id": str(doc["_id"]),
        "nombre_evento": doc["nombre_evento"],
        "descripcion": doc.get("descripcion"),
        "precio_base": float(doc["precio_base"]),
        "created_at": doc.get("created_at"),
    }


# --- Consultas ---

def get_all_tipos_evento() -> list[dict[str, Any]]:
    """Lista todos los tipos de evento."""
    return [_serialize(t) for t in collection.find()]


def get_tipo_evento_by_id(tipo_evento_id: str) -> Optional[dict[str, Any]]:
    """Obtiene tipo de evento por ID."""
    oid = _to_oid(tipo_evento_id)
    if not oid:
        return None
    doc = collection.find_one({"_id": oid})
    return _serialize(doc) if doc else None


# --- CRUD ---

def create_tipo_evento(data: dict) -> dict[str, Any]:
    """Inserta tipo_evento con created_at en UTC."""
    doc = dict(data)
    doc.setdefault("activo", True)
    doc.setdefault("created_at", datetime.now(timezone.utc))

    result = collection.insert_one(doc)
    return get_tipo_evento_by_id(str(result.inserted_id))  # type: ignore


def update_tipo_evento(tipo_evento_id: str, data: dict) -> Optional[dict[str, Any]]:
    """Actualiza tipo_evento. None si no existe."""
    oid = _to_oid(tipo_evento_id)
    if not oid:
        return None

    result = collection.update_one({"_id": oid}, {"$set": data})
    if result.matched_count == 0:
        return None

    return get_tipo_evento_by_id(tipo_evento_id)


def delete_tipo_evento(tipo_evento_id: str) -> bool:
    """Elimina tipo_evento."""
    oid = _to_oid(tipo_evento_id)
    if not oid:
        return False

    result = collection.delete_one({"_id": oid})

    return result.deleted_count > 0


# ==========================
# Seed de datos iniciales
# ==========================

def seed_tipos_evento():
    """
    Inserta tipos de evento básicos si no existen.
    Esto se ejecuta al iniciar el servidor.
    """

    eventos = [
        {
            "nombre_evento": "Boda",
            "descripcion": "Evento matrimonial",
            "precio_base": 800000
        },
        {
            "nombre_evento": "Reunion",
            "descripcion": "Reunión empresarial o social",
            "precio_base": 300000
        },
        {
            "nombre_evento": "Reunion Familiar",
            "descripcion": "Encuentro familiar",
            "precio_base": 400000
        },
    ]

    for evento in eventos:
        existe = collection.find_one({"nombre_evento": evento["nombre_evento"]})

        if not existe:
            evento["created_at"] = datetime.now(timezone.utc)
            collection.insert_one(evento)