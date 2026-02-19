from bson import ObjectId

def user_entity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "username": item["username"],
        "email": item["email"],
        "full_name": item["full_name"],
        "roles": item["roles"],
        "hashed_password": item["hashed_password"]
    }