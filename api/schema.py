from pydantic import BaseModel
from typing import Optional
from ._types import States


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


#
# EMO
#


class Emo(BaseModel):
    text: str
    state: Optional[States]


class EmoResponse(Emo):
    state: States
