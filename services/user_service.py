from db.client import db
from models.user_model import UserBase, UserCreate, UserInDB, UserOut
from bson import ObjectId
from bson.errors import InvalidId
from core.security import hash_password
from schemas.user_schema import user_schema, users_schema

collection = db.users

def get_user_by_email(email: str):
    """Mantiene tu lógica: busca en la DB y lo convierte a UserBase usando tu schema"""
    user = collection.find_one({"email": email})
    if not user:
        return None
    return UserBase(**user_schema(user))

def get_user_db(email: str):
    """
    Función CLAVE para el Login:
    Mantiene tu lógica de búsqueda, pero mapea el password 
    directamente del diccionario para que UserInDB no lo pierda.
    """
    user = collection.find_one({"email": email})
    if not user:
        return None

    return UserInDB(
        names=user.get("names"),
        surnames=user.get("surnames"),
        document_type=user.get("document_type"),
        document_number=user.get("document_number"),
        email=user["email"],
        role=user.get("role", "user"),
        disabled=user.get("disabled", False),
        password=user["password"] # ← Aquí recuperamos el hash para el login
    )

def get_user_by_document(document: str):
    user = collection.find_one({"document_number": document})
    if not user:
        return None
    return UserBase(**user_schema(user))

def get_users(page: int, limit: int):
    skip = (page - 1) * limit
    users = list(collection.find().skip(skip).limit(limit))
    
    for user in users:
        user["_id"] = str(user["_id"])

    return users

def get_user_by_id(user_id: str):
    try:
        objeto_id = ObjectId(user_id)
    except Exception:
        return None

    user = collection.find_one({"_id": objeto_id})
    if user:
        return user_schema(user)
    return None

def create_user(user: dict):
    """Mantiene tu lógica de inserción y retorno con schema"""
    result = collection.insert_one(user)
    new_user = collection.find_one({"_id": result.inserted_id})
    return user_schema(new_user)

def update_user(data: dict):
    if "password" in data:
        data["password"] = hash_password(data["password"])

    try:
        object_id = ObjectId(data["id"])
    except InvalidId:
        return None

    user_dict = dict(data)
    del user_dict["id"] 

    result = collection.find_one_and_replace({"_id": object_id}, user_dict, return_document=True)
    if not result:
        return None
    
    return user_schema(result)

def delete_user(user_id: str):
    return collection.delete_one({"_id": ObjectId(user_id)})