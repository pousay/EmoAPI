from fastapi import APIRouter
from schema import EmoResponse
from typing import Set
from _types import States

router = APIRouter()


@router.get("/all_states", response_model=Set[str])
async def show_state():
    return States.get_all_states()
