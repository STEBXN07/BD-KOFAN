"""
Schemas Pydantic para Facturas y Pagos.

Basado en Docs/DB_architecture.json:
- facturas: reserva_id, numero_factura (único), fecha_emision, valor_total, valor_pagado, estado, pagos[], created_at
- pagos[]: _id, monto, fecha_pago, metodo_pago, estado
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class EstadoFactura(str, Enum):
    """Estados de la factura según DB_architecture.json."""
    PAGADA = "PAGADA"
    PENDIENTE = "PENDIENTE"
    VENCIDA = "VENCIDA"


class EstadoPago(str, Enum):
    """Estados de cada pago (subdocumento)."""
    PAGADO = "PAGADO"
    PENDIENTE = "PENDIENTE"
    VENCIDO = "VENCIDO"
    REEMBOLSO = "REEMBOLSO"


class MetodoPago(str, Enum):
    """Métodos de pago permitidos (DB_architecture.json)."""
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    TARJETA = "TARJETA"
    NEQUI = "NEQUI"
    DAVIPLATA = "DAVIPLATA"


class PagoBase(BaseModel):
    monto: float = Field(..., gt=0)
    fecha_pago: datetime = Field(..., description="Fecha/hora del pago")
    metodo_pago: MetodoPago
    estado: EstadoPago = EstadoPago.PENDIENTE


class PagoCreate(PagoBase):
    """Schema para crear un pago (se embebe en factura)."""
    pass


class PagoResponse(PagoBase):
    """Pago serializado para respuesta (incluye id)."""
    id: str


class PagoEstadoUpdate(BaseModel):
    """Solo el campo estado para actualizar un pago."""
    estado: EstadoPago


class FacturaBase(BaseModel):
    reserva_id: str = Field(..., min_length=1, description="ObjectId de reserva como string")
    numero_factura: str = Field(..., min_length=1)
    fecha_emision: Optional[datetime] = None
    valor_total: float = Field(..., gt=0)
    estado: EstadoFactura = EstadoFactura.PENDIENTE


class FacturaCreate(FacturaBase):
    """Schema para crear una nueva factura."""
    pass


class FacturaUpdate(BaseModel):
    """Actualización parcial; todos los campos opcionales."""
    reserva_id: Optional[str] = Field(None, min_length=1)
    numero_factura: Optional[str] = Field(None, min_length=1)
    fecha_emision: Optional[datetime] = None
    valor_total: Optional[float] = Field(None, gt=0)
    estado: Optional[EstadoFactura] = None


class FacturaResponse(BaseModel):
    id: str
    reserva_id: str
    numero_factura: str
    fecha_emision: Optional[datetime] = None
    valor_total: float
    valor_pagado: float
    estado: EstadoFactura
    pagos: List[PagoResponse] = Field(default_factory=list)
    created_at: Optional[datetime] = None
