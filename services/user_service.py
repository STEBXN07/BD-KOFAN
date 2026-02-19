from db.client import db
from core.security import hash_password

def create_user(user_data):
    user_dict = user_data.dict()
    user_dict["password"] = hash_password(user_dict["password"])
    db.users.insert_one(user_dict)
    
def create_user(user):
    user_dict = user.dict()
    user_dict["hashed_password"] = hash_password(user_dict.pop("password"))
    db.users.insert_one(user_dict)
    
def get_user_by_username(username: str):
    return db.users.find_one({"username": username})

def get_user_by_id(id: str):
    return db.users.find_one({"id": id})
