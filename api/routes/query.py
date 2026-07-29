from fastapi import APIRouter, Query, Request
from core.model import Predict
from schema import EmoResponse
from core.ratelimiter import limiter
from core.config import config

router = APIRouter(tags=["EMO"])


@router.get("/text", response_model=EmoResponse)
@limiter.limit(limiter._default_limits[0])
async def show_state(request: Request, text: str = Query(...)):
    if text.strip() == "":
        raise ValueError

    state = Predict.predict(text)
    return EmoResponse(text=text, state=state)
