"""
from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"

cliente = MongoClient(MONGO_URL)

db = cliente["ecohotel_kofan_db"]

"""

#
from pymongo import MongoClient

# Base de datos: kofan_reservas (misma que ves en MongoDB Atlas / IDE)
MONGO_URL = "mongodb+srv://kofan_admin:Kofan2026@kofan-cluster.j9z4urw.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "kofan_reservas"

cliente = MongoClient(MONGO_URL)
db = cliente[DATABASE_NAME]

print("Conectado a MongoDB Atlas correctamente")