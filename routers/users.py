from fastapi import APIRouter, Depends
from dependencies.auth import require_admin, get_current_user

router = APIRouter(
    prefix="/users", 
    tags=["users"],
    dependencies=[Depends(get_current_user)]
    )

@router.get("/me")
async def read_me(user=Depends(get_current_user)):
    return user

@router.get("/admin")
async def admin_only(user=Depends(require_admin)):
    return {"message": "Welcome, admin!"}