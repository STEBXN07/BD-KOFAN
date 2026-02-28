from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from schemas.salon_schema import Salon, Reserva
from bson import ObjectId
from pymongo import MongoClient

# --- CONEXIÓN UNIFICADA A KOFAN_RESERVAS ---
try:
    uri = "mongodb+srv://kofan_admin:Kofan2026@kofan-cluster.j9z4urw.mongodb.net/"
    client = MongoClient(uri)
    client.admin.command('ping')
    db = client["kofan_reservas"] 
    print("¡Conectado a kofan_reservas melo!")
except Exception as e:
    print(f"Error de conexión: {e}")

router = APIRouter(prefix="/eventos", tags=["eventos"])

# --- 1. GESTIÓN DE SALONES ---

@router.post("/crear-salon")
async def crear_salon(salon: Salon):
    if db.salones.find_one({"nombre": salon.nombre}):
        raise HTTPException(status_code=400, detail=f"El salón '{salon.nombre}' ya existe.")
    nuevo = salon.model_dump()
    res = db.salones.insert_one(nuevo)
    return {"mensaje": "Salón creado en kofan_reservas", "id": str(res.inserted_id)}

@router.get("/listar-salones")
async def listar_salones():
    salones = []
    for s in db.salones.find():
        s["id"] = str(s["_id"])
        del s["_id"]
        salones.append(s)
    return salones

@router.delete("/salones/{id_salon}")
async def borrar_salon(id_salon: str):
    try:
        res = db.salones.delete_one({"_id": ObjectId(id_salon)})
        if res.deleted_count == 1:
            return {"mensaje": "Salón eliminado correctamente. 🗑️"}
        return {"error": "No se encontró el salón."}
    except:
        return {"error": "ID de salón no válido."}

# --- 2. GESTIÓN DE RESERVAS ---

@router.post("/reservar")
async def crear_reserva(reserva: Reserva):
    existe = db.reservas.find_one({
        "salon_id": reserva.salon_id,
        "fecha_inicio": reserva.fecha_inicio,
        "estado": {"$ne": "expirada"}
    })
    if existe:
        raise HTTPException(status_code=400, detail="Esa fecha ya está ocupada.")

    nueva = reserva.model_dump()
    nueva["fecha_creacion"] = datetime.utcnow()
    nueva["estado"] = "pendiente" # Empieza en ROJO
    
    res = db.reservas.insert_one(nueva)
    return {"mensaje": "Reserva creada. Tienes 24h para pagar.", "id": str(res.inserted_id)}

@router.put("/reservas/{id_reserva}")
async def actualizar_reserva(id_reserva: str, reserva_actualizada: Reserva):
    try:
        datos = reserva_actualizada.model_dump()
        res = db.reservas.update_one({"_id": ObjectId(id_reserva)}, {"$set": datos})
        if res.modified_count == 1:
            return {"mensaje": "Reserva actualizada con éxito. 📝"}
        return {"error": "No hubo cambios."}
    except:
        return {"error": "Error al actualizar."}

@router.patch("/reservas/{id_reserva}/confirmar")
async def confirmar_pago(id_reserva: str):
    try:
        res = db.reservas.update_one(
            {"_id": ObjectId(id_reserva)},
            {"$set": {"estado": "confirmado"}} # Pasa a VERDE
        )
        if res.modified_count == 1:
            return {"mensaje": "Pago confirmado. Reserva activa."}
        return {"error": "No se pudo actualizar."}
    except:
        return {"error": "ID no válido."}

@router.get("/ocupacion/{salon_id}")
async def obtener_ocupacion(salon_id: str):
    # Limpieza automática de 24 horas
    limite = datetime.utcnow() - timedelta(hours=24)
    db.reservas.update_many(
        {"estado": "pendiente", "fecha_creacion": {"$lt": limite}},
        {"$set": {"estado": "expirada"}}
    )

    reservas = db.reservas.find({
        "salon_id": salon_id,
        "estado": {"$ne": "expirada"}
    })
    
    lista = []
    for r in reservas:
        color = "green" if r.get("estado") == "confirmado" else "red"
        lista.append({
            "id": str(r["_id"]),
            "title": f"{r.get('nombre_evento')} - {r.get('estado')}",
            "start": r["fecha_inicio"],
            "end": r["fecha_fin"],
            "color": color 
        })
    return lista