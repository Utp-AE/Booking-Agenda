# backend/app/schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


# ==== TOKENS ====

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ==== USUARIOS ====

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    # lo usaremos solo desde Swagger / admin, en el frontend siempre será false
    is_admin: bool = False


class UserRead(UserBase):
    id: int
    is_admin: bool

    # Pydantic v2: para que acepte objetos ORM (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)


# ==== RESERVAS ====

class ReservationBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime


class ReservationCreate(ReservationBase):
    # si el admin quiere crear para otro usuario
    owner_id: Optional[int] = None


class ReservationRead(ReservationBase):
    id: int
    owner_id: int
    # 👇 Aquí viene el usuario completo, con full_name, email, etc.
    owner: UserRead

    model_config = ConfigDict(from_attributes=True)