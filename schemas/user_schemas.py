from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str = "user"
    disabled: bool = False
    
class UserCreate(UserBase):
    password: str
    
class UserLogin(BaseModel):
    username: str
    password: str
    
class tojen(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
