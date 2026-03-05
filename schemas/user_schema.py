from bson import ObjectId

def user_schema(user) -> dict:
    return {
        "id": str(user["_id"]),
        "names": user.get("names"),
        "surnames": user.get("surnames"),
        "document_type": user.get("document_type"),
        "document_number": user.get("document_number"),
        "email": user["email"],  # este sí obligatorio
        "role": user.get("role", "user"),
        "disabled": user.get("disabled", False),
    }


def users_schema(users) -> list:
    return [user_schema(user) for user in users] 