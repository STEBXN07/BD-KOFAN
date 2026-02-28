from pydantic import BaseModel, ConfigDict
from typing import Optional

class Salon(BaseModel):
    nombre: str
    capacidad: int
    descripcion: str
    
    # Esto es para que en el Docs aparezca un ejemplo real
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "nombre": "Salón Kofán Principal",
            "capacidad": 50,
            "descripcion": "Salón amplio con vista al río"
        }
    })

class Reserva(BaseModel):
    salon_id: str
    nombre_evento: str
    fecha_inicio: str
    fecha_fin: str

    # AQUÍ ESTÁ LA MAGIA: Esto le devuelve las fechas al Docs
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "salon_id": "69a24d80b...",
            "nombre_evento": "Boda Real",
            "fecha_inicio": "2026-03-20T10:00:00",
            "fecha_fin": "2026-03-20T20:00:00"
        }
    })