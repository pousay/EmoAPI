from fastapi import APIRouter, Query
from core.model import predict

router = APIRouter(prefix="/emo")


@router.get("/", response_model=str)
async def show_state(text: str = Query(...)):
    return predict(str(text))
