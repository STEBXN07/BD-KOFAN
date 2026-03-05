"""
Schemas Pydantic para Tipo Evento.

Basado en DB_architecture.json:
- tipo_evento: nombre_evento, precio_base, created_at
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class NombreEvento(str, Enum):
    boda = "Boda"
    reunion = "Reunion"
    reunion_familiar = "Reunion Familiar"


class TipoEventoCreate(BaseModel):
    nombre_evento: NombreEvento
    descripcion: Optional[str] = None
    precio_base: float = Field(
        ...,
        gt=0
    )


class TipoEventoUpdate(BaseModel):
    nombre_evento: Optional[NombreEvento] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = Field(None, gt=0)