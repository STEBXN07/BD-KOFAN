from bson import ObjectId

from db.client import db
from core.security import hash_password

collection = db.users


def create_user(user_data):
    """Crea un usuario; guarda la contraseña hasheada en 'password' (compatible con login)."""
    user_dict = user_data.dict() if hasattr(user_data, "dict") else dict(user_data)
    plain = user_dict.pop("password", None) or user_dict.pop("hashed_password", "")
    user_dict["password"] = hash_password(plain)
    db.users.insert_one(user_dict)


def get_user_by_username(username: str):
    """Devuelve el documento del usuario (incluye password para verificación en auth)."""
    return db.users.find_one({"username": username})


def get_user_by_id(user_id: str):
    """Busca usuario por _id (ObjectId) o por campo 'id'."""
    try:
        doc = db.users.find_one({"_id": ObjectId(user_id)})
        if doc:
            return doc
    except Exception:
        pass
    return db.users.find_one({"id": user_id})
