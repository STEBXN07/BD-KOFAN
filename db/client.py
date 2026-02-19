from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"

cliente = MongoClient(MONGO_URL)

db = cliente["ecohotel_kofan_db"]