"""
Schemas Pydantic para Cotizaciones.

Basado en Docs/DB_architecture.json:
- cotizaciones: cliente_id, usuario_cotizador_id, fecha_inicio, fecha_finalizacion,
  estado, total, observaciones, created_at
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EstadoCotizacion(str, Enum):
    """Estados de la cotización según DB_architecture.json."""
    BORRADOR = "BORRADOR"
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"


class CotizacionCreate(BaseModel):
    """Schema para crear una nueva cotización."""
    cliente_id: str = Field(..., min_length=1, description="ObjectId del cliente")
    usuario_cotizador_id: str = Field(..., min_length=1, description="ObjectId del usuario que cotiza")
    fecha_inicio: datetime
    fecha_finalizacion: datetime
    estado: EstadoCotizacion = EstadoCotizacion.BORRADOR
    total: float = Field(..., gt=0)
    observaciones: Optional[str] = None


class CotizacionUpdate(BaseModel):
    """Actualización parcial; todos los campos opcionales."""
    cliente_id: Optional[str] = Field(None, min_length=1)
    usuario_cotizador_id: Optional[str] = Field(None, min_length=1)
    fecha_inicio: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    estado: Optional[EstadoCotizacion] = None
    total: Optional[float] = Field(None, gt=0)
    observaciones: Optional[str] = None
