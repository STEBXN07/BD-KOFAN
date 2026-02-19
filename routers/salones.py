from fastapi import APIRouter, HTTPException
from db.client import db
from schemas.salon_schema import Salon, Reserva
from bson import ObjectId

router = APIRouter(prefix="/eventos", tags=["eventos"])

# --- GESTIÓN DE SALONES ---

# 1. Crear un Salón nuevo (Para que tengas Salón 1 y Salón 2)
@router.post("/crear-salon")
async def crear_salon(salon: Salon):
    nuevo_salon = dict(salon)
    del nuevo_salon["id"]
    id = db.salones.insert_one(nuevo_salon).inserted_id
    return {"mensaje": "Salón creado", "id": str(id)}

# 2. Ver todos los salones (Para el menú desplegable del Frontend)
@router.get("/listar-salones")
async def listar_salones():
    salones = []
    for s in db.salones.find():
        s["id"] = str(s["_id"])
        del s["_id"]
        salones.append(s)
    return salones

# --- GESTIÓN DE RESERVAS (CALENDARIO) ---

# 3. Guardar una Reserva (Bloquear fecha)
@router.post("/reservar")
async def crear_reserva(reserva: Reserva):
    nueva_reserva = dict(reserva)
    del nueva_reserva["id"]
    
    # Aquí podrías validar si ya existe fecha (opcional por ahora)
    id = db.reservas.insert_one(nueva_reserva).inserted_id
    return {"mensaje": "Fecha reservada con éxito", "id": str(id)}

# 4. 🔥 EL ENDPOINT DEL CALENDARIO 🔥
# Este es el que tu Frontend llama para saber qué pintar de rojo
@router.get("/ocupacion/{salon_id}")
async def obtener_ocupacion(salon_id: str):
    # Busca solo las reservas de ESE salón específico
    reservas = db.reservas.find({"salon_id": salon_id})
    
    lista = []
    for r in reservas:
        lista.append({
            "title": r["nombre_evento"], # "title" suele usarlo FullCalendar
            "start": r["fecha_inicio"],
            "end": r["fecha_fin"],
            "color": "red" # Para que salga rojo en el calendario
        })
    return lista

from bson import ObjectId # <--- OJO: Asegúrese de tener esto arriba del todo

# 5. ELIMINAR RESERVA (Versión para IDs largos de letras)
@router.delete("/reservas/{id_reserva}")
async def borrar_reserva(id_reserva: str): # <--- CAMBIO 1: Ahora dice "str"
    try:
        # CAMBIO 2: Convertimos las letras a un ID de Mongo real
        resultado = db.reservas.delete_one({"_id": ObjectId(id_reserva)})
        
        if resultado.deleted_count == 1:
            return {"mensaje": "Reserva eliminada. 🗑️"}
        else:
            return {"error": "No encontré esa reserva (o el ID está mal copiado)."}
            
    except Exception as e:
        return {"error": "El ID que mandaste no tiene formato válido de Mongo."}