from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Estructura de un Salón (Ej: Salón Principal)
class Salon(BaseModel):
    id: Optional[str] = None
    nombre: str         # Ej: "Salón Dorado"
    capacidad: int      # Ej: 200
    descripcion: str    # Ej: "Con aire acondicionado"

# Estructura de una Reserva (Ej: Matrimonio el Sábado)
class Reserva(BaseModel):
    id: Optional[str] = None
    salon_id: str       # <--- IMPORTANTE: Dice en cuál salón es
    fecha_inicio: datetime
    fecha_fin: datetime
    nombre_evento: str  # Ej: "Boda de Brayan"
    cliente_nombre: str