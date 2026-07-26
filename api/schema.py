from pydantic import BaseModel
from typing import Optional


class Emo(BaseModel):
    text: str
    state: Optional[str]


class EmoResponse(Emo):
    state: str
