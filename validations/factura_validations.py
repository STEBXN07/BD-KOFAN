from __future__ import annotations

from bson import ObjectId


def is_valid_object_id(value: str) -> bool:
    try:
        ObjectId(value)
        return True
    except Exception:
        return False


def require_valid_object_id(value: str, field_name: str) -> None:
    if not value or not is_valid_object_id(value):
        raise ValueError(f"{field_name} inválido")


def require_non_empty_update(payload: dict) -> None:
    if not payload:
        raise ValueError("No hay datos para actualizar")
