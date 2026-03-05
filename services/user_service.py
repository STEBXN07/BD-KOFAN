from db.client import db
from models.user_model import UserBase, UserPassword
from bson import ObjectId
from bson.errors import InvalidId
from core.security import hash_password
from schemas.user_schema import user_schema, users_schema


collection = db.users


def get_user_by_email(email: str):

    user = collection.find_one({"email": email})
    if not user:
        return None
    return UserBase(**user_schema(user))

def get_user_by_username(username: str):
    user = collection.find_one({"username": username})
    if not user:
        return None
    return user

def get_user_by_document(document: str):

    user = collection.find_one({"document": document})
    if not user:
        return None
    return UserBase(**user_schema(user))



def get_user_db(email: str):
    user = collection.find_one({"email": email})
    if not user:
        return None

    return UserPassword(
        names=user.get("names"),
        surnames=user.get("surnames"),
        document_type=user.get("document_type"),
        document_number=user.get("document_number"),
        email=user["email"],
        role=user.get("role", "user"),
        disabled=user.get("disabled", False),
        password=user["password"],  # ← AQUÍ está la clave
    )



#def get_all_users():
#    return users_schema(collection.find())    

def get_users(page: int, limit: int):

    skip = (page - 1) * limit
    users = list(collection.find().skip(skip).limit(limit))
    
    for user in users:
        user["_id"] = str(user["_id"])

    return users
    #return users_schema(users)


def get_user_by_id(user_id: str):
    try:
        objeto_id = ObjectId(user_id)
    except Exception:
        return None

    user = collection.find_one({"_id": objeto_id})
    if user:
        return user_schema(user)
    return None


def create_user(data: dict):
    data["password"] = hash_password(data["password"])
    id = collection.insert_one(data).inserted_id
    new_user = user_schema(collection.find_one({"_id": id}))
    return UserBase(**new_user)


def update_user(data: dict):
    if "password" in data:
        data["password"] = hash_password(data["password"])

    try:
        object_id = ObjectId(data["id"])
    except InvalidId:
        return None

    user_dict = dict(data)
    del user_dict["id"] 

    result = collection.find_one_and_replace({"_id": object_id}, user_dict)
    if not result:
        return None
    
    return UserBase(**get_user_by_id(data["id"]))



def delete_user(user_id: str):
    return collection.delete_one({"_id": ObjectId(user_id)})