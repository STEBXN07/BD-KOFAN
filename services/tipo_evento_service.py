"""
Servicio de Tipos de Evento.
Colección: tipo_evento en kofan_reservas.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
from bson import ObjectId
from pymongo import ASCENDING
from db.client import db

collection = db.tipo_evento

DEFAULT_TIPOS_EVENTO: list[dict[str, Any]] = [
    {
        "nombre_evento": "Bodas",
        "descripcion": "Celebraciones matrimoniales",
        "precio_base": 800000.0,
    },
    {
        "nombre_evento": "Reuniones",
        "descripcion": "Reuniones empresariales o sociales",
        "precio_base": 300000.0,
    },
    {
        "nombre_evento": "Reuniones Familiares",
        "descripcion": "Encuentros familiares",
        "precio_base": 400000.0,
    },
]


# --- Helpers ---

def _to_oid(value: str) -> Optional[ObjectId]:
    """Convierte string a ObjectId. None si es inválido."""
    try:
        return ObjectId(value)
    except Exception:
        return None


def _normalize_nombre(nombre: str) -> str:
    return nombre.strip().lower()


def _serialize(doc: dict) -> dict[str, Any]:
    return {
        "id": str(doc["_id"]),
        "nombre_evento": doc["nombre_evento"],
        "descripcion": doc.get("descripcion"),
        "precio_base": float(doc["precio_base"]),
        "activo": doc.get("activo", True),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }


# --- Consultas ---

def get_all_tipos_evento() -> list[dict[str, Any]]:
    """Lista todos los tipos de evento activos."""
    return [_serialize(t) for t in collection.find({"activo": True}).sort("nombre_evento", 1)]


def get_tipo_evento_by_id(tipo_evento_id: str) -> Optional[dict[str, Any]]:
    """Obtiene tipo de evento por ID."""
    oid = _to_oid(tipo_evento_id)
    if not oid:
        return None
    doc = collection.find_one({"_id": oid, "activo": True})
    return _serialize(doc) if doc else None


# --- CRUD ---

def create_tipo_evento(data: dict) -> dict[str, Any]:
    """Inserta tipo_evento con created_at en UTC."""
    nombre_evento = data["nombre_evento"]
    nombre_key = _normalize_nombre(nombre_evento)
    if collection.find_one({"nombre_evento_key": nombre_key, "activo": True}):
        raise ValueError("Ya existe un tipo de evento con ese nombre")

    now = datetime.now(timezone.utc)
    doc = dict(data)
    doc["nombre_evento_key"] = nombre_key
    doc["activo"] = True
    doc["created_at"] = now
    doc["updated_at"] = now

    result = collection.insert_one(doc)
    return get_tipo_evento_by_id(str(result.inserted_id))  # type: ignore


def update_tipo_evento(tipo_evento_id: str, data: dict) -> Optional[dict[str, Any]]:
    """Actualiza tipo_evento. None si no existe."""
    oid = _to_oid(tipo_evento_id)
    if not oid:
        return None

    updates = dict(data)
    if "nombre_evento" in updates:
        nombre_key = _normalize_nombre(updates["nombre_evento"])
        existing = collection.find_one(
            {
                "_id": {"$ne": oid},
                "nombre_evento_key": nombre_key,
                "activo": True,
            }
        )
        if existing:
            raise ValueError("Ya existe un tipo de evento con ese nombre")
        updates["nombre_evento_key"] = nombre_key

    updates["updated_at"] = datetime.now(timezone.utc)

    result = collection.update_one({"_id": oid}, {"$set": updates})
    if result.matched_count == 0:
        return None

    return get_tipo_evento_by_id(tipo_evento_id)


def delete_tipo_evento(tipo_evento_id: str) -> bool:
    """Realiza borrado lógico de tipo_evento."""
    oid = _to_oid(tipo_evento_id)
    if not oid:
        return False

    result = collection.update_one(
        {"_id": oid, "activo": True},
        {"$set": {"activo": False, "updated_at": datetime.now(timezone.utc)}},
    )

    return result.modified_count > 0


# ==========================
# Seed de datos iniciales
# ==========================

def seed_tipos_evento():
    """
    Inserta tipos de evento básicos si no existen (idempotente).
    """
    collection.create_index([("nombre_evento_key", ASCENDING)], unique=True)
    now = datetime.now(timezone.utc)
    for evento in DEFAULT_TIPOS_EVENTO:
        nombre_key = _normalize_nombre(evento["nombre_evento"])
        existing = collection.find_one({"nombre_evento_key": nombre_key})
        if existing:
            if not existing.get("activo", True):
                collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"activo": True, "updated_at": now}},
                )
            continue

        collection.insert_one(
            {
                **evento,
                "nombre_evento_key": nombre_key,
                "activo": True,
                "created_at": now,
                "updated_at": now,
            }
        )