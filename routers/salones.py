from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta # <--- ESTA ES LA +LÍNEA QUE TE FALTA
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

@router.post("/reservar")
async def crear_reserva(reserva: Reserva):
    # 1. Verificar si ya hay una reserva para ese salón en esa fecha
    existe = db.reservas.find_one({
        "salon_id": reserva.salon_id,
        "fecha_inicio": reserva.fecha_inicio
    })
    
    if existe:
        raise HTTPException(status_code=400, detail="Esta fecha ya está ocupada para este salón.")

    nueva_reserva = dict(reserva)
    if "id" in nueva_reserva: del nueva_reserva["id"]
    
    id = db.reservas.insert_one(nueva_reserva).inserted_id
    return {"mensaje": "Fecha reservada con éxito", "id": str(id)}

@router.get("/ocupacion/{salon_id}")
async def obtener_ocupacion(salon_id: str):
    # Buscamos solo reservas que NO estén canceladas o expiradas
    reservas = db.reservas.find({
        "salon_id": salon_id,
        "estado": {"$ne": "expirada"} # Solo trae las pendientes o confirmadas
    })
    
    lista = []
    for r in reservas:
        # Si está confirmada la ponemos verde, si está pendiente (menos de 24h) roja
        color_evento = "green" if r.get("estado") == "confirmado" else "red"
        
        lista.append({
            "id": str(r["_id"]),
            "title": r["nombre_evento"],
            "start": r["fecha_inicio"],
            "end": r["fecha_fin"],
            "color": color_evento 
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
    
# Lógica sugerida para el servicio de facturas
async def limpiar_reservas_expiradas():
    ahora = datetime.utcnow()
    limite = ahora - timedelta(hours=24)
    
    # Buscamos reservas 'pendientes' creadas hace más de 24h
    resultado = await db.reservas.update_many(
        {"estado": "pendiente", "fecha_creacion": {"$lt": limite}},
        {"$set": {"estado": "expirada"}}
    )
    return resultado.modified_count