from fastapi import APIRouter, Query
from core.model import Predict
from schema import EmoResponse

router = APIRouter(tags=["EMO"])


@router.get("/text", response_model=EmoResponse)
async def show_state(text: str = Query(...)):
    if text.strip() == "":
        raise ValueError

    state = Predict.predict(text)
    return EmoResponse(text=text, state=state)
