"""
Schemas Pydantic para Tipo Evento.

Basado en DB_architecture.json (colección tipo_evento):
  _id, nombre_evento, descripcion, precio_base, activo, created_at, updated_at.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TipoEventoCreate(BaseModel):
    nombre_evento: str = Field(..., min_length=1, max_length=100, description="Nombre del tipo de evento")
    descripcion: Optional[str] = Field(None, max_length=255)
    precio_base: float = Field(..., gt=0)


class TipoEventoUpdate(BaseModel):
    nombre_evento: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    precio_base: Optional[float] = Field(None, gt=0)