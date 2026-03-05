from datetime import datetime

def tipo_evento_entity(tipo) -> dict:
    return {
        "id": str(tipo["_id"]),
        "nombre_evento": tipo["nombre_evento"],
        "descripcion": tipo.get("descripcion"),
        "precio_base": tipo["precio_base"],
        "created_at": tipo.get("created_at")
    }

def tipos_evento_entity(tipos) -> list:
    return [tipo_evento_entity(tipo) for tipo in tipos]