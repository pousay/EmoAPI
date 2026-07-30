from fastapi import APIRouter, Depends, Query, Request, HTTPException
from core.model import Predict
from core.dependencies import require_auth
from schema import EmoResponse
from core.ratelimiter import limiter

router = APIRouter(tags=["EMO"], dependencies=[Depends(require_auth)])


@router.get("/text", response_model=EmoResponse)
@limiter.limit(limiter._default_limits[0])
async def show_state(request: Request, text: str = Query(...)):
    if text.strip() == "":
        raise HTTPException(status_code=422, detail="text must not be empty")

    state = Predict.predict(text)
    return EmoResponse(text=text, state=state)
