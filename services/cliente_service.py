"""
Capa de servicio para la entidad Cliente.

Acceso a la colección `clientes` en MongoDB (PyMongo síncrono).
La forma del documento cumple con mongodb_schema.json (clientes):
_id, nombre_completo, tipo_documento, numero_documento, telefono, email,
pais, ciudad, fecha_nacimiento, created_at, updated_at.
La unicidad de email se valida en el router; se recomienda índice único en BD.
"""
from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId

from db.client import db

# -----------------------------------------------------------------------------
# Configuración — colección clientes (mongodb_schema.json)
# -----------------------------------------------------------------------------

collection = db.clientes


# -----------------------------------------------------------------------------
# Serialización (campos según mongodb_schema.json)
# -----------------------------------------------------------------------------


def _cliente_entity(cliente: dict) -> dict[str, Any]:
    """
    Serializa un documento de MongoDB a dict para la API.

    Convierte _id a string como 'id' y expone solo los campos
    definidos en mongodb_schema.json para clientes.

    Args:
        cliente: Documento raw de la colección clientes.

    Returns:
        Dict con id, campos del cliente y created_at/updated_at.
    """
    return {
        "id": str(cliente["_id"]),
        "nombre_completo": cliente["nombre_completo"],
        "tipo_documento": cliente["tipo_documento"],
        "numero_documento": cliente["numero_documento"],
        "telefono": cliente.get("telefono"),
        "email": cliente["email"],
        "pais": cliente.get("pais"),
        "ciudad": cliente.get("ciudad"),
        "fecha_nacimiento": cliente.get("fecha_nacimiento"),
        "created_at": cliente.get("created_at"),
        "updated_at": cliente.get("updated_at"),
    }


# -----------------------------------------------------------------------------
# Consultas
# -----------------------------------------------------------------------------


def get_all_clientes() -> list[dict[str, Any]]:
    """Devuelve todos los clientes de la colección, serializados."""
    return [_cliente_entity(c) for c in collection.find()]


def get_cliente_by_id(cliente_id: str) -> Optional[dict[str, Any]]:
    """
    Busca un cliente por su ObjectId.

    Args:
        cliente_id: String con el ObjectId del cliente.

    Returns:
        Cliente serializado o None si no existe o el id es inválido.
    """
    try:
        cliente = collection.find_one({"_id": ObjectId(cliente_id)})
    except Exception:
        return None
    if cliente:
        return _cliente_entity(cliente)
    return None


def get_cliente_by_email(email: str) -> Optional[dict[str, Any]]:
    """
    Busca un cliente por email (útil para validar unicidad).

    Returns:
        Cliente serializado o None si no existe.
    """
    cliente = collection.find_one({"email": email})
    if cliente:
        return _cliente_entity(cliente)
    return None


# -----------------------------------------------------------------------------
# Escritura
# -----------------------------------------------------------------------------


def create_cliente(data: dict) -> Optional[dict[str, Any]]:
    """
    Inserta un nuevo cliente y devuelve el documento creado.

    Añade created_at y updated_at en UTC antes de insertar.
    """
    now = datetime.now(timezone.utc)
    data["created_at"] = now
    data["updated_at"] = now
    result = collection.insert_one(data)
    return get_cliente_by_id(str(result.inserted_id))


def update_cliente(cliente_id: str, data: dict) -> Optional[dict[str, Any]]:
    """
    Actualiza un cliente por id. Actualiza updated_at.

    Returns:
        Cliente actualizado serializado o None si no existe o id inválido.
    """
    try:
        data["updated_at"] = datetime.now(timezone.utc)
        result = collection.update_one(
            {"_id": ObjectId(cliente_id)},
            {"$set": data},
        )
        if result.matched_count == 0:
            return None
        return get_cliente_by_id(cliente_id)
    except Exception:
        return None


def delete_cliente(cliente_id: str) -> bool:
    """
    Elimina un cliente por id.

    Returns:
        True si se eliminó un documento, False si no existía o id inválido.
    """
    try:
        result = collection.delete_one({"_id": ObjectId(cliente_id)})
        return result.deleted_count == 1
    except Exception:
        return False
