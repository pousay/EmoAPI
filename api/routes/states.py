from fastapi import APIRouter, Depends
from typing import Set
from _types import States
from core.dependencies import require_auth

router = APIRouter(tags=["STATES"], dependencies=[Depends(require_auth)])


@router.get("/all_states", response_model=Set[str])
async def show_state():
    return States.get_all_states()
