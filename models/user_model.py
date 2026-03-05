from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    names: Optional[str] = None
    surnames: Optional[str] = None
    document_type: Optional[str] = None
    document_number: Optional[str] = None 
    email: str    
    role: str = "user"
    disabled: bool = False

class UserPassword(UserBase):
    password: str   

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"