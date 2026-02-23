"""
Schemas Pydantic para la entidad Cliente.

Define los modelos de validación y serialización para creación,
actualización y respuesta de clientes en la API.

Alineado con la colección "clientes" del mongodb_schema.json:
- nombre_completo, numero_documento (requeridos)
- tipo_documento: solo CC, CE, PASAPORTE, TI, RC, NIT
- email (único; la unicidad se valida en el router)
- telefono, pais, ciudad, fecha_nacimiento opcionales
- created_at, updated_at gestionados en el servicio
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Valores permitidos según mongodb_schema.json (clientes.tipo_documento)
# -----------------------------------------------------------------------------


class TipoDocumento(str, Enum):
    """Tipos de documento permitidos para clientes (CC, CE, PASAPORTE, TI, RC, NIT)."""

    CC = "CC"
    CE = "CE"
    PASAPORTE = "PASAPORTE"
    TI = "TI"
    RC = "RC"
    NIT = "NIT"


# -----------------------------------------------------------------------------
# Modelos base y de entrada
# -----------------------------------------------------------------------------


class ClienteBase(BaseModel):
    """
    Campos comunes de un cliente (lectura y creación).

    Cumple con mongodb_schema.json: nombre_completo y numero_documento
    requeridos; tipo_documento restringido a los valores del schema.
    """

    nombre_completo: str = Field(..., min_length=1, description="Nombre completo (requerido)")
    tipo_documento: TipoDocumento = Field(..., description="CC, CE, PASAPORTE, TI, RC, NIT")
    numero_documento: str = Field(..., min_length=1, description="Número de documento (requerido)")
    telefono: Optional[str] = None
    email: str = Field(..., min_length=1, description="Email único del cliente")
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None


class ClienteCreate(ClienteBase):
    """Payload para crear un nuevo cliente (email debe ser único en la BD)."""

    pass


class ClienteUpdate(BaseModel):
    """Payload para actualización parcial de un cliente (todos opcionales)."""

    nombre_completo: Optional[str] = Field(None, min_length=1)
    tipo_documento: Optional[TipoDocumento] = None
    numero_documento: Optional[str] = Field(None, min_length=1)
    telefono: Optional[str] = None
    email: Optional[str] = Field(None, min_length=1)
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None


# -----------------------------------------------------------------------------
# Modelos de respuesta
# -----------------------------------------------------------------------------


class ClienteResponse(ClienteBase):
    """
    Cliente tal como se devuelve en las respuestas de la API.

    Incluye id (ObjectId como string), created_at y updated_at
    según mongodb_schema.json.
    """

    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
