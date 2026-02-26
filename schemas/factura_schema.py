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
    PAGADA = "PAGADA"
    PENDIENTE = "PENDIENTE"
    VENCIDA = "VENCIDA"


class EstadoPago(str, Enum):
    PAGADO = "PAGADO"
    PENDIENTE = "PENDIENTE"
    VENCIDO = "VENCIDO"
    REEMBOLSO = "REEMBOLSO"


class MetodoPago(str, Enum):
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
    pass


class PagoResponse(PagoBase):
    id: str


class PagoEstadoUpdate(BaseModel):
    estado: EstadoPago


class FacturaBase(BaseModel):
    reserva_id: str = Field(..., min_length=1, description="ObjectId de reserva como string")
    numero_factura: str = Field(..., min_length=1)
    fecha_emision: Optional[datetime] = None
    valor_total: float = Field(..., gt=0)
    estado: EstadoFactura = EstadoFactura.PENDIENTE


class FacturaCreate(FacturaBase):
    pass


class FacturaUpdate(BaseModel):
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
