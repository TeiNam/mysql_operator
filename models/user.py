from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_id: int
    permission: int
    is_use: str
    is_auth: str
    email_token: Optional[str] = None
    create_at: Optional[str] = None
    update_at: Optional[str] = None

    class Config:
        orm_mode = True
